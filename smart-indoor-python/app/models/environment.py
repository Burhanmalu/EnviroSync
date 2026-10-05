from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from app.core.database import Base

class EnvironmentReading(Base):
    __tablename__ = "environment_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hall_id = Column(String, ForeignKey("halls.id"), index=True, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    co2 = Column(Float, nullable=False)
    light = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
