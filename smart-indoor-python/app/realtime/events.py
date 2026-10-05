from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, Field

class RealtimeEvent(BaseModel):
    event_type: str  # "environment_update", "occupancy_update", "device_update", "automation_event", "notification", "connection_status"
    hall_id: str
    data: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
