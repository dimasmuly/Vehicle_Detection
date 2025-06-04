import cv2
import numpy as np
import logging
import time
import subprocess
import threading
from typing import Dict
from config import Config
from utils import process_detections, draw_detections
from openvino.runtime import Core
import os
import signal
import sys

logger = logging.getLogger(__name__)

class VehicleCounter:
    def __init__(self, config: Config):
        self.config = config
        self.vehicle_count = 0
        self.total_vehicles = 0
        self.frame_count = 0
        self.ffmpeg_process = None
        self.streaming_enabled = True
        
        # Initialize OpenVINO models
        self.setup_openvino_models()
        
        # Initialize video capture
        self.cap = None
        self.setup_video_capture()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.streaming_enabled = False
        self.cleanup()
        sys.exit(0)
    
    def setup_openvino_models(self):
        """Setup OpenVINO models for local inference"""
        self.core = Core()
        
        # Load vehicle detection model
        detection_model_path = os.path.join(
            self.config.MODEL_PATH, 
            'vehicle-detection-0202/1/vehicle-detection-0202.xml'
        )
        
        if os.path.exists(detection_model_path):
            self.detection_model = self.core.read_model(detection_model_path)
            self.compiled_detection_model = self.core.compile_model(
                self.detection_model, "CPU"
            )
            
            # Get input and output info
            self.input_key = list(self.compiled_detection_model.inputs)[0]
            self.output_key = list(self.compiled_detection_model.outputs)[0]
            
            # Get input shape
            self.input_shape = self.input_key.shape
            logger.info(f"Model input shape: {self.input_shape}")
            logger.info(f"Vehicle detection model loaded: {detection_model_path}")
        else:
            raise FileNotFoundError(f"Detection model not found: {detection_model_path}")
    
    def setup_video_capture(self):
        """Setup video capture with infinite looping"""
        self.cap = cv2.VideoCapture(self.config.INPUT_VIDEO)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video file: {self.config.INPUT_VIDEO}")
        
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        logger.info(f"Video loaded: {self.total_frames} frames at {self.fps} FPS")
    
    def wait_for_mediamtx(self, max_retries=30, delay=2):
        """Wait for MediaMTX to be ready"""
        import requests
        
        mediamtx_api = "http://mediamtx:9997/v3/paths/list"
        
        for attempt in range(max_retries):
            try:
                response = requests.get(mediamtx_api, timeout=5)
                if response.status_code == 200:
                    logger.info("MediaMTX is ready!")
                    return True
            except Exception as e:
                logger.info(f"Waiting for MediaMTX... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
        
        logger.warning("MediaMTX not ready after maximum retries, proceeding anyway...")
        return False
    
    def setup_streaming(self):
        """Setup FFmpeg streaming to MediaMTX with retry logic"""
        if not self.streaming_enabled:
            return False
            
        # Wait for MediaMTX to be ready
        self.wait_for_mediamtx()
        
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output files
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{self.config.FRAME_WIDTH}x{self.config.FRAME_HEIGHT}',
            '-r', str(self.fps),
            '-i', '-',  # Input from stdin
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-g', str(self.fps),  # Keyframe interval
            '-sc_threshold', '0',  # Disable scene change detection
            '-f', 'flv',
            self.config.MEDIAMTX_URL
        ]
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                self.ffmpeg_process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=0
                )
                logger.info(f"FFmpeg streaming started to {self.config.MEDIAMTX_URL} (attempt {attempt + 1})")
                return True
            except Exception as e:
                logger.error(f"Failed to start FFmpeg (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    logger.error("Failed to start streaming after all retries")
                    self.ffmpeg_process = None
                    return False
        
        return False
    
    def predict_vehicles(self, frame: np.ndarray) -> Dict:
        """Local vehicle detection using OpenVINO"""
        try:
            # Get input shape
            n, c, h, w = self.input_shape
            
            # Preprocess frame
            resized_frame = cv2.resize(frame, (w, h))
            
            # Convert BGR to RGB and normalize
            input_data = resized_frame.astype(np.float32)
            input_data = np.transpose(input_data, (2, 0, 1))  # HWC to CHW
            input_data = np.expand_dims(input_data, axis=0)  # Add batch dimension
            
            # Run inference
            result = self.compiled_detection_model({self.input_key: input_data})
            
            # Get output
            detections = result[self.output_key]
            
            # Process results
            if len(detections.shape) == 4:
                detections = detections[0][0]
            elif len(detections.shape) == 3:
                detections = detections[0]
            
            coordinates = []
            confidence = []
            types = []
            colors = []
            
            for detection in detections:
                if len(detection) >= 7:
                    conf = detection[2]
                    if conf > self.config.CONFIDENCE_THRESHOLD:
                        # Normalized coordinates
                        x_min = max(0.0, min(detection[3], 1.0))
                        y_min = max(0.0, min(detection[4], 1.0))
                        x_max = max(0.0, min(detection[5], 1.0))
                        y_max = max(0.0, min(detection[6], 1.0))
                        
                        if x_max > x_min and y_max > y_min:
                            coordinates.append([x_min, y_min, x_max, y_max])
                            confidence.append(float(conf))
                            types.append(int(detection[1]))
                            colors.append(0)
            
            return {
                'coordinates': np.array(coordinates) if coordinates else np.array([]).reshape(0, 4),
                'confidence': np.array(confidence),
                'types': np.array(types),
                'colors': np.array(colors)
            }
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return {
                'coordinates': np.array([]).reshape(0, 4),
                'confidence': np.array([]),
                'types': np.array([]),
                'colors': np.array([])
            }
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process single frame for vehicle detection"""
        # Get predictions
        predictions = self.predict_vehicles(frame)
        
        # Process detections
        detections = process_detections(
            predictions,
            frame.shape,
            confidence_threshold=self.config.CONFIDENCE_THRESHOLD
        )
        
        # Update vehicle count
        current_count = len(detections)
        self.vehicle_count = current_count
        if current_count > 0:
            self.total_vehicles += current_count
        
        # Draw detections and metadata
        annotated_frame = draw_detections(frame, detections)
        annotated_frame = self.add_metadata_overlay(annotated_frame)
        
        return annotated_frame
    
    def add_metadata_overlay(self, frame: np.ndarray) -> np.ndarray:
        """Add vehicle count and metadata overlay to frame"""
        overlay = frame.copy()
        
        # Add semi-transparent background for text
        cv2.rectangle(overlay, (10, 10), (400, 120), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Add text information
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f'Current Vehicles: {self.vehicle_count}', (20, 40), font, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f'Total Detected: {self.total_vehicles}', (20, 70), font, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f'Frame: {self.frame_count}', (20, 100), font, 0.7, (0, 255, 0), 2)
        
        return frame
    
    def stream_frame(self, frame: np.ndarray):
        """Stream frame to MediaMTX via FFmpeg with error handling"""
        if not self.streaming_enabled:
            return
            
        if self.ffmpeg_process and self.ffmpeg_process.stdin:
            try:
                self.ffmpeg_process.stdin.write(frame.tobytes())
                self.ffmpeg_process.stdin.flush()
            except BrokenPipeError:
                logger.warning("Broken pipe detected, attempting to restart streaming...")
                self.restart_streaming()
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                self.restart_streaming()
    
    def restart_streaming(self):
        """Restart streaming connection"""
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except:
                pass
            self.ffmpeg_process = None
        
        # Wait a bit before restarting
        time.sleep(2)
        
        # Try to restart streaming
        if self.streaming_enabled:
            logger.info("Attempting to restart streaming...")
            self.setup_streaming()
    
    def run(self):
        """Main processing loop with streaming"""
        logger.info("Starting vehicle counting with OpenVINO and MediaMTX streaming...")
        
        # Setup streaming
        streaming_ready = self.setup_streaming()
        if not streaming_ready:
            logger.warning("Streaming not available, running in local mode only")
        
        try:
            while self.streaming_enabled:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.info("End of video reached, restarting...")
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                self.frame_count += 1
                frame = cv2.resize(frame, (self.config.FRAME_WIDTH, self.config.FRAME_HEIGHT))
                processed_frame = self.process_frame(frame)
                
                # Stream to MediaMTX if available
                if streaming_ready and self.ffmpeg_process:
                    self.stream_frame(processed_frame)
                
                # Control frame rate
                time.sleep(1.0 / self.fps)
                
                # Log progress every 100 frames
                if self.frame_count % 100 == 0:
                    logger.info(f"Processed {self.frame_count} frames, detected {self.vehicle_count} vehicles")
                
        except KeyboardInterrupt:
            logger.info("Stopping vehicle counting...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        
        if self.cap:
            self.cap.release()
        
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except:
                pass
        
        cv2.destroyAllWindows()
        logger.info("Cleanup completed")

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = Config()
    counter = VehicleCounter(config)
    counter.run()