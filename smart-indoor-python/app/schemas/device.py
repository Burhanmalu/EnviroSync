from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class DeviceBase(BaseModel):
    name: str
    type: str  # "ac", "fan", "curtain"
    status: str = "ONLINE"
    power: bool = False
    control_mode: str = "AUTO"  # "AUTO", "MANUAL"
    state: Dict[str, Any] = {}

class DeviceCreate(DeviceBase):
    id: str
    hall_id: str

class DeviceUpdate(BaseModel):
    power: Optional[bool] = None
    control_mode: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class DeviceCommand(BaseModel):
    action: str  # "SET_POWER", "SET_TEMP", "SET_MODE", "SET_SPEED", "SET_POSITION", "RETURN_AUTO"
    value: Optional[Any] = None

class DeviceResponse(DeviceBase):
    id: str
    hall_id: str
    manual_override_until: Optional[datetime] = None
    last_command_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class HallDevicesState(BaseModel):
    hall_id: str
    ac: Dict[str, Any]
    fan: Dict[str, Any]
    curtain: Dict[str, Any]
    devices: list[DeviceResponse] = []
