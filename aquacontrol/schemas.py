from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SensorReadingBase(BaseModel):
    sensor_type: str
    value: float
    unit: str

class SensorReadingCreate(SensorReadingBase):
    pass

class SensorReading(SensorReadingBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class DeviceBase(BaseModel):
    name: str
    type: str
    status: bool
    power: Optional[float] = None
    mode: Optional[str] = None
    target_temperature: Optional[float] = None   # новое поле

class DeviceCreate(DeviceBase):
    pass

class Device(DeviceBase):
    id: int

    class Config:
        from_attributes = True

class ScheduleBase(BaseModel):
    device_id: int
    cron_expression: str
    action: str
    enabled: bool = True

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int

    class Config:
        from_attributes = True

class EventBase(BaseModel):
    event_type: str
    source: str
    description: str
    priority: int

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True