from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import redis.asyncio as redis

from app.database import get_db
from app.models import User, City, BotConfig, Conversation, Message, AuditLog
from app.schemas import BotConfigUpdate, BotConfigResponse, AnalyticsResponse, ConversationStats
from app.dependencies import get_user_city_access
from app.config import settings
from app.auth import get_current_user

router = APIRouter(prefix="/cities/{city_id}", tags=["Bot Configuration"])


async def invalidate_cache(city_id: int):
    """Invalidate Redis cache for bot config"""
    try:
        r = redis.from_url(settings.REDIS_URL)
        await r.delete(f"bot_config:{city_id}")
        await r.close()
    except Exception:
        pass  # Cache is optional


@router.get("/config", response_model=BotConfigResponse)
async def get_bot_config(
    city: City = Depends(get_user_city_access),
    db: AsyncSession = Depends(get_db)
):
    """Get bot configuration for a city"""
    
    # Try to get from cache first
    try:
        r = redis.from_url(settings.REDIS_URL)
        cached = await r.get(f"bot_config:{city.id}")
        await r.close()
        
        if cached:
            import json
            return json.loads(cached)
    except Exception:
        pass  # Cache is optional
    
    result = await db.execute(
        select(BotConfig).where(BotConfig.city_id == city.id)
    )
    bot_config = result.scalar_one_or_none()
    
    if not bot_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot configuration not found"
        )
    
    # Cache the result
    try:
        r = redis.from_url(settings.REDIS_URL)
        import json
        await r.setex(
            f"bot_config:{city.id}",
            3600,  # 1 hour
            json.dumps({
                "id": bot_config.id,
                "city_id": bot_config.city_id,
                "system_prompt": bot_config.system_prompt,
                "greeting_message": bot_config.greeting_message,
                "manager_contact": bot_config.manager_contact,
                "escalation_action": bot_config.escalation_action.value,
                "updated_by": bot_config.updated_by,
                "updated_at": bot_config.updated_at.isoformat()
            })
        )
        await r.close()
    except Exception:
        pass
    
    return bot_config


@router.put("/config", response_model=BotConfigResponse)
async def update_bot_config(
    config_data: BotConfigUpdate,
    city: City = Depends(get_user_city_access),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update bot configuration for a city"""
    
    result = await db.execute(
        select(BotConfig).where(BotConfig.city_id == city.id)
    )
    bot_config = result.scalar_one_or_none()
    
    if not bot_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot configuration not found"
        )
    
    # Store old values for audit
    old_value = {
        "system_prompt": bot_config.system_prompt,
        "greeting_message": bot_config.greeting_message,
        "manager_contact": bot_config.manager_contact,
        "escalation_action": bot_config.escalation_action.value if bot_config.escalation_action else None
    }
    
    # Update fields
    update_data = config_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bot_config, field, value)
    
    bot_config.updated_by = current_user.id
    
    # Log audit
    audit = AuditLog(
        user_id=current_user.id,
        city_id=city.id,
        action="UPDATE",
        table_name="bot_configs",
        record_id=bot_config.id,
        old_value=old_value,
        new_value=update_data
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(bot_config)
    
    # Invalidate cache
    await invalidate_cache(city.id)
    
    return bot_config


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    city: City = Depends(get_user_city_access),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a city"""
    
    # Get conversation stats
    total_convs = await db.execute(
        select(func.count(Conversation.id)).where(Conversation.city_id == city.id)
    )
    total_conversations = total_convs.scalar() or 0
    
    active_convs = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.city_id == city.id,
            Conversation.ended_at.is_(None)
        )
    )
    active_conversations = active_convs.scalar() or 0
    
    total_msgs = await db.execute(
        select(func.count(Message.id))
        .join(Conversation)
        .where(Conversation.city_id == city.id)
    )
    total_messages = total_msgs.scalar() or 0
    
    avg_msgs = total_messages / total_conversations if total_conversations > 0 else 0
    
    # Get recent conversations
    recent = await db.execute(
        select(Conversation)
        .where(Conversation.city_id == city.id)
        .order_by(Conversation.started_at.desc())
        .limit(10)
    )
    recent_conversations = [
        {
            "id": conv.id,
            "user_telegram_id": conv.user_telegram_id,
            "started_at": conv.started_at.isoformat(),
            "ended_at": conv.ended_at.isoformat() if conv.ended_at else None,
            "message_count": conv.message_count
        }
        for conv in recent.scalars().all()
    ]
    
    return {
        "stats": {
            "total_conversations": total_conversations,
            "active_conversations": active_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": round(avg_msgs, 2)
        },
        "recent_conversations": recent_conversations
    }
