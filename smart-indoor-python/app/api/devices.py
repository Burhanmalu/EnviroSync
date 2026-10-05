from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.device import DeviceResponse, DeviceUpdate, DeviceCommand, HallDevicesState
from app.services.device_service import device_service
from app.iot.device_controller import device_controller
from app.realtime.manager import connection_manager

router = APIRouter(tags=["Devices"])

@router.get("/halls/{id}/devices", response_model=List[DeviceResponse])
async def get_hall_devices(id: str, db: AsyncSession = Depends(get_db)):
    devices = await device_service.get_hall_devices(db, id)
    return [DeviceResponse.model_validate(d) for d in devices]

@router.get("/halls/{id}/devices/state", response_model=HallDevicesState)
async def get_hall_devices_state(id: str, db: AsyncSession = Depends(get_db)):
    devices = await device_service.get_hall_devices(db, id)
    cached = device_controller.get_state(id)
    return HallDevicesState(
        hall_id=id,
        ac=cached.get("ac", {}),
        fan=cached.get("fan", {}),
        curtain=cached.get("curtain", {}),
        devices=[DeviceResponse.model_validate(d) for d in devices]
    )

@router.put("/devices/{id}", response_model=DeviceResponse)
async def update_device(
    id: str,
    payload: DeviceUpdate,
    db: AsyncSession = Depends(get_db)
):
    device = await device_service.update_device_state(db, id, payload, source="MANUAL")
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Broadcast device update
    await connection_manager.broadcast_to_hall(device.hall_id, {
        "event_type": "device_update",
        "hall_id": device.hall_id,
        "data": DeviceResponse.model_validate(device).model_dump(mode="json")
    })

    return DeviceResponse.model_validate(device)

@router.post("/devices/{id}/command", response_model=DeviceResponse)
async def execute_device_command(
    id: str,
    command: DeviceCommand,
    db: AsyncSession = Depends(get_db)
):
    device = await device_service.execute_command(db, id, command, source="MANUAL")
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Broadcast device update
    await connection_manager.broadcast_to_hall(device.hall_id, {
        "event_type": "device_update",
        "hall_id": device.hall_id,
        "data": DeviceResponse.model_validate(device).model_dump(mode="json")
    })

    return DeviceResponse.model_validate(device)
