from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database import get_db
from models import Event
from schemas import Event as EventSchema

router = APIRouter(prefix="/api/v1/events", tags=["events"])

@router.get("/")
async def get_events(limit: int = 100, db: AsyncSession = Depends(get_db)):
    stmt = select(Event).order_by(desc(Event.timestamp)).limit(limit)
    result = await db.execute(stmt)
    events = result.scalars().all()
    return events