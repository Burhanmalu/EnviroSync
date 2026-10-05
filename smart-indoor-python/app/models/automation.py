from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey, JSON, Integer
from app.core.database import Base

class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id = Column(String, primary_key=True, index=True)
    hall_id = Column(String, ForeignKey("halls.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    condition_type = Column(String, nullable=False)  # "TEMPERATURE", "OCCUPANCY", "CO2", "LIGHT", "SCHEDULE"
    operator = Column(String, nullable=False)  # ">", "<", ">=", "<=", "==", "BETWEEN"
    threshold = Column(Float, nullable=False)
    hysteresis = Column(Float, default=0.5)  # Anti-flapping hysteresis margin
    action_device = Column(String, nullable=False)  # "AC", "FAN", "CURTAIN"
    action_type = Column(String, nullable=False)  # "COOLING", "HEATING", "SPEED_HIGH", "OPEN", "CLOSE"
    action_value = Column(String, nullable=True)
    priority = Column(Integer, default=1)
    enabled = Column(Boolean, default=True)
    cooldown_seconds = Column(Integer, default=300)
    last_triggered = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class AutomationEvent(Base):
    __tablename__ = "automation_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hall_id = Column(String, ForeignKey("halls.id"), index=True, nullable=False)
    rule_id = Column(String, nullable=True)
    rule_name = Column(String, nullable=False)
    trigger_reason = Column(String, nullable=False)
    actions_taken = Column(JSON, default=list)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
