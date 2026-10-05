from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AutomationRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    condition_type: str  # "TEMPERATURE", "OCCUPANCY", "CO2", "LIGHT"
    operator: str  # ">", "<", ">=", "<=", "==", "BETWEEN"
    threshold: float
    hysteresis: float = 0.5
    action_device: str  # "AC", "FAN", "CURTAIN"
    action_type: str  # "COOLING", "HEATING", "SPEED_HIGH", "OPEN", "CLOSE"
    action_value: Optional[str] = None
    priority: int = 1
    enabled: bool = True
    cooldown_seconds: int = 300

class AutomationRuleCreate(AutomationRuleBase):
    id: str
    hall_id: str

class AutomationRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition_type: Optional[str] = None
    operator: Optional[str] = None
    threshold: Optional[float] = None
    hysteresis: Optional[float] = None
    action_device: Optional[str] = None
    action_type: Optional[str] = None
    action_value: Optional[str] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None
    cooldown_seconds: Optional[int] = None

class AutomationRuleResponse(AutomationRuleBase):
    id: str
    hall_id: str
    last_triggered: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AutomationAction(BaseModel):
    device: str
    action: str
    value: Optional[Any] = None
    reason: str

class AutomationEventResponse(BaseModel):
    id: int
    hall_id: str
    rule_id: Optional[str] = None
    rule_name: str
    trigger_reason: str
    actions_taken: List[Dict[str, Any]] = []
    timestamp: datetime

    class Config:
        from_attributes = True
