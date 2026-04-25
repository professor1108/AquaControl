from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import models
import schemas

async def create_sensor_reading(db: AsyncSession, reading: schemas.SensorReadingCreate):
    db_reading = models.SensorReading(**reading.dict())
    db.add(db_reading)
    await db.commit()
    await db.refresh(db_reading)
    return db_reading

async def get_latest_sensor_readings(db: AsyncSession):
    types = ['temperature', 'ph', 'ammonia', 'oxygen', 'turbidity']
    result = {}
    for t in types:
        stmt = select(models.SensorReading).where(models.SensorReading.sensor_type == t).order_by(desc(models.SensorReading.timestamp)).limit(1)
        reading = (await db.execute(stmt)).scalar_one_or_none()
        if reading:
            result[t] = reading.value
    return result

async def create_event(db: AsyncSession, event: schemas.EventCreate):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event