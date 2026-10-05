from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class EnvironmentData(BaseModel):
    hall_id: str
    temperature: float = Field(..., description="Temperature in Celsius (24-32°C)")
    humidity: float = Field(..., description="Humidity percentage (40-75%)")
    co2: float = Field(..., description="CO2 in ppm (400-1800 ppm)")
    light: float = Field(..., description="Light level in lux (100-900 lux)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EnvironmentResponse(EnvironmentData):
    id: Optional[int] = None
    iaq_score: Optional[int] = 85
    iaq_status: Optional[str] = "GOOD"

    class Config:
        from_attributes = True

class EnvironmentHistoricalQuery(BaseModel):
    hall_id: str
    hours: int = 24
