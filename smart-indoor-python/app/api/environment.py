from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.environment import EnvironmentData, EnvironmentResponse
from app.services.environment_service import environment_service
from app.services.automation_service import automation_service
from app.services.occupancy_service import occupancy_service
from app.services.comfort_service import comfort_service
from app.realtime.manager import connection_manager

router = APIRouter(tags=["Environment"])

@router.get("/halls/{id}/environment", response_model=EnvironmentResponse)
async def get_hall_environment(id: str, db: AsyncSession = Depends(get_db)):
    data = await environment_service.get_latest_reading(db, id)
    return EnvironmentResponse(**data)

@router.post("/halls/{id}/environment", response_model=EnvironmentResponse)
async def ingest_hall_environment(
    id: str,
    payload: EnvironmentData,
    db: AsyncSession = Depends(get_db)
):
    payload.hall_id = id
    reading = await environment_service.record_reading(db, payload)
    
    # Get current occupancy
    occ_data = await occupancy_service.get_latest_occupancy(db, id)

    # Re-evaluate comfort score
    comfort = await comfort_service.evaluate_and_record(
        db,
        id,
        temperature=payload.temperature,
        humidity=payload.humidity,
        co2=payload.co2,
        occupancy_pct=occ_data["occupancy_percentage"],
        light=payload.light
    )

    # Re-evaluate automation rules
    await automation_service.evaluate_hall_automation(
        db,
        id,
        env_data={
            "temperature": payload.temperature,
            "humidity": payload.humidity,
            "co2": payload.co2,
            "light": payload.light
        },
        occ_data=occ_data
    )

    # Broadcast environment update via WebSocket
    response_data = await environment_service.get_latest_reading(db, id)
    await connection_manager.broadcast_to_hall(id, {
        "event_type": "environment_update",
        "hall_id": id,
        "data": {
            **response_data,
            "timestamp": response_data["timestamp"].isoformat() if hasattr(response_data["timestamp"], "isoformat") else str(response_data["timestamp"])
        }
    })

    return EnvironmentResponse(**response_data)

@router.get("/halls/{id}/environment/history", response_model=List[EnvironmentResponse])
async def get_hall_environment_history(
    id: str,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    readings = await environment_service.get_history(db, id, hours=hours)
    return [
        EnvironmentResponse(
            id=r.id,
            hall_id=r.hall_id,
            temperature=r.temperature,
            humidity=r.humidity,
            co2=r.co2,
            light=r.light,
            timestamp=r.timestamp
        )
        for r in readings
    ]
