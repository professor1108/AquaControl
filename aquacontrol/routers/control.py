from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Device
import crud
import schemas
from dependencies import send_notification

router = APIRouter(prefix="/api/v1/control", tags=["control"])

class TemperatureTarget(BaseModel):
    target: float

class FeedingPortion(BaseModel):
    portion: float

class LightMode(BaseModel):
    mode: str

@router.post("/temperature")
async def set_temperature(
    target: TemperatureTarget,
    db: AsyncSession = Depends(get_db)
):
    heater = (await db.execute(select(Device).where(Device.name == "Нагреватель"))).scalar_one_or_none()
    if not heater:
        raise HTTPException(status_code=404, detail="Нагреватель не найден")

    # Сохраняем целевую температуру как порог для тревог
    heater.target_temperature = target.target
    await db.commit()

    event_desc = f"Установлен порог температуры {target.target}°C — при превышении будет выдана экстренная ситуация"
    event = schemas.EventCreate(
        event_type="info",
        source="user",
        description=event_desc,
        priority=2
    )
    await crud.create_event(db, event)
    return {"status": "ok", "target": target.target}

@router.post("/feeding")
async def feed(
    portion: FeedingPortion,
    db: AsyncSession = Depends(get_db)
):
    feeder = (await db.execute(select(Device).where(Device.name == "Кормушка"))).scalar_one_or_none()
    if not feeder:
        raise HTTPException(status_code=404, detail="Кормушка не найдена")

    feeder.status = True
    feeder.power = portion.portion
    await db.commit()

    event_desc = f"Ручное кормление порцией {portion.portion} г"
    event = schemas.EventCreate(
        event_type="info",
        source="user",
        description=event_desc,
        priority=2
    )
    await crud.create_event(db, event)
    await send_notification("feeding", event_desc)

    import asyncio
    from database import AsyncSessionLocal
    async def reset_feeder():
        await asyncio.sleep(5)
        async with AsyncSessionLocal() as session:
            feeder = await session.get(Device, feeder.id)
            if feeder:
                feeder.status = False
                await session.commit()
    asyncio.create_task(reset_feeder())

    return {"status": "feeding triggered", "portion": portion.portion}

@router.post("/light/mode")
async def set_light_mode(
    light_mode: LightMode,
    db: AsyncSession = Depends(get_db)
):
    light = (await db.execute(select(Device).where(Device.name == "Освещение"))).scalar_one_or_none()
    if not light:
        raise HTTPException(status_code=404, detail="Освещение не найдено")

    old_mode = light.mode
    light.mode = light_mode.mode

    status_map = {"day": True, "night": False, "storm": True, "plant_growth": True}
    new_status = status_map.get(light_mode.mode, False)
    light.status = new_status
    await db.commit()

    event_desc = f"Режим освещения изменён с '{old_mode}' на '{light_mode.mode}' (питание: {'вкл' if new_status else 'выкл'})"
    event = schemas.EventCreate(
        event_type="info",
        source="user",
        description=event_desc,
        priority=2
    )
    await crud.create_event(db, event)
    return {"status": "ok", "mode": light_mode.mode, "power": new_status}