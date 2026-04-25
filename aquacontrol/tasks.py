import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import AsyncSessionLocal
from models import Device
import crud
import schemas
from dependencies import send_notification

# Пороговые значения по умолчанию для тревог
DEFAULT_THRESHOLDS = {
    "ammonia": 0.5,
    "ph": (6.0, 8.5),
    "oxygen": 4.0,
    "turbidity": 10.0,
}

async def check_alarms(db: AsyncSession, sensor_type: str, value: float):
    alarm = False
    desc = ""

    if sensor_type == "temperature":
        # Получаем порог из устройства "Нагреватель"
        heater = (await db.execute(select(Device).where(Device.name == "Нагреватель"))).scalar_one_or_none()
        threshold = heater.target_temperature if (heater and heater.target_temperature is not None) else 30.0
        if value > threshold:
            alarm = True
            desc = f"Температура {value:.1f}°C превышает установленный порог {threshold}°C"

    elif sensor_type == "ph":
        low, high = DEFAULT_THRESHOLDS["ph"]
        if value < low:
            alarm = True
            desc = f"Критически низкий pH: {value:.2f}"
        elif value > high:
            alarm = True
            desc = f"Критически высокий pH: {value:.2f}"

    elif sensor_type == "ammonia":
        threshold = DEFAULT_THRESHOLDS["ammonia"]
        if value > threshold:
            alarm = True
            desc = f"Высокий уровень аммиака: {value:.2f} мг/л"

    elif sensor_type == "oxygen":
        threshold = DEFAULT_THRESHOLDS["oxygen"]
        if value < threshold:
            alarm = True
            desc = f"Низкий уровень кислорода: {value:.1f} мг/л"

    elif sensor_type == "turbidity":
        threshold = DEFAULT_THRESHOLDS["turbidity"]
        if value > threshold:
            alarm = True
            desc = f"Высокая мутность: {value:.1f} NTU"

    if alarm:
        # Событие тревоги
        event = schemas.EventCreate(
            event_type="alarm",
            source="simulator",
            description=desc,
            priority=1
        )
        await crud.create_event(db, event)
        await send_notification("alarm", desc)

        # Автоматическое управление приборами
        if sensor_type == "temperature":
            heater = (await db.execute(select(Device).where(Device.name == "Нагреватель"))).scalar_one_or_none()
            if heater and heater.status:
                heater.status = False
                await db.commit()
                auto_event = schemas.EventCreate(
                    event_type="auto",
                    source="system",
                    description="Автоматическое отключение нагревателя из-за превышения порога температуры",
                    priority=1
                )
                await crud.create_event(db, auto_event)

        elif sensor_type in ("ammonia", "turbidity"):
            filter_device = (await db.execute(select(Device).where(Device.name == "Фильтр"))).scalar_one_or_none()
            if filter_device and not filter_device.status:
                filter_device.status = True
                await db.commit()
                auto_event = schemas.EventCreate(
                    event_type="auto",
                    source="system",
                    description=f"Автоматическое включение фильтра из-за высокого уровня {sensor_type}",
                    priority=1
                )
                await crud.create_event(db, auto_event)

async def simulate_sensors():
    while True:
        await asyncio.sleep(10)
        async with AsyncSessionLocal() as db:
            readings = {
                "temperature": random.uniform(24.0, 31.0),
                "ph": random.uniform(5.5, 9.0),
                "ammonia": random.uniform(0.0, 0.8),
                "oxygen": random.uniform(3.0, 8.0),
                "turbidity": random.uniform(0.0, 12.0)
            }
            for sensor_type, value in readings.items():
                unit_map = {
                    "temperature": "°C",
                    "ph": "pH",
                    "ammonia": "мг/л",
                    "oxygen": "мг/л",
                    "turbidity": "NTU"
                }
                reading = schemas.SensorReadingCreate(
                    sensor_type=sensor_type,
                    value=value,
                    unit=unit_map.get(sensor_type, "")
                )
                await crud.create_sensor_reading(db, reading)
                await check_alarms(db, sensor_type, value)