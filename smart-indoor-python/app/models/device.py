from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, ForeignKey, JSON
from app.core.database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True)
    hall_id = Column(String, ForeignKey("halls.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "ac", "fan", "curtain"
    status = Column(String, default="ONLINE")  # "ONLINE", "OFFLINE", "ERROR"
    power = Column(Boolean, default=False)
    control_mode = Column(String, default="AUTO")  # "AUTO", "MANUAL"
    
    # State fields for different actuators
    # AC: power, target_temp, mode ("cool", "heat", "fan", "dry", "auto"), fan_speed ("low", "mid", "high", "auto")
    # Fan: power, speed (0-5 or "low", "mid", "high"), oscillation (bool)
    # Curtain: position (0-100), state ("OPEN", "CLOSED", "PARTIAL", "STOPPED")
    state = Column(JSON, default=dict)
    
    manual_override_until = Column(DateTime, nullable=True)
    last_command_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class DeviceEvent(Base):
    __tablename__ = "device_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.id"), index=True, nullable=False)
    hall_id = Column(String, nullable=False)
    action = Column(String, nullable=False)  # e.g., "SET_TEMPERATURE", "TURN_ON", "SET_SPEED"
    source = Column(String, default="AUTOMATION")  # "MANUAL", "AUTOMATION", "AI", "MQTT"
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
