from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.hall import Hall
from app.schemas.hall import HallCreate, HallUpdate, HallResponse
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter(prefix="/halls", tags=["Halls"])

@router.get("", response_model=List[HallResponse])
async def get_all_halls(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hall).order_by(Hall.name.asc()))
    halls = result.scalars().all()
    return [HallResponse.model_validate(h) for h in halls]

@router.post("", response_model=HallResponse, status_code=status.HTTP_201_CREATED)
async def create_hall(
    hall_in: HallCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    existing = await db.execute(select(Hall).where(Hall.id == hall_in.id))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Hall ID already exists")

    hall = Hall(
        id=hall_in.id,
        name=hall_in.name,
        building=hall_in.building,
        floor=hall_in.floor,
        capacity=hall_in.capacity,
        current_occupancy=0,
        status="OPTIMAL",
        comfort_score=85,
        comfort_status="GOOD"
    )
    db.add(hall)
    await db.commit()
    await db.refresh(hall)
    return HallResponse.model_validate(hall)

@router.get("/{id}", response_model=HallResponse)
async def get_hall_by_id(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hall).where(Hall.id == id))
    hall = result.scalars().first()
    if not hall:
        raise HTTPException(status_code=404, detail="Hall not found")
    return HallResponse.model_validate(hall)

@router.put("/{id}", response_model=HallResponse)
async def update_hall(
    id: str,
    hall_in: HallUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    result = await db.execute(select(Hall).where(Hall.id == id))
    hall = result.scalars().first()
    if not hall:
        raise HTTPException(status_code=404, detail="Hall not found")

    for key, value in hall_in.model_dump(exclude_unset=True).items():
        setattr(hall, key, value)

    await db.commit()
    await db.refresh(hall)
    return HallResponse.model_validate(hall)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hall(
    id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    result = await db.execute(select(Hall).where(Hall.id == id))
    hall = result.scalars().first()
    if not hall:
        raise HTTPException(status_code=404, detail="Hall not found")

    await db.delete(hall)
    await db.commit()
    return None
