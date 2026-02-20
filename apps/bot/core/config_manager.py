"""
Config Manager - Dynamic configuration loading with auto-reload
Loads bot configuration from ZETA admin API and hot-reloads every 5 minutes
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages dynamic bot configuration with hot-reload from admin API"""
    
    def __init__(self, api_url: str, city_id: int, reload_interval: int = 300):
        """
        Initialize ConfigManager
        
        Args:
            api_url: Base URL of ZETA admin API (e.g., http://localhost:8000)
            city_id: City ID for this bot instance
            reload_interval: Seconds between config reloads (default: 300 = 5 minutes)
        """
        self.api_url = api_url.rstrip('/')
        self.city_id = city_id
        self.reload_interval = reload_interval
        self.config: Dict[str, Any] = {}
        self.last_reload: Optional[datetime] = None
        self._reload_task: Optional[asyncio.Task] = None
    
    async def load_config(self) -> Dict[str, Any]:
        """Load configuration from API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/cities/{self.city_id}/bot-config"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        self.config = await resp.json()
                        self.last_reload = datetime.now()
                        logger.info(f"✅ Config loaded for city {self.city_id}")
                        return self.config
                    else:
                        logger.error(f"❌ Failed to load config: HTTP {resp.status}")
                        raise Exception(f"Config load failed with status {resp.status}")
        except Exception as e:
            logger.error(f"❌ Config load error: {e}")
            raise
    
    async def auto_reload(self):
        """Background task that reloads config every N seconds"""
        while True:
            await asyncio.sleep(self.reload_interval)
            try:
                await self.load_config()
                logger.info(f"🔄 Config auto-reloaded (every {self.reload_interval}s)")
            except Exception as e:
                logger.error(f"❌ Auto-reload failed: {e}")
    
    def start_auto_reload(self):
        """Start the auto-reload background task"""
        if self._reload_task is None or self._reload_task.done():
            self._reload_task = asyncio.create_task(self.auto_reload())
            logger.info(f"🚀 Started auto-reload task (interval: {self.reload_interval}s)")
    
    def stop_auto_reload(self):
        """Stop the auto-reload background task"""
        if self._reload_task and not self._reload_task.done():
            self._reload_task.cancel()
            logger.info("⏹️ Stopped auto-reload task")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key"""
        return self.config.get(key, default)
    
    @property
    def system_prompt(self) -> Optional[str]:
        """Get system prompt for AI"""
        return self.config.get('system_prompt')
    
    @property
    def greeting_message(self) -> Optional[str]:
        """Get greeting message"""
        return self.config.get('greeting_message', 'Добро пожаловать! Чем могу помочь?')
    
    @property
    def manager_contact(self) -> Optional[str]:
        """Get manager contact (phone/telegram)"""
        return self.config.get('manager_contact')
    
    @property
    def escalation_action(self) -> str:
        """Get escalation action (notify/transfer/log_only)"""
        return self.config.get('escalation_action', 'log_only')
