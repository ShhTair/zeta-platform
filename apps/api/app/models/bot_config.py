from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class EscalationAction(str, enum.Enum):
    NOTIFY = "notify"
    TRANSFER = "transfer"
    LOG_ONLY = "log_only"


class BotConfig(Base):
    __tablename__ = "bot_configs"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), unique=True, nullable=False)
    system_prompt = Column(Text, nullable=True)
    greeting_message = Column(Text, nullable=True)
    manager_contact = Column(String, nullable=True)
    escalation_action = Column(Enum(EscalationAction), default=EscalationAction.LOG_ONLY, nullable=False)

    # Relationships
    city = relationship("City", back_populates="bot_config")
