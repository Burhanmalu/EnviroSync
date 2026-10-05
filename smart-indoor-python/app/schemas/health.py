from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel

class HealthCheckResponse(BaseModel):
    status: str  # "HEALTHY", "DEGRADED", "UNHEALTHY"
    version: str
    uptime_seconds: float
    components: Dict[str, Any]
    timestamp: datetime
