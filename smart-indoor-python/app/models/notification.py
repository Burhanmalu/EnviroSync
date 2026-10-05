from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from app.core.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    hall_id = Column(String, ForeignKey("halls.id"), index=True, nullable=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, default="INFO")  # "INFO", "WARNING", "CRITICAL", "SUCCESS"
    category = Column(String, default="ENVIRONMENT")  # "ENVIRONMENT", "OCCUPANCY", "DEVICE", "AUTOMATION", "SYSTEM"
    read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
