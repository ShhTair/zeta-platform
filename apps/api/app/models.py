from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    Text, Numeric, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    CITY_ADMIN = "city_admin"
    MANAGER = "manager"


class EscalationAction(str, enum.Enum):
    LINK = "link"
    NOTIFY = "notify"
    BITRIX = "bitrix"


class MessageRole(str, enum.Enum):
    USER = "user"
    BOT = "bot"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.MANAGER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    city_admins = relationship("CityAdmin", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    user = relationship("User", back_populates="sessions")


class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    bot_token = Column(String(255), nullable=True)
    webhook_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    city_admins = relationship("CityAdmin", back_populates="city", cascade="all, delete-orphan")
    bot_config = relationship("BotConfig", back_populates="city", uselist=False, cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="city", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="city", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="city", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="city", cascade="all, delete-orphan")


class CityAdmin(Base):
    __tablename__ = "city_admins"
    
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    
    city = relationship("City", back_populates="city_admins")
    user = relationship("User", back_populates="city_admins")


class BotConfig(Base):
    __tablename__ = "bot_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), unique=True, nullable=False)
    system_prompt = Column(Text, nullable=True)
    greeting_message = Column(Text, nullable=True)
    manager_contact = Column(String(255), nullable=True)
    escalation_action = Column(SQLEnum(EscalationAction), default=EscalationAction.LINK)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    city = relationship("City", back_populates="bot_config")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    
    city = relationship("City", back_populates="categories")
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    stock = Column(Integer, default=0)
    sku = Column(String(100), nullable=True)
    link = Column(String(512), nullable=T