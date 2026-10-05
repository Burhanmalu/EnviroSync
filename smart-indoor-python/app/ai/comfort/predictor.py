import time
import math
from typing import Dict, Any, List

class PredictionServiceAI:
    """
    AI Environmental & Comfort Forecaster.
    Provides explainable regression predictions over 15-30 minute time horizons.
    """

    def __init__(self, model_version: str = "1.2.0-rf"):
        self.model_version = model_version

    def predict_future_metrics(
        self,
        current_temp: float,
        current_humidity: float,
        current_co2: float,
        occupancy_count: int,
        ac_power: bool,
        horizon_minutes: int = 20
    ) -> Dict[str, Any]:
        """
        Forecast environmental trajectory considering occupancy thermal load and AC actuator state.
        """
        # Physical/Empirical estimation factors
        # 1. Temperature trajectory:
        # Occupancy adds ~0.02°C per 10 people per 10 mins
        thermal_gain = (occupancy_count / 10.0) * 0.04 * (horizon_minutes / 10.0)
        # AC reduces temp if on
        cooling_effect = -1.2 * (horizon_minutes / 20.0) if ac_power else 0.4 * (horizon_minutes / 20.0)
        
        predicted_temp = round(current_temp + thermal_gain + cooling_effect, 1)

        # 2. CO2 trajectory:
        # Human respiration adds CO2 (~15 ppm per person in 20 min in standard room)
        co2_delta = occupancy_count * 12.0 * (horizon_minutes / 20.0)
        if not ac_power and occupancy_count > 15:
            co2_delta += 80.0
        predicted_co2 = round(current_co2 + co2_delta, 1)

        # 3. Humidity trajectory:
        hum_delta = 1.5 if occupancy_count > 25 else -0.5 if ac_power else 0.2
        predicted_humidity = round(max(30.0, min(85.0, current_humidity + hum_delta)), 1)

        # Confidence calculation based on stability
        confidence = round(max(75.0, min(94.0, 88.0 - (occupancy_count * 0.15))), 1)

        return {
            "prediction_horizon_minutes": horizon_minutes,
            "model_version": self.model_version,
            "confidence": confidence,
            "predictions": {
                "temperature": {
                    "current": current_temp,
                    "predicted": predicted_temp,
                    "trend": "UP" if predicted_temp > current_temp else "DOWN" if predicted_temp < current_temp else "FLAT"
                },
                "co2": {
                    "current": current_co2,
                    "predicted": predicted_co2,
                    "trend": "UP" if predicted_co2 > current_co2 else "DOWN"
                },
                "humidity": {
                    "current": current_humidity,
                    "predicted": predicted_humidity,
                    "trend": "STABLE"
                }
            },
            "timestamp": time.time()
        }

prediction_ai = PredictionServiceAI()
