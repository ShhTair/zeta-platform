"""
Price Alerts & Saved Searches
Background worker notifies users when conditions are met
"""

import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from core.memory import conversation_memory

logger = logging.getLogger(__name__)


async def save_price_alert(
    user_phone: str,
    sku: str,
    target_price: Optional[float] = None
):
    """
    Save price alert for a product.
    
    Worker checks daily and sends template message when price drops.
    """
    try:
        if conversation_memory.redis is None:
            await conversation_memory.connect()
        
        alert = {
            "user_phone": user_phone,
            "sku": sku,
            "target_price": target_price,
            "created_at": datetime.now().isoformat()
        }
        
        # Add to alerts set
        key = f"price_alerts:{user_phone}"
        await conversation_memory.redis.lpush(key, json.dumps(alert))
        await conversation_memory.redis.expire(key, 60 * 60 * 24 * 30)  # 30 days
        
        logger.info(f"✓ Price alert saved: {user_phone} → {sku}")
    
    except Exception as e:
        logger.error(f"❌ Save price alert error: {e}")


async def get_price_alerts(user_phone: str) -> List[Dict[str, Any]]:
    """Get all price alerts for a user"""
    try:
        if conversation_memory.redis is None:
            await conversation_memory.connect()
        
        key = f"price_alerts:{user_phone}"
        alerts_raw = await conversation_memory.redis.lrange(key, 0, -1)
        
        alerts = [json.loads(alert) for alert in alerts_raw]
        return alerts
    
    except Exception as e:
        logger.error(f"❌ Get price alerts error: {e}")
        return []


async def save_search_query(
    user_phone: str,
    query: str,
    category: Optional[str] = None
):
    """
    Save search query for future notifications.
    
    When new products matching this search arrive, notify user.
    """
    try:
        if conversation_memory.redis is None:
            await conversation_memory.connect()
        
        search = {
            "user_phone": user_phone,
            "query": query,
            "category": category,
            "created_at": datetime.now().isoformat()
        }
        
        key = f"saved_searches:{user_phone}"
        await conversation_memory.redis.lpush(key, json.dumps(search))
        await conversation_memory.redis.expire(key, 60 * 60 * 24 * 30)  # 30 days
        
        logger.info(f"✓ Search saved: {user_phone} → {query}")
    
    except Exception as e:
        logger.error(f"❌ Save search error: {e}")


async def get_saved_searches(user_phone: str) -> List[Dict[str, Any]]:
    """Get all saved searches for a user"""
    try:
        if conversation_memory.redis is None:
            await conversation_memory.connect()
        
        key = f"saved_searches:{user_phone}"
        searches_raw = await conversation_memory.redis.lrange(key, 0, -1)
        
        searches = [json.loads(s) for s in searches_raw]
        return searches
    
    except Exception as e:
        logger.error(f"❌ Get saved searches error: {e}")
        return []


__all__ = [
    "save_price_alert",
    "get_price_alerts",
    "save_search_query",
    "get_saved_searches"
]
