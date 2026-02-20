from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, JSON, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    user_telegram_id = Column(BigInteger, nullable=False, index=True)
    user_name = Column(String, nullable=True)
    product_sku = Column(String, nullable=True)
    reason = Column(String, nullable=False)  # "price_question", "availability", "complex_query", etc.
    conversation = Column(JSON, nullable=True)  # Full conversation history
    status = Column(String, default="pending", nullable=False)  # pending, contacted, resolved
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    city = relationship("City", back_populates="escalations")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
