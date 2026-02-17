"""
Prompt Manager - Dynamic prompt loading with hot-reload
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages dynamic prompts with caching and hot-reload"""
    
    def __init__(self, api_client, city_id: str, cache_ttl: int = 300):
        self.api_client = api_client
        self.city_id = city_id
        self.cache_ttl = cache_ttl  # Cache TTL in seconds (5 min default)
        
        self.config: Optional[Dict] = None
        self.prompts: Dict[str, str] = {}
        self.last_reload: Optional[datetime] = None
    
    async def load_config(self) -> None:
        """Load city config and prompts"""
        self.config = await self.api_client.get_city_config(self.city_id)
        self.prompts = self.config.get("prompts", {})
        self.last_reload = datetime.now()
        logger.info(f"✅ Config loaded: {self.city_id}")
    
    async def reload_if_stale(self) -> None:
        """Reload prompts if cache is stale"""
        if self.last_reload is None:
            await self.load_config()
            return
        
        age = datetime.now() - self.last_reload
        if age.total_seconds() > self.cache_ttl:
            logger.info("🔄 Cache stale, reloading prompts...")
            try:
                new_prompts = await self.api_client.get_prompts(self.city_id)
                self.prompts.update(new_prompts)
                self.last_reload = datetime.now()
            except Exception as e:
                logger.error(f"❌ Failed to reload prompts: {e}")
    
    async def get_prompt(self, key: str, default: str = "") -> str:
        """Get prompt by key with hot-reload"""
        await self.reload_if_stale()
        return self.prompts.get(key, default)
    
    def get_config(self, key: str, default=None):
        """Get config value"""
        if self.config is None:
            return default
        return self.config.get(key, default)
    
    @property
    def manager_telegram_id(self) -> Optional[str]:
        """Get manager Telegram ID for tagging"""
        return self.get_config("manager_telegram_id")
    
    @property
    def bitrix_endpoint(self) -> Optional[str]:
        """Get Bitrix API endpoint"""
        return self.get_config("bitrix_endpoint")
