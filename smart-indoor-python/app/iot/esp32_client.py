import logging
from typing import Dict, Any, Optional
from app.iot.mqtt_client import mqtt_service

logger = logging.getLogger("smart_indoor.esp32")

class ESP32Client:
    """
    Direct hardware abstraction for ESP32 microcontrollers.
    Translates high-level device states to low-level GPIO, PWM, and Relay commands.
    """

    def __init__(self):
        self.device_map = {}

    def send_ac_command(self, hall_id: str, power: bool, temp: float, mode: str, fan_speed: str):
        payload = {
            "type": "AC",
            "power": 1 if power else 0,
            "target_temp": temp,
            "mode": mode.upper(),
            "fan_speed": fan_speed.upper()
        }
        logger.info(f"ESP32 Relay [Hall: {hall_id}] AC Dispatch: {payload}")
        mqtt_service.publish_command(hall_id, "ac", "UPDATE_STATE", payload)

    def send_fan_command(self, hall_id: str, power: bool, speed: int):
        payload = {
            "type": "FAN",
            "power": 1 if power else 0,
            "speed_level": speed
        }
        logger.info(f"ESP32 PWM [Hall: {hall_id}] Fan Dispatch: {payload}")
        mqtt_service.publish_command(hall_id, "fan", "UPDATE_SPEED", payload)

    def send_curtain_command(self, hall_id: str, position: int, action: str):
        payload = {
            "type": "CURTAIN",
            "target_position": position,
            "motor_action": action.upper()
        }
        logger.info(f"ESP32 Stepper [Hall: {hall_id}] Curtain Dispatch: {payload}")
        mqtt_service.publish_command(hall_id, "curtain", "SET_POSITION", payload)

esp32_client = ESP32Client()
