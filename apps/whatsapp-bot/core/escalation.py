"""
Manager Escalation Logger
Logs escalations to admin platform for manager follow-up
"""

import logging
import httpx
from typing import Optional
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


async def log_escalation(
    user_phone: str,
    product_sku: Optional[str] = None,
    reason: str = "user_request",
    conversation_excerpt: Optional[str] = None
):
    """
    Log escalation to admin platform.
    
    Args:
        user_phone: User's WhatsApp number
        product_sku: Product SKU (if escalation is about specific product)
        reason: Escalation reason (user_request, not_found, complex_query, etc.)
        conversation_excerpt: Last few messages for context
    """
    try:
        payload = {
            "platform": "whatsapp",
            "user_id": user_phone,
            "user_phone": user_phone,
            "product_sku": product_sku,
            "reason": reason,
            "conversation_excerpt": conversation_excerpt,
            "timestamp": datetime.now().isoformat(),
            "city_id": settings.city_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.admin_api_url}/api/escalations",
                json=payload,
                headers={"Authorization": f"Bearer {settings.admin_api_key}"},
                timeout=10.0
            )
            response.raise_for_status()
            
            logger.info(f"✓ Escalation logged: {user_phone} → {reason}")
    
    except Exception as e:
        logger.error(f"❌ Log escalation error: {e}")


__all__ = ["log_escalation"]
