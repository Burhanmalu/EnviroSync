from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.notification import NotificationResponse, NotificationCreate
from app.services.notification_service import notification_service
from app.realtime.manager import connection_manager

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    hall_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    notifs = await notification_service.get_notifications(db, hall_id=hall_id, limit=limit)
    return [NotificationResponse.model_validate(n) for n in notifs]

@router.post("", response_model=NotificationResponse)
async def create_notification(
    notif_in: NotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    notif = await notification_service.create_notification(db, notif_in)
    
    # Broadcast notification
    if notif.hall_id:
        await connection_manager.broadcast_to_hall(notif.hall_id, {
            "event_type": "notification",
            "hall_id": notif.hall_id,
            "data": NotificationResponse.model_validate(notif).model_dump(mode="json")
        })
    else:
        await connection_manager.broadcast_global({
            "event_type": "notification",
            "hall_id": "global",
            "data": NotificationResponse.model_validate(notif).model_dump(mode="json")
        })

    return NotificationResponse.model_validate(notif)

@router.put("/{id}/read", response_model=NotificationResponse)
async def mark_notification_read(id: str, db: AsyncSession = Depends(get_db)):
    notif = await notification_service.mark_as_read(db, id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.model_validate(notif)
