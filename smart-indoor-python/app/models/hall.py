from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, JSON
from app.core.database import Base

class Hall(Base):
    __tablename__ = "halls"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    building = Column(String, nullable=False)
    floor = Column(Integer, default=1)
    capacity = Column(Integer, nullable=False, default=50)
    current_occupancy = Column(Integer, default=0)
    status = Column(String, default="OPTIMAL")  # OPTIMAL, MODERATE, CRITICAL
    comfort_score = Column(Integer, default=85)
    comfort_status = Column(String, default="GOOD")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
