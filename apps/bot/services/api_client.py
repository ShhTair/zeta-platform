"""
API Client for fetching config, catalog, and creating Bitrix deals
"""
import logging
from typing import Dict, List, Optional, Any
from aiohttp import ClientSession, ClientError

logger = logging.getLogger(__name__)


class APIClient:
    """Client for ZETA API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[ClientSession] = None
    
    async def _get_session(self) -> ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = ClientSession()
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_city_config(self, city_id: str) -> Dict[str, Any]:
        """
        Fetch city configuration
        GET /api/cities/{city_id}/config
        
        Returns:
        {
            "city_id": "moscow",
            "city_name": "Москва",
            "bot_token": "...",
            "manager_telegram_id": "@manager_username",
            "prompts": {
                "greeting": "Добро пожаловать! Я помогу вам...",
                "product_inquiry": "Что вас интересует?",
                "catalog_search": "Ищу в каталоге..."
            },
            "bitrix_endpoint": "https://your-bitrix.ru/rest/..."
        }
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/cities/{city_id}/config"
        
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"✅ Config loaded for city: {city_id}")
                return data
        except ClientError as e:
            logger.error(f"❌ Failed to fetch config: {e}")
            raise
    
    async def search_products(
        self, 
        query: str, 
        city_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search products in catalog
        GET /api/products/search?q=query&city_id=city&limit=5
        
        Returns:
        [
            {
                "id": "123",
                "name": "Product Name",
                "description": "...",
                "price": 1000,
                "url": "https://shop.com/product/123",
                "image_url": "https://..."
            }
        ]
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/products/search"
        params = {
            "q": query,
            "city_id": city_id,
            "limit": limit
        }
        
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"🔍 Found {len(data)} products for: {query}")
                return data
        except ClientError as e:
            logger.error(f"❌ Product search failed: {e}")
            return []
    
    async def create_bitrix_deal(
        self,
        customer_name: str,
        customer_telegram: str,
        product_id: Optional[str],
        message: str,
        city_id: str
    ) -> Dict[str, Any]:
        """
        Create Bitrix CRM deal
        POST /api/bitrix/deals
        
        Returns:
        {
            "success": true,
            "deal_id": "12345",
            "deal_url": "https://bitrix.ru/crm/deal/12345/"
        }
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/bitrix/deals"
        payload = {
            "customer_name": customer_name,
            "customer_telegram": customer_telegram,
            "product_id": product_id,
            "message": message,
            "city_id": city_id,
            "source": "telegram_bot"
        }
        
        try:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"✅ Bitrix deal created: {data.get('deal_id')}")
                return data
        except ClientError as e:
            logger.error(f"❌ Bitrix deal creation failed: {e}")
            raise
    
    async def get_prompts(self, city_id: str) -> Dict[str, str]:
        """
        Fetch dynamic prompts for the city
        GET /api/cities/{city_id}/prompts
        
        Returns hot-reloadable prompts from DB
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/cities/{city_id}/prompts"
        
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"🔄 Prompts reloaded for: {city_id}")
                return data
        except ClientError as e:
            logger.error(f"❌ Failed to fetch prompts: {e}")
            raise
