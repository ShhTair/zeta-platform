from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.escalation import Escalation
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.middleware.audit import create_audit_log


router = APIRouter(tags=["Escalations"])


# Schemas
class EscalationCreate(BaseModel):
    city_id: int
    user_telegram_id: int
    user_name: Optional[str] = None
    product_sku: Optional[str] = None
    reason: str
    conversation: Optional[list] = None


class EscalationUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class EscalationResponse(BaseModel):
    id: int
    city_id: int
    user_telegram_id: int
    user_name: Optional[str]
    product_sku: Optional[str]
    reason: str
    conversation: Optional[list]
    status: str
    assigned_to: Optional[int]
    notes: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/escalations", response_model=EscalationResponse, status_code=status.HTTP_201_CREATED)
def create_escalation(
    escalation_data: EscalationCreate,
    db: Session = Depends(get_db)
):
    """Create a new escalation (called by bot - no auth required for now)"""
    escalation = Escalation(**escalation_data.model_dump())
    db.add(escalation)
    db.commit()
    db.refresh(escalation)
    return escalation


@router.get("/cities/{city_id}/escalations", response_model=List[EscalationResponse])
def get_city_escalations(
    city_id: int,
    status_filter: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get escalations for a city"""
    from app.dependencies.auth import get_user_cities
    
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this city"
        )
    
    query = db.query(Escalation).filter(Escalation.city_id == city_id)
    
    if status_filter:
        query = query.filter(Escalation.status == status_filter)
    
    escalations = query.order_by(desc(Escalation.created_at)).limit(limit).all()
    return escalations


@router.get("/escalations/{escalation_id}", response_model=EscalationResponse)
def get_escalation(
    escalation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single escalation"""
    escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    from app.dependencies.auth import get_user_cities
    accessible_city_ids = get_user_cities(current_user, db)
    if escalation.city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return escalation


@router.put("/escalations/{escalation_id}", response_model=EscalationResponse)
def update_escalation(
    escalation_id: int,
    update_data: EscalationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update escalation status, assignment, or notes"""
    escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    from app.dependencies.auth import get_user_cities
    accessible_city_ids = get_user_cities(current_user, db)
    if escalation.city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    old_values = {
        "status": escalation.status,
        "assigned_to": escalation.assigned_to,
        "notes": escalation.notes
    }
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(escalation, field, value)
    
    # Mark as resolved if status changed to "resolved"
    if update_data.status == "resolved" and escalation.resolved_at is None:
        escalation.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(escalation)
    
    create_audit_log(
        db=db,
        user_id=current_user.id,
        city_id=escalation.city_id,
        action="UPDATE",
        table_name="escalations",
        record_id=escalation.id,
        old_value=old_values,
        new_value=update_dict
    )
    
    return escalation


@router.delete("/escalations/{escalation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_escalation(
    escalation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an escalation"""
    escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation not found"
        )
    
    from app.dependencies.auth import get_user_cities
    accessible_city_ids = get_user_cities(current_user, db)
    if escalation.city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    create_audit_log(
        db=db,
        user_id=current_user.id,
        city_id=escalation.city_id,
        action="DELETE",
        table_name="escalations",
        record_id=escalation.id,
        old_value={
            "user_telegram_id": escalation.user_telegram_id,
            "reason": escalation.reason
        }
    )
    
    db.delete(escalation)
    db.commit()
