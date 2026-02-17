from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, EscalationAction, MessageRole


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.MANAGER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# City Schemas
class CityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
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
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Bot Config Schemas
class BotConfigBase(BaseModel):
    system_prompt: Optional[str] = None
    greeting_message: Optional[str] = None
    manager_contact: Optional[str] = None
    esca