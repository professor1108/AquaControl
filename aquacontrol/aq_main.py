import asyncio
import os
import time
import aiohttp
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, AsyncSessionLocal
from routers import status, sensors, control, devices, events
import tasks
from sqlalchemy import select
from models import Device
from metrics import MetricsMiddleware, get_metrics
from logging_config import setup_logging

setup_logging("aquacontrol")
VERSION = "1.0.0"

app = FastAPI(title="AquaControl", version=VERSION)
app.add_middleware(MetricsMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status.router)
app.include_router(sensors.router)
app.include_router(control.router)
app.include_router(devices.router)
app.include_router(events.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/stats")
async def stats():
    return get_metrics(VERSION)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": VERSION}

# Фоновая отправка метрик в Elasticsearch
async def send_stats_to_elastic():
    es_host = os.getenv("ES_HOST", "http://elasticsearch:9200")
    while True:
        await asyncio.sleep(30)
        data = get_metrics(VERSION)
        data['timestamp'] = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(f"{es_host}/aquacontrol-stats/_doc", json=data)
        except Exception as e:
            print(f"Failed to send stats to ES: {e}")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        devices_list = [
            ("Нагреватель", "heater"),
            ("Фильтр", "filter"),
            ("Кормушка", "feeder"),
            ("Освещение", "light"),
            ("Аэратор", "aerator")
        ]
        for name, dtype in devices_list:
            exists = (await db.execute(select(Device).where(Device.name == name))).scalar_one_or_none()
            if not exists:
                dev = Device(name=name, type=dtype, status=False, power=None, mode=None)
                db.add(dev)
        await db.commit()

    asyncio.create_task(tasks.simulate_sensors())
    asyncio.create_task(send_stats_to_elastic())

@app.get("/metrics")
async def metrics():
    return {"uptime": 12345, "version": VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
