"""
User Context Management
Tracks user preferences, viewed products, and conversation state
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.memory import conversation_memory

logger = logging.getLogger(__name__)


async def get_user_context(phone: str) -> Dict[str, Any]:
    """
    Get full user context from Redis.
    
    Returns:
        {
            "preferences": {"colors": [...], "materials": [...], "budget_range": "..."},
            "viewed_products": ["SKU1", "SKU2", ...],
            "language": "ru" | "kz",
            "last_interaction": "2026-02-20T10:30:00"
        }
    """
    try:
        if conversation_memory.redis is None:
            await conversation_memory.connect()
        
        key = f"user_context:{phone}"
        data = await conversation_memory.redis.get(key)
        
        if data:
            context = json.loads(data)
            return context
        
        # Default context
        return {
            "preferences": {},
            "viewed_products": [],
            "language": "ru",
            "last_interaction": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Get user context error: {e}")
        return {
            "preferences": {},
            "viewed_products": [],
            "language": "ru"
        }


async def update_user_preferences(phone: str, preferences: Dict[str, Any]):
    """
    Update user preferences (colors, materials, budget, etc.).
    """
    try:
        context = await get_user_context(phone)
        
        # Merge preferences
        current_prefs = context.get("preferences", {})
        
        for key, value in preferences.items():
            if key in ["colors", "materials"]:
                # Merge lists
                current_values = current_prefs.get(key, [])
                current_prefs[key] = list(set(current_values + value))
            else:
                current_prefs[key] = value
        
        context["preferences"] = current_prefs
        context["last_interaction"] = datetime.now().isoformat()
        
        # Save to Redis
        await _save_user_context(phone, context)
        
        logger.info(f"✓ Updated preferences for {phone}: {preferences}")
    
    except Exception as e:
        logger.error(f"❌ Update preferences error: {e}")


async def track_viewed_products(phone: str, sku_list: List[str]):
    """
    Track which products user has viewed.
    Keep last 20 products.
    """
    try:
        context = await get_user_context(phone)
        
        viewed = context.get("viewed_products", [])
        
        # Add new products (avoid duplicates)
        for sku in sku_list:
            if sku not in viewed:
                viewed.insert(0, sku)
        
        # Keep last 20
        context["viewed_products"] = viewed[:20]
        context["last_interaction"] = datetime.now().isoformat()
        
        await _save_user_context(phone, context)
        
        logger.debug(f"✓ Tracked {len(sku_list)} products for {phone}")
    
    except Exception as e:
        logger.error(f"❌ Track viewed products error: {e}")


async def set_user_language(phone: str, language: str):
    """Set user's preferred language"""
    try:
        context = await get_user_context(phone)
        context["language"] = language
        await _save_user_context(phone, context)
        
        logger.info(f"✓ Set language {language} for {phone}")
    
    except Exception as e:
        logger.error(f"❌ Set language error: {e}")


async def _save_user_context(phone: str, context: Dict[str, Any]):
    """Save user context to Redis with 7-day expiration"""
    try:
        if conversation_memory.redis is None:
            await conversation_memory.connect()
        
        key = f"user_context:{phone}"
        await conversation_memory.redis.setex(
            key,
            60 * 60 * 24 * 7,  # 7 days
            json.dumps(context)
        )
    
    except Exception as e:
        logger.error(f"❌ Save user context error: {e}")


__all__ = [
    "get_user_context",
    "update_user_preferences",
    "track_viewed_products",
    "set_user_language"
]
