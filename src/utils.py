import cv2
import numpy as np
from typing import List, Dict, Tuple

def process_detections(predictions: Dict, frame_shape: Tuple, confidence_threshold: float = 0.5) -> List[Dict]:
    """Process raw predictions into detection objects"""
    detections = []
    
    coordinates = predictions.get('coordinates', [])
    confidences = predictions.get('confidence', [])
    types = predictions.get('types', [])
    colors = predictions.get('colors', [])
    
    for i in range(len(coordinates)):
        if len(confidences) > i and confidences[i] > confidence_threshold:
            # Convert normalized coordinates to pixel coordinates
            x1, y1, x2, y2 = coordinates[i]
            x1 = int(x1 * frame_shape[1])
            y1 = int(y1 * frame_shape[0])
            x2 = int(x2 * frame_shape[1])
            y2 = int(y2 * frame_shape[0])
            
            detection = {
                'bbox': (x1, y1, x2, y2),
                'confidence': confidences[i],
                'type': get_vehicle_type(types[i] if len(types) > i else 0),
                'color': get_vehicle_color(colors[i] if len(colors) > i else 0)
            }
            detections.append(detection)
    
    return detections

def get_vehicle_type(type_id: int) -> str:
    """Convert type ID to string"""
    types = ['car', 'van', 'truck', 'bus', 'motorcycle']
    return types[int(type_id)] if int(type_id) < len(types) else 'unknown'

def get_vehicle_color(color_id: int) -> str:
    """Convert color ID to string"""
    colors = ['white', 'gray', 'yellow', 'red', 'green', 'blue', 'black']
    return colors[int(color_id)] if int(color_id) < len(colors) else 'unknown'

def draw_detections(frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
    """Draw detection boxes and labels on frame"""
    annotated_frame = frame.copy()
    
    for detection in detections:
        x1, y1, x2, y2 = detection['bbox']
        confidence = detection['confidence']
        vehicle_type = detection['type']
        
        # Draw bounding box
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        label = f"{vehicle_type} {confidence:.2f}"
        
        # Calculate label size and position
        (label_width, label_height), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        
        # Draw label background
        cv2.rectangle(
            annotated_frame,
            (x1, y1 - label_height - 10),
            (x1 + label_width, y1),
            (0, 255, 0),
            -1
        )
        
        # Draw label text
        cv2.putText(
            annotated_frame,
            label,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1
        )
    
    return annotated_frame