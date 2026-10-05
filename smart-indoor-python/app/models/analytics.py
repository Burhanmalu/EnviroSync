from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, JSON
from app.core.database import Base

class ComfortScoreHistory(Base):
    __tablename__ = "comfort_score_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hall_id = Column(String, ForeignKey("halls.id"), index=True, nullable=False)
    score = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    temperature_score = Column(Integer, nullable=False)
    humidity_score = Column(Integer, nullable=False)
    air_quality_score = Column(Integer, nullable=False)
    occupancy_score = Column(Integer, nullable=False)
    light_score = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class EnvironmentalPrediction(Base):
    __tablename__ = "environmental_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hall_id = Column(String, ForeignKey("halls.id"), index=True, nullable=False)
    target_metric = Column(String, nullable=False)  # "temperature", "humidity", "co2"
    current_value = Column(Float, nullable=False)
    predicted_value = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)  # 0-100
    horizon_minutes = Column(Integer, default=20)
    model_version = Column(String, default="1.0.0")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    component = Column(String, nullable=False)  # "AI_VISION", "MQTT", "AUTOMATION", "SIMULATOR"
    level = Column(String, default="INFO")
    message = Column(String, nullable=False)
    metadata_json = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
