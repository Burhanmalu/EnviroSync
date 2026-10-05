from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class HallBase(BaseModel):
    name: str
    building: str
    floor: int = 1
    capacity: int = 50

class HallCreate(HallBase):
    id: str

class HallUpdate(BaseModel):
    name: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    status: Optional[str] = None
    comfort_score: Optional[int] = None
    comfort_status: Optional[str] = None

class HallResponse(HallBase):
    id: str
    current_occupancy: int = 0
    status: str = "OPTIMAL"
    comfort_score: int = 85
    comfort_status: str = "GOOD"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
