from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.models.environment import EnvironmentReading
from app.schemas.environment import EnvironmentData
from app.utils.calculations import calculate_iaq_score
from app.iot.sensor_manager import sensor_manager

class EnvironmentService:
    async def record_reading(self, db: AsyncSession, data: EnvironmentData) -> EnvironmentReading:
        reading = EnvironmentReading(
            hall_id=data.hall_id,
            temperature=data.temperature,
            humidity=data.humidity,
            co2=data.co2,
            light=data.light,
            timestamp=data.timestamp or datetime.now(timezone.utc)
        )
        db.add(reading)
        await db.commit()
        await db.refresh(reading)

        # Update sensor manager cache
        sensor_manager.ingest_reading(
            data.hall_id,
            data.temperature,
            data.humidity,
            data.co2,
            data.light
        )
        return reading

    async def get_latest_reading(self, db: AsyncSession, hall_id: str) -> Dict[str, Any]:
        result = await db.execute(
            select(EnvironmentReading)
            .where(EnvironmentReading.hall_id == hall_id)
            .order_by(desc(EnvironmentReading.timestamp))
            .limit(1)
        )
        reading = result.scalars().first()
        if reading:
            iaq = calculate_iaq_score(reading.co2, reading.humidity, reading.temperature)
            return {
                "id": reading.id,
                "hall_id": reading.hall_id,
                "temperature": reading.temperature,
                "humidity": reading.humidity,
                "co2": reading.co2,
                "light": reading.light,
                "timestamp": reading.timestamp,
                "iaq_score": iaq["iaq_score"],
                "iaq_status": iaq["iaq_status"]
            }
        
        # Fallback to sensor manager
        cached = sensor_manager.get_latest(hall_id)
        iaq = calculate_iaq_score(cached["co2"], cached["humidity"], cached["temperature"])
        return {
            "hall_id": hall_id,
            "temperature": cached["temperature"],
            "humidity": cached["humidity"],
            "co2": cached["co2"],
            "light": cached["light"],
            "timestamp": datetime.now(timezone.utc),
            "iaq_score": iaq["iaq_score"],
            "iaq_status": iaq["iaq_status"]
        }

    async def get_history(self, db: AsyncSession, hall_id: str, hours: int = 24) -> List[EnvironmentReading]:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        result = await db.execute(
            select(EnvironmentReading)
            .where(
                EnvironmentReading.hall_id == hall_id,
                EnvironmentReading.timestamp >= since
            )
            .order_by(EnvironmentReading.timestamp.asc())
        )
        return list(result.scalars().all())

environment_service = EnvironmentService()
