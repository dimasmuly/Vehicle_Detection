import os
from dataclasses import dataclass

@dataclass
class Config:
    # Video settings
    INPUT_VIDEO: str = os.getenv('INPUT_VIDEO', '../videos/test_video.mp4')
    FRAME_WIDTH: int = 1280
    FRAME_HEIGHT: int = 720
    
    # OVMS settings
    OVMS_HOST: str = os.getenv('OVMS_HOST', 'localhost')
    OVMS_PORT: int = int(os.getenv('OVMS_PORT', '9000'))
    
    # MediaMTX settings
    MEDIAMTX_URL: str = os.getenv('MEDIAMTX_URL', 'rtmp://localhost:1935/live/stream')
    
    # Detection settings
    CONFIDENCE_THRESHOLD: float = 0.5
    
    # Model settings
    MODEL_PATH: str = os.getenv('MODEL_PATH', '../models')