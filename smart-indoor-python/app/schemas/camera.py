from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel

class CameraStatusResponse(BaseModel):
    status: str  # "ONLINE", "OFFLINE", "CONNECTING", "ERROR"
    camera_id: str
    hall_id: str
    camera_source: Optional[str] = "webcam"
    people_detected: int
    occupancy_percentage: float
    zone_distribution: Dict[str, int]
    fps: float
    inference_time_ms: float
    image_base64: Optional[str] = None
    privacy_notice: str = "Privacy Preserved: YOLO/HOG person detection only. No facial recognition or biometric identity tracking."
    timestamp: datetime
