from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import User, City, BotConfig, AuditLog, UserRole
from app.schemas import CityCreate, CityUpdate, CityResponse
from app.auth import require_role

router = APIRouter(prefix="/cities", tags=["Cities"])


async def log_audit(
    db: AsyncSession,
    user_id: int,
    city_id: int,
    action: str,
    table_name: str,
    record_id: int,
    old_value: dict = None,
    new_value: dict = None
):
    """Helper to log audit entries"""
    audit = AuditLog(
        user_id=user_id,
        city_id=city_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_value=old_value,
        new_value=new_value
    )
    db.add(audit)


@router.get("", response_model=List[CityResponse])
async def list_cities(
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """List all cities (Super Admin only)"""
    result = await db.execute(select(City))
    cities = result.scalars().all()
    return cities


@router.post("", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(
    city_data: CityCreate,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Create a new city (Super Admin only)"""
    
    # Check if slug already exists
    result = await db.execute(select(City).where(City.slug == city_data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City with this slug already exists"
        )
    
    # Create city
    new_city = City(**city_data.model_dump())
    db.add(new_city)
    await db.flush()
    
    # Create default bot config
    bot_config = BotConfig(
        city_id=new_city.id,
        updated_by=current_user.id
    )
    db.add(bot_config)
    
    # Log audit
    await log_audit(
        db, current_user.id, new_city.id, "CREATE", "cities", 
        new_city.id, new_value=city_data.model_dump()
    )
    
    await db.commit()
    await db.refresh(new_city)
    
    return new_city


@router.put("/{city_id}", response_model=CityResponse)
async def update_city(
    city_id: int,
    city_data: CityUpdate,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Update a city (Super Admin only)"""
    
    result = await db.execute(select(City).where(City.id == city_id))
    city = result.scalar_one_or_none()
    
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )
    
    # Store old values for audit
    old_value = {
        "name": city.name,
        "slug": city.slug,
        "bot_token": city.bot_token,
        "webhook_url": city.webhook_url,
        "is_active": city.is_active
    }
    
    # Update fields
    update_data = city_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(city, field, value)
    
    # Log audit
    await log_audit(
        db, current_user.id, city_id, "UPDATE", "cities",
        city_id, old_value=old_value, new_value=update_data
    )
    
    await db.commit()
    await db.refresh(city)
    
    return city


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_city(
    city_id: int,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Delete a city (Super Admin only)"""
    
    result = await db.execute(select(City).where(City.id == city_id))
    city = result.scalar_one_or_none()
    
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )
    
    # Log audit before deletion
    await log_audit(
        db, current_user.id, city_id, "DELETE", "cities",
        city_id, old_value={"name": city.name, "slug": city.slug}
    )
    
    await db.delete(city)
    await db.commit()
    
    return None
