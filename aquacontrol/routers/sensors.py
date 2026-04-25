from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from database import get_db
from models import SensorReading
from schemas import SensorReading as SensorReadingSchema
import crud

router = APIRouter(prefix="/api/v1/sensors", tags=["sensors"])

@router.get("/")
async def list_sensors(db: AsyncSession = Depends(get_db)):
    latest = await crud.get_latest_sensor_readings(db)
    return latest

@router.get("/{sensor_type}/history")
async def get_history(sensor_type: str, from_date: datetime = Query(None), to_date: datetime = Query(None), db: AsyncSession = Depends(get_db)):
    query = select(SensorReading).where(SensorReading.sensor_type == sensor_type).order_by(desc(SensorReading.timestamp)).limit(100)
    if from_date:
        query = query.where(SensorReading.timestamp >= from_date)
    if to_date:
        query = query.where(SensorReading.timestamp <= to_date)
    result = await db.execute(query)
    readings = result.scalars().all()
    return readings