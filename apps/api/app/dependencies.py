from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.models import User, City, CityAdmin, UserRole
from app.auth import get_current_user


async def get_user_city_access(
    city_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> City:
    """Verify user has access to the specified city"""
    
    # Super admins have access to all cities
    if current_user.role == UserRole.SUPER_ADMIN:
        result = await db.execute(select(City).where(City.id == city_id))
        city = result.scalar_one_or_none()
        if not city:
