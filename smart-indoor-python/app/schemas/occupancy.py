from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field

class OccupancyData(BaseModel):
    hall_id: str
    people_count: int = Field(..., ge=0, description="Detected number of people")
    occupancy_percentage: float = Field(..., ge=0, le=100)
    capacity: int = Field(..., gt=0)
    zone_distribution: Optional[Dict[str, int]] = Field(
        default={"Zone A": 0, "Zone B": 0, "Zone C": 0, "Zone D": 0},
        description="Room occupancy zone percentages"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class OccupancyResponse(OccupancyData):
    id: Optional[int] = None
    status: str = "NORMAL"  # "LOW", "NORMAL", "CROWDED", "OVER_CAPACITY"

    class Config:
        from_attributes = True
