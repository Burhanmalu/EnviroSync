from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from app.core.database import Base

class CameraEvent(Base):
    __tablename__ = "camera_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hall_id = Column(String, ForeignKey("halls.id"), index=True, nullable=False)
    camera_id = Column(String, default="cam-main")
    status = Column(String, default="ONLINE")  # "ONLINE", "OFFLINE", "CONNECTING", "ERROR"
    people_detected = Column(Integer, default=0)
    occupancy_percentage = Column(Float, default=0.0)
    inference_time_ms = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
