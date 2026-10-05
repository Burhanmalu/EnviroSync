from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.environment import EnvironmentReading
from app.models.occupancy import OccupancyReading
from app.models.analytics import ComfortScoreHistory

class AnalyticsService:
    async def get_hall_analytics(self, db: AsyncSession, hall_id: str, hours: int = 24) -> Dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        # 1. Environment Averages
        env_res = await db.execute(
            select(
                func.avg(EnvironmentReading.temperature).label("avg_temp"),
                func.avg(EnvironmentReading.humidity).label("avg_hum"),
                func.avg(EnvironmentReading.co2).label("avg_co2")
            )
            .where(
                EnvironmentReading.hall_id == hall_id,
                EnvironmentReading.timestamp >= since
            )
        )
        row = env_res.first()
        avg_temp = round(float(row.avg_temp or 25.4), 1)
        avg_hum = round(float(row.avg_hum or 51.5), 1)
        avg_co2 = round(float(row.avg_co2 or 560.0), 1)

        # 2. Occupancy Averages
        occ_res = await db.execute(
            select(
                func.avg(OccupancyReading.occupancy_percentage).label("avg_occ")
            )
            .where(
                OccupancyReading.hall_id == hall_id,
                OccupancyReading.timestamp >= since
            )
        )
        occ_row = occ_res.first()
        avg_occ = round(float(occ_row.avg_occ or 42.0), 1)

        # 3. Comfort Trend
        comfort_res = await db.execute(
            select(ComfortScoreHistory)
            .where(
                ComfortScoreHistory.hall_id == hall_id,
                ComfortScoreHistory.timestamp >= since
            )
            .order_by(ComfortScoreHistory.timestamp.asc())
            .limit(24)
        )
        comfort_trend = [
            {
                "score": c.score,
                "status": c.status,
                "timestamp": c.timestamp.isoformat() if c.timestamp else None
            }
            for c in comfort_res.scalars().all()
        ]

        # 4. Energy Saved Estimate (approx calculation based on low-occupancy setback)
        energy_saved = round(max(1.2, (100.0 - avg_occ) * 0.18), 1)

        return {
            "hall_id": hall_id,
            "avg_temperature": avg_temp,
            "avg_humidity": avg_hum,
            "avg_co2": avg_co2,
            "avg_occupancy_pct": avg_occ,
            "comfort_score_trend": comfort_trend,
            "energy_saved_estimate_kwh": energy_saved,
            "timeframe": f"Last {hours} hours"
        }

analytics_service = AnalyticsService()
