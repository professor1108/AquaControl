import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, AsyncSessionLocal
from routers import status, sensors, control, devices, events
import tasks
from sqlalchemy import select
from models import Device
from metrics import MetricsMiddleware, get_metrics   # <-- добавлено
from logging_config import setup_logging             # <-- добавлено

# Настройка JSON-логирования
setup_logging("aquacontrol")

VERSION = "1.0.0"
app = FastAPI(title="AquaControl", version=VERSION)

# Middleware для сбора метрик запросов
app.add_middleware(MetricsMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(status.router)
app.include_router(sensors.router)
app.include_router(control.router)
app.include_router(devices.router)
app.include_router(events.router)

# Редирект с корня на статику
@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---- Эндпоинты для мониторинга ----
@app.get("/stats")
async def stats():
    return get_metrics(VERSION)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": VERSION}
# -----------------------------------

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

@app.get("/metrics")
async def metrics():
    return {"uptime": 12345, "version": VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
