from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import crud

router = APIRouter(prefix="/api/v1/status", tags=["status"])

@router.get("/")
async def get_status(db: AsyncSession = Depends(get_db)):
    latest = await crud.get_latest_sensor_readings(db)
    return {"status": "ok", "sensors": latest}