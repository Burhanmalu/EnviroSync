from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.occupancy import OccupancyData, OccupancyResponse
from app.services.occupancy_service import occupancy_service
from app.services.environment_service import environment_service
from app.services.automation_service import automation_service
from app.services.comfort_service import comfort_service
from app.realtime.manager import connection_manager

router = APIRouter(tags=["Occupancy"])

@router.get("/halls/{id}/occupancy", response_model=OccupancyResponse)
async def get_hall_occupancy(id: str, db: AsyncSession = Depends(get_db)):
    data = await occupancy_service.get_latest_occupancy(db, id)
    return OccupancyResponse(**data)

@router.post("/halls/{id}/occupancy", response_model=OccupancyResponse)
async def ingest_hall_occupancy(
    id: str,
    payload: OccupancyData,
    db: AsyncSession = Depends(get_db)
):
    payload.hall_id = id
    reading = await occupancy_service.record_occupancy(db, payload)

    # Get environment
    env_data = await environment_service.get_latest_reading(db, id)

    # Re-evaluate comfort
    await comfort_service.evaluate_and_record(
        db,
        id,
        temperature=env_data["temperature"],
        humidity=env_data["humidity"],
        co2=env_data["co2"],
        occupancy_pct=payload.occupancy_percentage,
        light=env_data["light"]
    )

    # Re-evaluate automation
    await automation_service.evaluate_hall_automation(
        db,
        id,
        env_data=env_data,
        occ_data=payload.model_dump()
    )

    # Broadcast via WebSocket
    response_data = await occupancy_service.get_latest_occupancy(db, id)
    await connection_manager.broadcast_to_hall(id, {
        "event_type": "occupancy_update",
        "hall_id": id,
        "data": {
            **response_data,
            "timestamp": response_data["timestamp"].isoformat() if hasattr(response_data["timestamp"], "isoformat") else str(response_data["timestamp"])
        }
    })

    return OccupancyResponse(**response_data)
