from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter(tags=["Analytics"])


@router.get("/cities/{city_id}/analytics")
def get_city_analytics(
    city_id: int,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for a city"""
    from app.dependencies.auth import get_user_cities
    
    accessible_city_ids = get_user_cities(current_user, db)
    if city_id not in accessible_city_ids:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this city"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total conversations
    total_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.city_id == city_id,
        Conversation.started_at >= start_date
    ).scalar()
    
    # Active conversations (not ended)
    active_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.city_id == city_id,
        Conversation.ended_at.is_(None)
    ).scalar()
    
    # Total messages
    total_messages = db.query(func.count(Message.id)).join(Conversation).filter(
        Conversation.city_id == city_id,
        Message.created_at >= start_date
    ).scalar()
    
    # Unique users
    unique_users = db.query(func.count(func.distinct(Conversation.user_telegram_id))).filter(
        Conversation.city_id == city_id,
        Conversation.started_at >= start_date
    ).scalar()
    
    # Average messages per conversation
    avg_messages = 0
    if total_conversations > 0:
        avg_messages = round(total_messages / total_conversations, 2)
    
    return {
        "city_id": city_id,
        "period_days": days,
        "total_conversations": total_conversations,
        "active_conversations": active_conversations,
        "total_messages": total_messages,
        "unique_users": unique_users,
        "avg_messages_per_conversation": avg_messages
    }
