import logging
from typing import Dict, Any, Callable
from app.utils.validators import validate_environment_ranges

logger = logging.getLogger("smart_indoor.sensors")

class SensorManager:
    """
    Ingestion hub for DHT22/BME280 (Temp/Humidity), SCD30/MQ-135 (CO2),
    and BH1750 (Ambient Light) sensor inputs.
    """

    def __init__(self):
        self.latest_readings: Dict[str, Dict[str, Any]] = {}
        self.listeners: list[Callable[[str, Dict[str, Any]], None]] = []

    def ingest_reading(self, hall_id: str, temperature: float, humidity: float, co2: float, light: float) -> bool:
        valid, msg = validate_environment_ranges(temperature, humidity, co2, light)
        if not valid:
            logger.warning(f"Discarding invalid sensor reading for {hall_id}: {msg}")
            return False

        data = {
            "hall_id": hall_id,
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "co2": round(co2, 1),
            "light": round(light, 1)
        }
        self.latest_readings[hall_id] = data

        for listener in self.listeners:
            try:
                listener(hall_id, data)
            except Exception as e:
                logger.error(f"Error in sensor listener: {e}")

        return True

    def get_latest(self, hall_id: str) -> Dict[str, Any]:
        return self.latest_readings.get(hall_id, {
            "hall_id": hall_id,
            "temperature": 25.5,
            "humidity": 52.0,
            "co2": 580.0,
            "light": 450.0
        })

    def add_listener(self, listener: Callable[[str, Dict[str, Any]], None]):
        self.listeners.append(listener)

sensor_manager = SensorManager()
