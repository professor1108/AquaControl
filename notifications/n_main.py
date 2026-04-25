from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service", version="1.0")

class Notification(BaseModel):
    event_type: str
    description: str

@app.post("/notify")
async def notify(notification: Notification):
    # В реальном проекте здесь отправка Telegram/email/SMS
    logger.info(f"Received notification: {notification.event_type} - {notification.description}")
    # Имитация отправки (всегда успешно)
    return {"status": "delivered"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)