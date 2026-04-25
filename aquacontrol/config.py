from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/aquadb"
    NOTIFICATION_SERVICE_URL: str = "http://notifications:8001/notify"

    class Config:
        env_file = ".env"

settings = Settings()