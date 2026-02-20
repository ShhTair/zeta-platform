"""
Middleware for injecting services into handlers (aiogram 3.7+ compatible)
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class ServicesMiddleware(BaseMiddleware):
    """Inject services into handler context"""
    
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Inject services into data dict
        data.update(self.services)
        
        # Also create a fake bot.get() for backward compatibility
        # by attaching services to the bot object temporarily
        if hasattr(event, 'bot'):
            original_get = getattr(event.bot, 'get', None)
            
            def fake_get(key, default=None):
                return self.services.get(key, default)
            
            event.bot.get = fake_get
        
        return await handler(event, data)
