"""
Public Products API - No authentication required (for bot)
Provides search endpoint for ZETA Telegram Bot
Uses legacy product schema (37,318 products from old zeta-bot)
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from app.core.database import get_db
from app.models.product_legacy import ProductLegacy
from pydantic import BaseModel

router = APIRouter(prefix="/api/products", tags=["Products (Public)"])


class ProductSearchResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    price: Optional[float] = None
    primary_image: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/search", response_model=List[ProductSearchResponse])
def search_products(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    Search products by name, description, SKU, or category.
    Public endpoint - no authentication required.
    
    Example: /api/products/search?q=кресло&limit=10
    """
    
    # Build search query
    search_term = f"%{q.lower()}%"
    
    query = db.query(ProductLegacy).filter(
        or_(
            func.lower(ProductLegacy.name).like(search_term),
            func.lower(ProductLegacy.description).like(search_term),
            func.lower(ProductLegacy.sku).like(search_term),
            func.lower(ProductLegacy.category).like(search_term),
            func.lower(ProductLegacy.material).like(search_term),
            func.lower(ProductLegacy.color).like(search_term),
        )
    ).limit(limit).offset(offset)
    
    products = query.all()
    
    return products


@router.get("/{product_id}", response_model=ProductSearchResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get product details by ID.
    Public endpoint - no authentication required.
    """
    
    product = db.query(ProductLegacy).filter(ProductLegacy.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product
