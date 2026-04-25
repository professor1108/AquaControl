from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    sensor_type = Column(String(50), index=True)
    value = Column(Float)
    unit = Column(String(20))

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    type = Column(String(50))
    status = Column(Boolean, default=False)
    power = Column(Float, nullable=True)
    mode = Column(String(50), nullable=True)
    target_temperature = Column(Float, nullable=True)   # новое поле

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    cron_expression = Column(String(100))
    action = Column(String(100))
    enabled = Column(Boolean, default=True)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    event_type = Column(String(50))
    source = Column(String(50))
    description = Column(Text)
    priority = Column(Integer)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(128))
    role = Column(String(20))
    email = Column(String(100))
    telegram_chat_id = Column(String(50), nullable=True)