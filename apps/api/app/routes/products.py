from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.dependencies.auth import get_current_user, require_city_admin
from app.middleware.audit import create_audit_log

router = APIRouter(tags=["Products"])


@router.get("/cities/{city_id}/products", response_model=List[ProductResponse])
def list_products(
    city_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List products for a city"""
    from app.dependencies.auth import get_user_cities
    
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this city"
        )
    
    query = db.query(Product).filter(Product.city_id == city_id)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.post("/cities/{city_id}/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    city_id: int,
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product"""
    # Check access
    from app.dependencies.auth import get_user_cities
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this city"
        )
    
    product = Product(city_id=city_id, **product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    
    create_audit_log(
        db=db,
        user_id=current_user.id,
        city_id=city_id,
        action="CREATE",
        table_name="products",
        record_id=product.id,
        new_value=product_data.model_dump()
    )
    
    return product


@router.get("/cities/{city_id}/products/{product_id}", response_model=ProductResponse)
def get_product(
    city_id: int,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get product by ID"""
    from app.dependencies.auth import get_user_cities
    
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this city"
        )
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.city_id == city_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.put("/cities/{city_id}/products/{product_id}", response_model=ProductResponse)
def update_product(
    city_id: int,
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a product"""
    # Check access
    from app.dependencies.auth import get_user_cities
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this city"
        )
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.city_id == city_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    old_values = {
        "name": product.name,
        "price": float(product.price) if product.price else None,
        "stock": product.stock
    }
    
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    create_audit_log(
        db=db,
        user_id=current_user.id,
        city_id=city_id,
        action="UPDATE",
        table_name="products",
        record_id=product.id,
        old_value=old_values,
        new_value=update_data
    )
    
    return product


@router.delete("/cities/{city_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    city_id: int,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a product"""
    # Check access
    from app.dependencies.auth import get_user_cities
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this city"
        )
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.city_id == city_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    create_audit_log(
        db=db,
        user_id=current_user.id,
        city_id=city_id,
        action="DELETE",
        table_name="products",
        record_id=product.id,
        old_value={"name": product.name, "sku": product.sku}
    )
    
    db.delete(product)
    db.commit()
    
    return None
