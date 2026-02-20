"""
Bitrix24 CRM Integration (Stub)

Integration with Bitrix24 for:
- Lead creation from bot conversations
- Deal tracking
- Task assignment to managers
- Activity logging
- Contact management

TODO (Next Phase):
1. Get Bitrix24 webhook URL from account settings
2. Configure CRM fields mapping
3. Setup lead/deal stages pipeline
4. Test API calls and error handling
5. Implement automatic lead scoring
6. Setup activity stream logging

Bitrix24 REST API Documentation:
- Webhook format: https://your-domain.bitrix24.com/rest/USER_ID/WEBHOOK_CODE/
- Common endpoints:
  - crm.lead.add - Create lead
  - crm.deal.add - Create deal
  - crm.contact.add - Create contact
  - tasks.task.add - Create task
  - crm.timeline.comment.add - Add comment
"""

from typing import Dict, Any, Optional, List
import logging
import aiohttp
import json
from datetime import datetime

from . import Integration

logger = logging.getLogger(__name__)


class Bitrix24Integration(Integration):
    """
    Bitrix24 CRM integration connector.
    
    Currently a stub - implementation required in next phase.
    """
    
    def __init__(
        self,
        webhook_url: str,
        create_leads: bool = True,
        create_tasks: bool = True,
        timeout: int = 30
    ):
        """
        Initialize Bitrix24 integration.
        
        Args:
            webhook_url: Bitrix24 webhook URL
            create_leads: Automatically create leads from conversations
            create_tasks: Create tasks for managers
            timeout: Request timeout in seconds
        """
        self.webhook_url = webhook_url.rstrip('/')
        self.create_leads = create_leads
        self.create_tasks = create_tasks
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"Bitrix24 integration configured")
    
    async def initialize(self) -> bool:
        """
        Test connection to Bitrix24.
        
        TODO: Implement actual connection test
        - Create HTTP session
        - Test webhook validity
        - Check permissions
        """
        logger.warning("Bitrix24 integration: TODO - not implemented yet")
        
        # Stub: Always return False until implemented
        # When ready:
        # try:
        #     self.session = aiohttp.ClientSession(timeout=self.timeout)
        #     
        #     # Test webhook with simple API call
        #     async with self.session.get(f"{self.webhook_url}/profile.json") as resp:
        #         if resp.status == 200:
        #             data = await resp.json()
        #             if "result" in data:
        #                 logger.info("✓ Bitrix24 connection successful")
        #                 return True
        # except Exception as e:
        #     logger.error(f"✗ Bitrix24 connection failed: {e}")
        
        return False
    
    async def sync_products(self) -> Dict[str, Any]:
        """
        Bitrix24 doesn't manage products in the same way as 1C.
        This method is not applicable for CRM integration.
        """
        logger.info("Bitrix24: Product sync not applicable (CRM system)")
        return {
            "success": True,
            "products_synced": 0,
            "errors": []
        }
    
    async def check_availability(self, sku: str) -> Dict[str, Any]:
        """
        Bitrix24 doesn't track inventory.
        This method is not applicable for CRM integration.
        """
        logger.info("Bitrix24: Availability check not applicable (CRM system)")
        return {
            "available": False,
            "quantity": 0,
            "price": 0.0,
            "error": "Not applicable for CRM"
        }
    
    async def create_order(self, order_data: dict) -> Dict[str, Any]:
        """
        Create deal in Bitrix24 from order.
        
        TODO: Implement deal creation
        - Map order to Bitrix24 deal fields
        - Create contact if doesn't exist
        - Create deal with products
        - Add initial comment with order details
        
        Bitrix24 Deal Structure:
        {
          "fields": {
            "TITLE": "Заказ из Telegram",
            "TYPE_ID": "SALE",
            "STAGE_ID": "NEW",
            "CURRENCY_ID": "KZT",
            "OPPORTUNITY": 45000.00,
            "CONTACT_ID": 123,
            "COMMENTS": "Детали заказа...",
            "UF_CRM_TELEGRAM_ID": "123456789"
          }
        }
        """
        logger.warning("Bitrix24 order creation: TODO - not implemented yet")
        
        # Stub return
        return {
            "success": False,
            "order_id": None,
            "error": "Bitrix24 integration not implemented yet"
        }
        
        # TODO: Implement actual deal creation
        # try:
        #     # 1. Find or create contact
        #     contact_id = await self._find_or_create_contact(order_data["customer"])
        #     
        #     # 2. Create deal
        #     deal_data = {
        #         "fields": {
        #             "TITLE": f"Заказ от {order_data['customer']['name']}",
        #             "TYPE_ID": "SALE",
        #             "STAGE_ID": "NEW",
        #             "CURRENCY_ID": "KZT",
        #             "OPPORTUNITY": order_data["total"],
        #             "CONTACT_ID": contact_id,
        #             "COMMENTS": self._format_order_details(order_data)
        #         }
        #     }
        #     
        #     async with self.session.post(
        #         f"{self.webhook_url}/crm.deal.add.json",
        #         json=deal_data
        #     ) as resp:
        #         if resp.status == 200:
        #             result = await resp.json()
        #             deal_id = result.get("result")
        #             
        #             # 3. Add products to deal
        #             await self._add_products_to_deal(deal_id, order_data["products"])
        #             
        #             return {"success": True, "order_id": str(deal_id)}
        # except Exception as e:
        #     return {"success": False, "error": str(e)}
    
    async def create_lead(
        self,
        user_data: Dict[str, Any],
        conversation: List[Dict[str, str]],
        source: str = "Telegram Bot"
    ) -> Dict[str, Any]:
        """
        Create lead in Bitrix24 from bot conversation.
        
        TODO: Implement lead creation
        - Map user data to Bitrix24 lead fields
        - Include conversation history
        - Set lead source and tags
        - Add custom fields (Telegram ID, city, etc.)
        
        Args:
            user_data: User information (name, phone, telegram_id, etc.)
            conversation: List of messages in conversation
            source: Lead source identifier
        
        Returns:
            Dict with lead creation result
        
        Example:
        POST {webhook_url}/crm.lead.add.json
        {
          "fields": {
            "TITLE": "Лид из Telegram",
            "NAME": "Иван",
            "LAST_NAME": "Петров",
            "PHONE": [{"VALUE": "+77771234567", "VALUE_TYPE": "WORK"}],
            "SOURCE_ID": "TELEGRAM",
            "COMMENTS": "Разговор:\nUser: Хочу диван\nBot: Какой бюджет?",
            "UF_CRM_TELEGRAM_ID": "123456789",
            "UF_CRM_CITY": "Алматы"
          }
        }
        """
        logger.warning("Bitrix24 lead creation: TODO - not implemented yet")
        
        # Stub return
        return {
            "success": False,
            "lead_id": None,
            "error": "Bitrix24 integration not implemented yet"
        }
        
        # TODO: Implement actual lead creation
        # try:
        #     conversation_text = self._format_conversation(conversation)
        #     
        #     lead_data = {
        #         "fields": {
        #             "TITLE": f"Лид из {source}: {user_data.get('name', 'Unnamed')}",
        #             "NAME": user_data.get("first_name", ""),
        #             "LAST_NAME": user_data.get("last_name", ""),
        #             "SOURCE_ID": "TELEGRAM",
        #             "COMMENTS": conversation_text,
        #             "UF_CRM_TELEGRAM_ID": str(user_data.get("telegram_id", ""))
        #         }
        #     }
        #     
        #     # Add phone if available
        #     if "phone" in user_data:
        #         lead_data["fields"]["PHONE"] = [
        #             {"VALUE": user_data["phone"], "VALUE_TYPE": "WORK"}
        #         ]
        #     
        #     async with self.session.post(
        #         f"{self.webhook_url}/crm.lead.add.json",
        #         json=lead_data
        #     ) as resp:
        #         if resp.status == 200:
        #             result = await resp.json()
        #             lead_id = result.get("result")
        #             logger.info(f"✓ Lead created in Bitrix24: {lead_id}")
        #             return {"success": True, "lead_id": str(lead_id)}
        # except Exception as e:
        #     logger.error(f"✗ Bitrix24 lead creation error: {e}")
        #     return {"success": False, "error": str(e)}
    
    async def create_task_for_manager(
        self,
        title: str,
        description: str,
        responsible_id: Optional[int] = None,
        deadline: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create task for manager in Bitrix24.
        
        TODO: Implement task creation
        - Create task with description
        - Assign to responsible manager
        - Set deadline if provided
        - Link to related CRM entity if needed
        
        Args:
            title: Task title
            description: Task description
            responsible_id: Bitrix24 user ID of responsible person
            deadline: Task deadline
        
        Returns:
            Dict with task creation result
        
        Example:
        POST {webhook_url}/tasks.task.add.json
        {
          "fields": {
            "TITLE": "Связаться с клиентом",
            "DESCRIPTION": "Клиент интересуется диваном...",
            "RESPONSIBLE_ID": 1,
            "DEADLINE": "2024-02-20T18:00:00",
            "PRIORITY": "1"
          }
        }
        """
        logger.warning("Bitrix24 task creation: TODO - not implemented yet")
        
        # Stub return
        return {
            "success": False,
            "task_id": None,
            "error": "Bitrix24 integration not implemented yet"
        }
        
        # TODO: Implement actual task creation
        # try:
        #     task_data = {
        #         "fields": {
        #             "TITLE": title,
        #             "DESCRIPTION": description,
        #             "PRIORITY": "1"  # High priority
        #         }
        #     }
        #     
        #     if responsible_id:
        #         task_data["fields"]["RESPONSIBLE_ID"] = responsible_id
        #     
        #     if deadline:
        #         task_data["fields"]["DEADLINE"] = deadline.isoformat()
        #     
        #     async with self.session.post(
        #         f"{self.webhook_url}/tasks.task.add.json",
        #         json=task_data
        #     ) as resp:
        #         if resp.status == 200:
        #             result = await resp.json()
        #             task_id = result.get("result", {}).get("task", {}).get("id")
        #             return {"success": True, "task_id": str(task_id)}
        # except Exception as e:
        #     return {"success": False, "error": str(e)}
    
    def _format_conversation(self, conversation: List[Dict[str, str]]) -> str:
        """Format conversation history for Bitrix24 comments."""
        lines = ["=== История разговора ===", ""]
        for msg in conversation:
            role = "Клиент" if msg["role"] == "user" else "Бот"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
    
    def _format_order_details(self, order_data: dict) -> str:
        """Format order details for Bitrix24 comments."""
        lines = [
            "=== Детали заказа ===",
            f"Клиент: {order_data['customer']['name']}",
            f"Телефон: {order_data['customer']['phone']}",
            "",
            "Товары:"
        ]
        for item in order_data["products"]:
            lines.append(f"- {item['sku']} x{item['quantity']} = {item['price']} KZT")
        lines.append(f"\nДоставка: {order_data['delivery']['address']}")
        lines.append(f"Сумма: {order_data['total']} KZT")
        return "\n".join(lines)
    
    async def _find_or_create_contact(self, customer_data: dict) -> int:
        """
        Find existing contact by phone or create new one.
        
        TODO: Implement contact search and creation
        """
        # Stub - return dummy ID
        return 1
    
    async def _add_products_to_deal(self, deal_id: int, products: List[dict]):
        """
        Add products to deal.
        
        TODO: Implement product rows addition
        """
        pass
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()


__all__ = ["Bitrix24Integration"]
