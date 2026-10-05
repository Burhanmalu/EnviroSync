from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.demo import DemoScenarioRequest, DemoScenarioResponse
from app.services.demo_service import demo_service
from app.models.hall import Hall
from sqlalchemy.future import select

router = APIRouter(prefix="/demo", tags=["Demo Mode"])

@router.post("/scenario", response_model=DemoScenarioResponse)
async def activate_demo_scenario(
    req: DemoScenarioRequest,
    db: AsyncSession = Depends(get_db)
):
    target_hall = req.hall_id
    if not target_hall:
        # Default to first hall
        h_res = await db.execute(select(Hall).limit(1))
        h = h_res.scalars().first()
        target_hall = h.id if h else "hall-01"

    try:
        res = demo_service.trigger_scenario(target_hall, req.scenario)
        return DemoScenarioResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{hall_id}")
async def get_demo_status(hall_id: str):
    scenario = demo_service.get_status(hall_id)
    return {"hall_id": hall_id, "current_scenario": scenario}
