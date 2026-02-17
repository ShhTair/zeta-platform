from pydantic import BaseModel
from typing import Optional


class CityBase(BaseModel):
    name: str
    slug: str
    bot_token: Optional[str] = None
    webhook_url: Optional[str] = None
    is_active: bool = True


class CityCreate(CityBase):
    pass


class CityUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    bot_token: Optional[str] = None
    webhook_url: Optional[str] = None
    is_active: Optional[bool] = None


class CityResponse(CityBase):
    id: int

    class Config:
        from_attributes = True
