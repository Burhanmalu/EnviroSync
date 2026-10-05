import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

class NotificationService:
    async def get_notifications(self, db: AsyncSession, hall_id: Optional[str] = None, limit: int = 50) -> List[Notification]:
        query = select(Notification).order_by(Notification.timestamp.desc()).limit(limit)
        if hall_id:
            query = query.where(Notification.hall_id == hall_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_notification(self, db: AsyncSession, notif_in: NotificationCreate) -> Notification:
        notif_id = notif_in.id or f"notif-{uuid.uuid4().hex[:8]}"
        notif = Notification(
            id=notif_id,
            hall_id=notif_in.hall_id,
            title=notif_in.title,
            message=notif_in.message,
            type=notif_in.type,
            category=notif_in.category
        )
        db.add(notif)
        await db.commit()
        await db.refresh(notif)
        return notif

    async def mark_as_read(self, db: AsyncSession, notification_id: str) -> Optional[Notification]:
        result = await db.execute(select(Notification).where(Notification.id == notification_id))
        notif = result.scalars().first()
        if notif:
            notif.read = True
            await db.commit()
            await db.refresh(notif)
        return notif

notification_service = NotificationService()
