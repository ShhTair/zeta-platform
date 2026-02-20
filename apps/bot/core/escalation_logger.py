"""
Escalation Logger - Log user escalations to admin platform
"""
import aiohttp
import logging
from typing import Optional, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class EscalationLogger:
    """Logs escalations to ZETA admin platform"""
    
    def __init__(self, api_url: str):
        """
        Initialize EscalationLogger
        
        Args:
            api_url: Base URL of ZETA admin API
        """
        self.api_url = api_url.rstrip('/')
    
    async def log_escalation(
        self,
        city_id: int,
        user_id: int,
        user_name: str,
        product_sku: Optional[str],
        reason: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> bool:
        """
        Log an escalation to the admin platform
        
        Args:
            city_id: City ID
            user_id: Telegram user ID
            user_name: User's display name
            product_sku: Product SKU (if applicable)
            reason: Escalation reason (e.g., "price_question", "availability", "complex_query")
            conversation_history: List of conversation messages
        
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/escalations"
                payload = {
                    "city_id": city_id,
                    "user_telegram_id": user_id,
                    "user_name": user_name,
                    "product_sku": product_sku,
                    "reason": reason,
                    "conversation": conversation_history or []
                }
                
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status in (200, 201):
                        data = await resp.json()
                        escalation_id = data.get('id')
                        logger.info(f"✅ Escalation logged: #{escalation_id} - User {user_id}, Reason: {reason}")
                        return True
                    else:
                        logger.error(f"❌ Failed to log escalation: HTTP {resp.status}")
                        return False
        
        except Exception as e:
            logger.error(f"❌ Escalation logging error: {e}")
            return False
