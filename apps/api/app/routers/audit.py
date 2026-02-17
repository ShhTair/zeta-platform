from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import City, AuditLog
from app.schemas import AuditLogResponse
from app.dependencies import get_user_city_access

router = APIRouter(prefix="/cities/{city_id}", tags=["Audit"])


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    city: City = Depends(get_user_city_access),
    db: AsyncSession = Depends(get_db)
):
    """Get audit logs for a city"""
    
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.city_id == city.id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    logs = result.scalars().all()
    return logs
