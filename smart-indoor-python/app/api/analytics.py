from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.analytics import AnalyticsSummaryResponse, ComfortScoreResponse, PredictionResponse
from app.services.analytics_service import analytics_service
from app.services.comfort_service import comfort_service
from app.services.prediction_service import prediction_service
from app.services.environment_service import environment_service
from app.services.occupancy_service import occupancy_service

router = APIRouter(tags=["Analytics"])

@router.get("/halls/{id}/analytics", response_model=AnalyticsSummaryResponse)
async def get_hall_analytics(
    id: str,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    data = await analytics_service.get_hall_analytics(db, id, hours=hours)
    return AnalyticsSummaryResponse(**data)

@router.get("/halls/{id}/comfort", response_model=ComfortScoreResponse)
async def get_hall_comfort(id: str, db: AsyncSession = Depends(get_db)):
    env_data = await environment_service.get_latest_reading(db, id)
    occ_data = await occupancy_service.get_latest_occupancy(db, id)

    score_data = comfort_service.calculate_instant(
        temperature=env_data["temperature"],
        humidity=env_data["humidity"],
        co2=env_data["co2"],
        occupancy_pct=occ_data["occupancy_percentage"],
        light=env_data["light"]
    )
    return ComfortScoreResponse(**score_data)

@router.get("/halls/{id}/predictions")
async def get_hall_predictions(
    id: str,
    horizon_minutes: int = Query(20, ge=5, le=60),
    db: AsyncSession = Depends(get_db)
):
    env_data = await environment_service.get_latest_reading(db, id)
    occ_data = await occupancy_service.get_latest_occupancy(db, id)

    forecast = await prediction_service.predict_hall_metrics(
        db,
        id,
        current_temp=env_data["temperature"],
        current_humidity=env_data["humidity"],
        current_co2=env_data["co2"],
        occupancy_count=occ_data["people_count"],
        horizon_minutes=horizon_minutes
    )
    return forecast
