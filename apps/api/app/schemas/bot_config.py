from pydantic import BaseModel
from typing import Optional
from app.models.bot_config import EscalationAction


class BotConfigBase(BaseModel):
    system_prompt: Optional[str] = None
    greeting_message: Optional[str] = None
    manager_contact: Optional[str] = None
    escalation_action: EscalationAction = EscalationAction.LOG_ONLY


class BotConfigCreate(BotConfigBase):
    city_id: int


class BotConfigUpdate(BaseModel):
    system_prompt: Optional[str] = None
    greeting_message: Optional[str] = None
    manager_contact: Optional[str] = None
    escalation_action: Optional[EscalationAction] = None


class BotConfigResponse(BotConfigBase):
    id: int
    city_id: int

    class Config:
        from_attributes = True
