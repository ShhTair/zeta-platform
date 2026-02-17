from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import User, City, Product, Category, AuditLog
from app.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryResponse
)
from app.dependencies import get_user_city_access
from app.auth import get_current_user

router = APIRouter(prefix="/cities/{city_id}", tags=["Products"])


@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    city: City = Depends(get_user_city_access),
    db: AsyncSession = Depends(get_db)
):
    """List all products for a city"""
    result = await db.execute(
        select(Product).where(Product.city_id == city.id)
    )
    products = result.scalars().all()
    return products


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    city: City = Depends(get_user_city_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new product"""
    
    # Verify category belongs to this city if provided
    if product_data.category_id:
        result = await db.execute(
            select(Category).where(
                Category.id == product_data.category_id,
                Category.city_id == city.id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found or does not belong to this city"
            )
    
    # Create product
    new_product = Product(**product_data.model_dump(), city_id=city.id)
    db.add(new_product)
    await db.flush()
    
    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        city_id=city.id,
        action="CREATE",
        table_name="products",
        record_id=new_product.id,
        new_value=product_data.model_dump()
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(new_product)
    
    return new_product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    city: City = Depends(get_user_city_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a product"""
    
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.city_id == city.id
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Verify category if being updated
    if product_data.category_id:
        result = await db.execute(
            select(Category).where(
                Category.id == product_data.category_id,
                Category.city_id == city.id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found or does not belong to this city"
            )
    
    # Store old values
    old_value = {
        "name": product.name,
        "description": product.description,
        "price": float(product.price) if product.price else None,
        "stock": product.stock,
        "sku": product.sku,
        "link": product.link,
        "category_id": product.category_id,
        "is_active": product.is_active
    }
    
    # Update fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        city_id=city.id,
        action="UPDATE",
        table_name="products",
        record_id=product.id,
        old_value=old_value,
        new_value=update_data
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(product)
    
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    city: City = Depends(get_user_city_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a product"""
    
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.city_id == city.id
        )
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        city_id=city.id,
        action="DELETE",
        table_name="products",
        record_id=product.id,
        old_value={"name": product.name, "sku": product.sku}
    )
    db.add(audit)
    
    await db.delete(product)
    await db.commit()
    
    return None


@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(
    city: City = Depends(get_user_city_access),
    db: AsyncSession = Depends(get_db)
):
    """List all categories for a city"""
    result = await db.execute(
        select(Category).where(Category.city_id == city.id)
    )
    categories = result.scalars().all()
    return categories


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    city: City = Depends(get_user_city_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new category"""
    
    # Verify parent category if provided
    if category_data.parent_id:
        result = await db.execute(
            select(Category).where(
                Category.id == category_data.parent_id,
                Category.city_id == city.id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found or does not belong to this city"
            )
    
    new_category = Category(**category_data.model_dump(), city_id=city.id)
    db.add(new_category)
    await db.flush()
    
    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        city_id=city.id,
        action="CREATE",
        table_name="categories",
        record_id=new_category.id,
        new_value=category_data.model_dump()
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(new_category)
    
    return new_category
