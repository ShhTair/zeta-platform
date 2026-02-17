from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.models.city import City, CityAdmin

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def require_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


async def require_city_admin(
    city_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    # Super admins have access to all cities
    if current_user.role == UserRole.SUPER_ADMIN:
        return current_user
    
    # Check if user is admin of this specific city
    city_admin = db.query(CityAdmin).filter(
        CityAdmin.city_id == city_id,
        CityAdmin.user_id == current_user.id
    ).first()
    
    if city_admin is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="City admin access required"
        )
    
    return current_user


def get_user_cities(user: User, db: Session) -> list[int]:
    """Get list of city IDs the user has access to"""
    if user.role == UserRole.SUPER_ADMIN:
        return [city.id for city in db.query(City).all()]
    
    return [ca.city_id for ca in db.query(CityAdmin).filter(CityAdmin.user_id == user.id).all()]
