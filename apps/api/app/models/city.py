from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    bot_token = Column(String, nullable=True)
    webhook_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    admins = relationship("CityAdmin", back_populates="city", cascade="all, delete-orphan")
    bot_config = relationship("BotConfig", back_populates="city", uselist=False, cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="city", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="city", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="city", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="city")


class CityAdmin(Base):
    __tablename__ = "city_admins"

    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    city = relationship("City", back_populates="admins")
    user = relationship("User", back_populates="city_admins")
