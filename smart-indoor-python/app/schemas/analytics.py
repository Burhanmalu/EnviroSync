from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ComfortScoreResponse(BaseModel):
    score: int  # 0-100
    status: str  # "EXCELLENT", "GOOD", "FAIR", "POOR"
    temperature_score: int
    humidity_score: int
    air_quality_score: int
    occupancy_score: int
    light_score: int
    disclaimer: str = "System Comfort Score - calculated using multi-parameter environmental indexing"
    timestamp: datetime

class PredictionResponse(BaseModel):
    hall_id: str
    metric: str
    current_value: float
    predicted_value: float
    confidence: float  # e.g., 84.0%
    prediction_horizon_minutes: int
    model_version: str
    timestamp: datetime

class AnalyticsSummaryResponse(BaseModel):
    hall_id: str
    avg_temperature: float
    avg_humidity: float
    avg_co2: float
    avg_occupancy_pct: float
    comfort_score_trend: List[Dict[str, Any]]
    energy_saved_estimate_kwh: float
    timeframe: str
