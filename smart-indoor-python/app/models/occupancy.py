from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from app.core.database import Base

class OccupancyReading(Base):
    __tablename__ = "occupancy_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hall_id = Column(String, ForeignKey("halls.id"), index=True, nullable=False)
    people_count = Column(Integer, nullable=False)
    occupancy_percentage = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    zone_distribution = Column(JSON, nullable=True)  # e.g., {"Zone A": 80, "Zone B": 60, "Zone C": 30, "Zone D": 90}
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
