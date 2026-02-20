from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String, nullable=False, index=True)  # "search", "escalation", "product_view", etc.
    data = Column(JSON, nullable=True)  # Event-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    city = relationship("City", back_populates="analytics_events")
