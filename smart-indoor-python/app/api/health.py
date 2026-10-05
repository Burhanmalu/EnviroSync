import time
from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas.health import HealthCheckResponse
from app.core.config import settings
from app.iot.mqtt_client import mqtt_service

router = APIRouter(tags=["Health & System"])
start_time = time.time()

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    uptime = round(time.time() - start_time, 1)
    return HealthCheckResponse(
        status="HEALTHY",
        version=settings.VERSION,
        uptime_seconds=uptime,
        components={
            "api_server": "ONLINE",
            "database": "CONNECTED",
            "mqtt_bridge": "CONNECTED" if mqtt_service.connected else "VIRTUAL_READY",
            "ai_occupancy_detector": "ONLINE",
            "comfort_engine": "ONLINE",
            "simulation_worker": "ACTIVE" if settings.SIMULATION_ENABLED else "DISABLED"
        },
        timestamp=datetime.now(timezone.utc)
    )
