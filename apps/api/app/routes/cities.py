from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.city import City
from app.models.user import User
from app.schemas.city import CityCreate, CityUpdate, CityResponse
from app.dependencies.auth import get_current_user, require_super_admin
from app.middleware.audit import create_audit_log

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("", response_model=List[CityResponse])
def list_cities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all cities (super admin only gets all, city admins see their cities)"""
    from app.dependencies.auth import get_user_cities
    
    accessible_city_ids = get_user_cities(current_user, db)
    cities = db.query(City).filter(City.id.in_(accessible_city_ids)).all()
    
    return cities


@router.post("", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
def create_city(
    city_data: CityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Create a new city (super admin only)"""
    # Check if slug already exists
    existing = db.query(City).filter(City.slug == city_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City with this slug already exists"
        )
    
    city = City(**city_data.model_dump())
    db.add(city)
    db.commit()
    db.refresh(city)
    
    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        city_id=city.id,
        action="CREATE",
        table_name="cities",
        record_id=city.id,
        new_value=city_data.model_dump()
    )
    
    return city


@router.get("/{city_id}", response_model=CityResponse)
def get_city(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get city by ID"""
    from app.dependencies.auth import get_user_cities
    
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this city"
        )
    
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )
    
    return city


@router.put("/{city_id}", response_model=CityResponse)
def update_city(
    city_id: int,
    city_data: CityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Update city (super admin only)"""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )
    
    old_values = {
        "name": city.name,
        "slug": city.slug,
        "is_active": city.is_active
    }
    
    # Update fields
    update_data = city_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(city, field, value)
    
    db.commit()
    db.refresh(city)
    
    # Audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        city_id=city.id,
        action="UPDATE",
        table_name="cities",
        record_id=city.id,
        old_value=old_values,
        new_value=update_data
    )
    
    return city


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin)
):
    """Delete city (super admin only)"""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )
    
    # Audit log before deletion
    create_audit_log(
        db=db,
        user_id=current_user.id,
        city_id=city.id,
        action="DELETE",
        table_name="cities",
        record_id=city.id,
        old_value={"name": city.name, "slug": city.slug}
    )
    
    db.delete(city)
    db.commit()
    
    return None
