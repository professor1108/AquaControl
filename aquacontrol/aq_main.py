import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse          # ← добавлен импорт
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, AsyncSessionLocal
from routers import status, sensors, control, devices, events
import tasks
from sqlalchemy import select
from models import Device

app = FastAPI(title="AquaControl", version="1.0")

# Настройка CORS
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

# ---------- Добавленный обработчик корневого пути ----------
@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")
# ----------------------------------------------------------

# Статические файлы (фронтенд)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Предварительное создание устройств, если их нет
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

    # Запуск фоновой симуляции датчиков
    asyncio.create_task(tasks.simulate_sensors())

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    return {"uptime": 12345, "version": "1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
