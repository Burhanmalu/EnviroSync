from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.models.occupancy import OccupancyReading
from app.models.hall import Hall
from app.schemas.occupancy import OccupancyData
from app.ai.occupancy.detector import occupancy_detector
from app.ai.occupancy.tracker import occupancy_tracker

class OccupancyService:
    async def record_occupancy(self, db: AsyncSession, data: OccupancyData) -> OccupancyReading:
        reading = OccupancyReading(
            hall_id=data.hall_id,
            people_count=data.people_count,
            occupancy_percentage=data.occupancy_percentage,
            capacity=data.capacity,
            zone_distribution=data.zone_distribution,
            timestamp=data.timestamp or datetime.now(timezone.utc)
        )
        db.add(reading)

        # Update Hall current_occupancy
        result = await db.execute(select(Hall).where(Hall.id == data.hall_id))
        hall = result.scalars().first()
        if hall:
            hall.current_occupancy = data.people_count

        await db.commit()
        await db.refresh(reading)
        return reading

    async def get_latest_occupancy(self, db: AsyncSession, hall_id: str) -> Dict[str, Any]:
        from app.services.camera_service import camera_service

        # If live camera feed is active for hall-01, return real-time camera occupancy
        if camera_service.camera_source == "webcam" or camera_service.last_detection_result is not None:
            last_det = camera_service.last_detection_result
            people = last_det.get("people_detected", 0)
            capacity = 60
            pct = round((people / capacity) * 100.0, 1)
            status = (
                "OVER_CAPACITY" if pct > 100
                else "CROWDED" if pct >= 80
                else "NORMAL" if pct >= 20
                else "LOW"
            )
            return {
                "hall_id": hall_id,
                "people_count": people,
                "occupancy_percentage": pct,
                "capacity": capacity,
                "zone_distribution": last_det.get("zone_distribution", {"Zone A": 0, "Zone B": 0, "Zone C": 0, "Zone D": 0}),
                "status": status,
                "timestamp": datetime.now(timezone.utc)
            }

        result = await db.execute(
            select(OccupancyReading)
            .where(OccupancyReading.hall_id == hall_id)
            .order_by(desc(OccupancyReading.timestamp))
            .limit(1)
        )
        reading = result.scalars().first()
        if reading:
            status = (
                "OVER_CAPACITY" if reading.occupancy_percentage > 100
                else "CROWDED" if reading.occupancy_percentage >= 80
                else "NORMAL" if reading.occupancy_percentage >= 20
                else "LOW"
            )
            return {
                "id": reading.id,
                "hall_id": reading.hall_id,
                "people_count": reading.people_count,
                "occupancy_percentage": reading.occupancy_percentage,
                "capacity": reading.capacity,
                "zone_distribution": reading.zone_distribution or {"Zone A": 0, "Zone B": 0, "Zone C": 0, "Zone D": 0},
                "status": status,
                "timestamp": reading.timestamp
            }

        # Fallback to simulated CV reading
        cv_result = occupancy_detector.detect_frame()
        capacity = 60
        pct = round((cv_result["people_count"] / capacity) * 100.0, 1)
        return {
            "hall_id": hall_id,
            "people_count": cv_result["people_count"],
            "occupancy_percentage": pct,
            "capacity": capacity,
            "zone_distribution": cv_result["zones"],
            "status": "NORMAL",
            "timestamp": datetime.now(timezone.utc)
        }

occupancy_service = OccupancyService()
