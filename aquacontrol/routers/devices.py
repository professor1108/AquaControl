from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Device
from schemas import Device as DeviceSchema, DeviceCreate, EventCreate
from pydantic import BaseModel
import crud

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])

class DeviceStatusUpdate(BaseModel):
    status: bool

@router.get("/")
async def list_devices(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device))
    devices = result.scalars().all()
    return devices

@router.put("/{device_id}")
async def update_device(device_id: int, device_data: DeviceCreate, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.name = device_data.name
    device.type = device_data.type
    device.status = device_data.status
    device.power = device_data.power
    device.mode = device_data.mode
    await db.commit()
    return device

@router.patch("/{device_id}/status")
async def toggle_device(device_id: int, status_update: DeviceStatusUpdate, db: AsyncSession = Depends(get_db)):
    device = await db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    old_status = device.status
    device.status = status_update.status
    await db.commit()
    await db.refresh(device)

    # Логируем ручное изменение состояния
    action = "включено" if device.status else "выключено"
    event_desc = f"Устройство «{device.name}» {action} пользователем"
    event = EventCreate(
        event_type="info",
        source="user",
        description=event_desc,
        priority=2
    )
    await crud.create_event(db, event)

    return device