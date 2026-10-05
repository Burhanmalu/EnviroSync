from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.comfort.scorer import comfort_scorer
from app.models.analytics import ComfortScoreHistory
from app.models.hall import Hall
from sqlalchemy.future import select

class ComfortService:
    async def evaluate_and_record(
        self,
        db: AsyncSession,
        hall_id: str,
        temperature: float,
        humidity: float,
        co2: float,
        occupancy_pct: float,
        light: float
    ) -> Dict[str, Any]:
        result = comfort_scorer.calculate(
            temperature=temperature,
            humidity=humidity,
            co2=co2,
            occupancy_pct=occupancy_pct,
            light=light
        )
        
        # Save snapshot
        history = ComfortScoreHistory(
            hall_id=hall_id,
            score=result["score"],
            status=result["status"],
            temperature_score=result["temperature_score"],
            humidity_score=result["humidity_score"],
            air_quality_score=result["air_quality_score"],
            occupancy_score=result["occupancy_score"],
            light_score=result["light_score"]
        )
        db.add(history)

        # Update Hall comfort summary
        hall_res = await db.execute(select(Hall).where(Hall.id == hall_id))
        hall = hall_res.scalars().first()
        if hall:
            hall.comfort_score = result["score"]
            hall.comfort_status = result["status"]

        await db.commit()
        result["timestamp"] = datetime.now(timezone.utc)
        return result

    def calculate_instant(
        self,
        temperature: float,
        humidity: float,
        co2: float,
        occupancy_pct: float,
        light: float
    ) -> Dict[str, Any]:
        res = comfort_scorer.calculate(temperature, humidity, co2, occupancy_pct, light)
        res["timestamp"] = datetime.now(timezone.utc)
        return res

comfort_service = ComfortService()
