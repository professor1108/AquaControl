import os
import socket
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from metrics import MetricsMiddleware, get_metrics
from logging_config import setup_logging

# Настройка логирования
setup_logging("notifications")
VERSION = "1.0.0"

app = FastAPI(title="Notification Service", version=VERSION)
app.add_middleware(MetricsMiddleware)

logger = logging.getLogger(__name__)


class Notification(BaseModel):
    event_type: str
    description: str


@app.post("/notify")
async def notify(notification: Notification):
    # Получаем имя узла через socket (надёжнее, чем переменная окружения)
    node = socket.gethostname()
    logger.info(f"Received notification: {notification.event_type} - {notification.description}")
    return {"status": "delivered", "node": node}


@app.get("/stats")
async def stats():
    return get_metrics(VERSION)


@app.get("/health")
async def health():
    return {"status": "ok", "version": VERSION, "node": socket.gethostname()}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
    uvicorn.run(app, host="0.0.0.0", port=8001)
