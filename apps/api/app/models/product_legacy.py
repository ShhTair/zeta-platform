"""
Legacy Product Model - matches old ZETA bot database schema
37,318 furniture products imported from zeta-bot dump
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, ARRAY, JSON
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.core.database import Base


class ProductLegacy(Base):
    """Product model matching old zeta-bot schema (37k products)"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    sku = Column(Text, nullable=False, index=True)
    name = Column(Text, nullable=False, index=True)
    description = Column(Text)
    category = Column(Text, index=True)
    production_type = Column(Text)
    manufacturer = Column(Text)
    origin_country = Column(Text)
    material = Column(Text)
    color = Column(Text)
    dimensions = Column(JSONB)
    weight_capacity = Column(Integer)
    price = Column(Numeric(10, 2))
    price_currency = Column(String(3), default='KZT')
    images = Column(ARRAY(Text))
    primary_image = Column(Text)
    parent_sku = Column(Text)
    product_type = Column(Text, default='simple')
    created_at = Column(Text)  # Stored as text in old schema
    updated_at = Column(Text)
