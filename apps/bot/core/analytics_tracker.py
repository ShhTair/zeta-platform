"""
Analytics Tracker - Track bot events to admin platform
"""
import aiohttp
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalyticsTracker:
    """Tracks analytics events to ZETA admin platform"""
    
    def __init__(self, api_url: str):
        """
        Initialize AnalyticsTracker
        
        Args:
            api_url: Base URL of ZETA admin API
        """
        self.api_url = api_url.rstrip('/')
    
    async def track_event(
        self,
        city_id: int,
        event_type: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track an analytics event
        
        Args:
            city_id: City ID
            event_type: Event type (e.g., "search", "product_view", "escalation")
            data: Additional event data
        
        Returns:
            True if tracked successfully, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/analytics/events"
                payload = {
                    "city_id": city_id,
                    "event_type": event_type,
                    "data": data or {}
                }
                
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status in (200, 201):
                        logger.debug(f"📊 Event tracked: {event_type}")
                        return True
                    else:
                        logger.warning(f"⚠️ Failed to track event: HTTP {resp.status}")
                        return False
        
        except Exception as e:
            logger.warning(f"⚠️ Analytics tracking error: {e}")
            return False
    
    async def track_search(self, city_id: int, query: str, results_count: int):
        """Track a product search"""
        return await self.track_event(
            city_id=city_id,
            event_type="search",
            data={"query": query, "results_count": results_count}
        )
    
    async def track_product_view(self, city_id: int, product_sku: str):
        """Track a product view"""
        return await self.track_event(
            city_id=city_id,
            event_type="product_view",
            data={"product_sku": product_sku}
        )
    
    async def track_escalation(self, city_id: int, reason: str):
        """Track an escalation"""
        return await self.track_event(
            city_id=city_id,
            event_type="escalation",
            data={"reason": reason}
        )
    
    async def track_conversation_start(self, city_id: int, user_id: int):
        """Track a conversation start"""
        return await self.track_event(
            city_id=city_id,
            event_type="conversation_start",
            data={"user_id": user_id}
        )
