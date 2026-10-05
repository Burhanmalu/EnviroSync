import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from app.iot.esp32_client import esp32_client

logger = logging.getLogger("smart_indoor.device_controller")

class DeviceController:
    """
    Actuator state and command dispatcher.
    Handles AC, Fan, and Curtains with state caching and hardware dispatch.
    """

    def __init__(self):
        # In-memory device cache indexed by hall_id
        self._states: Dict[str, Dict[str, Any]] = {}

    def _get_hall_state(self, hall_id: str) -> Dict[str, Any]:
        if hall_id not in self._states:
            self._states[hall_id] = {
                "ac": {
                    "power": True,
                    "target_temp": 24.0,
                    "current_temp": 25.5,
                    "mode": "cool",
                    "fan_speed": "auto",
                    "control_mode": "AUTO",
                    "manual_until": None
                },
                "fan": {
                    "power": True,
                    "speed": 2,
                    "oscillation": False,
                    "control_mode": "AUTO",
                    "manual_until": None
                },
                "curtain": {
                    "position": 50,
                    "state": "PARTIAL",
                    "control_mode": "AUTO",
                    "manual_until": None
                }
            }
        return self._states[hall_id]

    # --- AC METHODS ---
    def turn_ac_on(self, hall_id: str, manual: bool = False):
        state = self._get_hall_state(hall_id)["ac"]
        state["power"] = True
        if manual:
            state["control_mode"] = "MANUAL"
            state["manual_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)
        esp32_client.send_ac_command(hall_id, True, state["target_temp"], state["mode"], state["fan_speed"])
        return state

    def turn_ac_off(self, hall_id: str, manual: bool = False):
        state = self._get_hall_state(hall_id)["ac"]
        state["power"] = False
        if manual:
            state["control_mode"] = "MANUAL"
            state["manual_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)
        esp32_client.send_ac_command(hall_id, False, state["target_temp"], state["mode"], state["fan_speed"])
        return state

    def set_ac_temperature(self, hall_id: str, temp: float, manual: bool = False):
        state = self._get_hall_state(hall_id)["ac"]
        state["target_temp"] = max(16.0, min(30.0, temp))
        if manual:
            state["control_mode"] = "MANUAL"
            state["manual_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)
        esp32_client.send_ac_command(hall_id, state["power"], state["target_temp"], state["mode"], state["fan_speed"])
        return state

    def set_ac_mode(self, hall_id: str, mode: str, manual: bool = False):
        state = self._get_hall_state(hall_id)["ac"]
        state["mode"] = mode.lower()
        if manual:
            state["control_mode"] = "MANUAL"
            state["manual_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)
        esp32_client.send_ac_command(hall_id, state["power"], state["target_temp"], state["mode"], state["fan_speed"])
        return state

    # --- FAN METHODS ---
    def turn_fan_on(self, hall_id: str, manual: bool = False):
        state = self._get_hall_state(hall_id)["fan"]
        state["power"] = True
        if state["speed"] == 0:
            state["speed"] = 2
        if manual:
            state["control_mode"] = "MANUAL"
            state["manual_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)
        esp32_client.send_fan_command(hall_id, True, state["speed"])
        return state

    def turn_fan_off(self, hall_id: str, manual: bool = False):
        state = self._get_hall_state(hall_id)["fan"]
        state["power"] = False
        state["speed"] = 0
        if manual:
            state["control_mode"] = "MANUAL"
            state["manual_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)
        esp32_client.send_fan_command(hall_id, False, 0)
        return state

    def set_fan_speed(self, hall_id: str, speed: int, manual: bool = False):
        state = self._get_hall_state(hall_id)["fan"]
        state["speed"] = max(0, min(5, speed))
        state["power"] = state["speed"] > 0
        if manual:
            state["control_mode"] = "MANUAL"
            state["manual_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)
        esp32_client.send_fan_command(hall_id, state["power"], state["speed"])
        return state

    # --- CURTAIN METHODS ---
    def open_curtain(self, hall_id: str, manual: bool = False):
        return self.set_curtain_position(hall_id, 100, manual=manual)

    def close_curtain(self, hall_id: str, manual: bool = False):
        return self.set_curtain_position(hall_id, 0, manual=manual)

    def stop_curtain(self, hall_id: str, manual: bool = False):
        state = self._get_hall_state(hall_id)["curtain"]
        state["state"] = "STOPPED"
        if manual:
            state["control_mode"] = "MANUAL"
            state["manual_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)
        esp32_client.send_curtain_command(hall_id, state["position"], "STOP")
        return state

    def set_curtain_position(self, hall_id: str, position: int, manual: bool = False):
        state = self._get_hall_state(hall_id)["curtain"]
        pos = max(0, min(100, position))
        state["position"] = pos
        state["state"] = "OPEN" if pos >= 95 else "CLOSED" if pos <= 5 else "PARTIAL"
        if manual:
            state["control_mode"] = "MANUAL"
            state["manual_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)
        esp32_client.send_curtain_command(hall_id, pos, state["state"])
        return state

    def return_to_auto(self, hall_id: str, device_type: Optional[str] = None):
        hall_state = self._get_hall_state(hall_id)
        if device_type:
            d = device_type.lower()
            if d in hall_state:
                hall_state[d]["control_mode"] = "AUTO"
                hall_state[d]["manual_until"] = None
        else:
            for d in ["ac", "fan", "curtain"]:
                hall_state[d]["control_mode"] = "AUTO"
                hall_state[d]["manual_until"] = None
        return hall_state

    def get_state(self, hall_id: str) -> Dict[str, Any]:
        return self._get_hall_state(hall_id)

device_controller = DeviceController()
