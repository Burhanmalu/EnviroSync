from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.comfort.predictor import prediction_ai
from app.models.analytics import EnvironmentalPrediction
from app.iot.device_controller import device_controller

class PredictionService:
    async def predict_hall_metrics(
        self,
        db: AsyncSession,
        hall_id: str,
        current_temp: float,
        current_humidity: float,
        current_co2: float,
        occupancy_count: int,
        horizon_minutes: int = 20
    ) -> Dict[str, Any]:
        dev_state = device_controller.get_state(hall_id)
        ac_power = dev_state["ac"]["power"]

        forecast = prediction_ai.predict_future_metrics(
            current_temp=current_temp,
            current_humidity=current_humidity,
            current_co2=current_co2,
            occupancy_count=occupancy_count,
            ac_power=ac_power,
            horizon_minutes=horizon_minutes
        )

        # Record prediction to DB
        pred_temp = forecast["predictions"]["temperature"]["predicted"]
        pred_record = EnvironmentalPrediction(
            hall_id=hall_id,
            target_metric="temperature",
            current_value=current_temp,
            predicted_value=pred_temp,
            confidence=forecast["confidence"],
            horizon_minutes=horizon_minutes,
            model_version=forecast["model_version"]
        )
        db.add(pred_record)
        await db.commit()

        return forecast

prediction_service = PredictionService()
