from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class EscalationBase(BaseModel):
    city_id: int
    user_telegram_id: int
    user_name: Optional[str] = None
    product_sku: Optional[str] = None
    reason: str
    conversation: Optional[List[Dict]] = None


class EscalationCreate(EscalationBase):
    pass


class EscalationUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class EscalationResponse(EscalationBase):
    id: int
    status: str
    assigned_to: Optional[int]
    notes: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True
