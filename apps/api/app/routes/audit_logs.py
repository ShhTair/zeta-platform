from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.dependencies.auth import get_current_user

router = APIRouter(tags=["Audit Logs"])


@router.get("/cities/{city_id}/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    city_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action: Optional[str] = None,
    table_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit logs for a city"""
    from app.dependencies.auth import get_user_cities
    
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this city"
        )
    
    query = db.query(AuditLog).filter(AuditLog.city_id == city_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if table_name:
        query = query.filter(AuditLog.table_name == table_name)
    
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return logs
