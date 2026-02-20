from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class AnalyticsEventCreate(BaseModel):
    city_id: int
    event_type: str
    data: Optional[Dict] = None


class AnalyticsEventResponse(BaseModel):
    id: int
    city_id: int
    event_type: str
    data: Optional[Dict]
    created_at: datetime

    class Config:
        from_attributes = True
