from typing import Optional, Dict, Any
from pydantic import BaseModel

class DemoScenarioRequest(BaseModel):
    scenario: str  # "NORMAL", "HIGH_TEMPERATURE", "HIGH_OCCUPANCY", "HIGH_CO2", "LOW_OCCUPANCY"
    hall_id: Optional[str] = None
    duration_seconds: Optional[int] = 300

class DemoScenarioResponse(BaseModel):
    success: bool
    current_scenario: str
    hall_id: str
    message: str
    applied_parameters: Dict[str, Any]
