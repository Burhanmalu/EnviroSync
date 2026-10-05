import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.device import Device, DeviceEvent
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceCommand
from app.iot.device_controller import device_controller

class DeviceService:
    async def get_hall_devices(self, db: AsyncSession, hall_id: str) -> List[Device]:
        result = await db.execute(select(Device).where(Device.hall_id == hall_id))
        return list(result.scalars().all())

    async def get_device_by_id(self, db: AsyncSession, device_id: str) -> Optional[Device]:
        result = await db.execute(select(Device).where(Device.id == device_id))
        return result.scalars().first()

    async def update_device_state(
        self,
        db: AsyncSession,
        device_id: str,
        update_data: DeviceUpdate,
        source: str = "MANUAL"
    ) -> Optional[Device]:
        device = await self.get_device_by_id(db, device_id)
        if not device:
            return None

        if update_data.power is not None:
            device.power = update_data.power
        if update_data.control_mode is not None:
            device.control_mode = update_data.control_mode
        if update_data.status is not None:
            device.status = update_data.status
        if update_data.state is not None:
            new_state = dict(device.state or {})
            new_state.update(update_data.state)
            device.state = new_state

        device.last_command_time = datetime.now(timezone.utc)

        # Log event
        event = DeviceEvent(
            device_id=device.id,
            hall_id=device.hall_id,
            action="UPDATE_STATE",
            source=source,
            details=update_data.model_dump(exclude_unset=True)
        )
        db.add(event)
        await db.commit()
        await db.refresh(device)
        return device

    async def execute_command(
        self,
        db: AsyncSession,
        device_id: str,
        command: DeviceCommand,
        source: str = "MANUAL"
    ) -> Optional[Device]:
        device = await self.get_device_by_id(db, device_id)
        if not device:
            return None

        hall_id = device.hall_id
        action = command.action.upper()
        value = command.value

        if action == "RETURN_AUTO":
            device.control_mode = "AUTO"
            device.manual_override_until = None
            device_controller.return_to_auto(hall_id, device.type)
        elif device.type == "ac":
            if action in ["TURN_ON", "POWER_ON"]:
                device.power = True
                device.control_mode = "MANUAL"
                device_controller.turn_ac_on(hall_id, manual=True)
            elif action in ["TURN_OFF", "POWER_OFF"]:
                device.power = False
                device.control_mode = "MANUAL"
                device_controller.turn_ac_off(hall_id, manual=True)
            elif action == "SET_TEMP":
                temp = float(value)
                state = dict(device.state or {})
                state["target_temp"] = temp
                device.state = state
                device.control_mode = "MANUAL"
                device_controller.set_ac_temperature(hall_id, temp, manual=True)
            elif action == "SET_MODE":
                state = dict(device.state or {})
                state["mode"] = str(value).lower()
                device.state = state
                device.control_mode = "MANUAL"
                device_controller.set_ac_mode(hall_id, str(value), manual=True)
        elif device.type == "fan":
            if action in ["TURN_ON", "POWER_ON"]:
                device.power = True
                device.control_mode = "MANUAL"
                device_controller.turn_fan_on(hall_id, manual=True)
            elif action in ["TURN_OFF", "POWER_OFF"]:
                device.power = False
                device.control_mode = "MANUAL"
                device_controller.turn_fan_off(hall_id, manual=True)
            elif action == "SET_SPEED":
                spd = int(value)
                state = dict(device.state or {})
                state["speed"] = spd
                device.state = state
                device.power = spd > 0
                device.control_mode = "MANUAL"
                device_controller.set_fan_speed(hall_id, spd, manual=True)
        elif device.type == "curtain":
            if action == "OPEN":
                device_controller.open_curtain(hall_id, manual=True)
                device.state = {"position": 100, "state": "OPEN"}
            elif action == "CLOSE":
                device_controller.close_curtain(hall_id, manual=True)
                device.state = {"position": 0, "state": "CLOSED"}
            elif action == "STOP":
                device_controller.stop_curtain(hall_id, manual=True)
                device.state = {"position": 50, "state": "STOPPED"}
            elif action == "SET_POSITION":
                pos = int(value)
                device_controller.set_curtain_position(hall_id, pos, manual=True)
                device.state = {"position": pos, "state": "OPEN" if pos >= 95 else "CLOSED" if pos <= 5 else "PARTIAL"}

        event = DeviceEvent(
            device_id=device.id,
            hall_id=device.hall_id,
            action=action,
            source=source,
            details={"value": value}
        )
        db.add(event)
        await db.commit()
        await db.refresh(device)
        return device

device_service = DeviceService()
