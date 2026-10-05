from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NotificationBase(BaseModel):
    title: str
    message: str
    type: str = "INFO"  # "INFO", "WARNING", "CRITICAL", "SUCCESS"
    category: str = "ENVIRONMENT"  # "ENVIRONMENT", "OCCUPANCY", "DEVICE", "AUTOMATION", "SYSTEM"
    hall_id: Optional[str] = None

class NotificationCreate(NotificationBase):
    id: Optional[str] = None

class NotificationResponse(NotificationBase):
    id: str
    read: bool = False
    timestamp: datetime

    class Config:
        from_attributes = True
