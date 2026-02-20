"""
Rate Limiting Middleware
Prevent abuse and API overuse with Redis-based rate limiting
"""

from typing import Callable, Dict, Any, Awaitable
import logging

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """
    Rate limiting middleware for Aiogram bot.
    
    Features:
    - Per-user rate limiting
    - Configurable limits (messages per time window)
    - Redis-based storage
    - Automatic cleanup
    
    Usage:
        rate_limiter = RateLimitMiddleware(
            redis_url="redis://localhost:6379",
            limit=10,  # messages
            window=60  # seconds
        )
        dp.message.middleware(rate_limiter)
    """
    
    def __init__(
        self,
        redis_url: str,
        limit: int = 10,
        window: int = 60,
        warning_message: str = "⏳ Слишком много запросов. Подождите минуту."
    ):
        """
        Initialize rate limiter.
        
        Args:
            redis_url: Redis connection URL
            limit: Maximum messages allowed per window
            window: Time window in seconds
            warning_message: Message to send when limit exceeded
        """
        super().__init__()
        
        if redis is None:
            logger.error("redis.asyncio not available - install with: pip install redis")
            raise ImportError("redis package required for RateLimitMiddleware")
        
        self.redis_url = redis_url
        self.limit = limit
        self.window = window
        self.warning_message = warning_message
        self.redis = redis.from_url(redis_url)
        
        logger.info(f"RateLimiter configured: {limit} messages per {window}s")
    
    def _get_key(self, user_id: int) -> str:
        """Generate Redis key for user rate limit."""
        return f"rate:{user_id}"
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Middleware handler.
        
        Args:
            handler: Next handler in chain
            event: Telegram event (message)
            data: Handler data
        
        Returns:
            Handler result or None if rate limited
        """
        # Get user ID
        user_id = event.from_user.id
        key = self._get_key(user_id)
        
        try:
            # Increment counter
            count = await self.redis.incr(key)
            
            # Set expiration on first message in window
            if count == 1:
                await self.redis.expire(key, self.window)
            
            # Check if limit exceeded
            if count > self.limit:
                logger.warning(f"Rate limit exceeded for user {user_id}: {count}/{self.limit}")
                await event.answer(self.warning_message)
                return None
            
            # Log if approaching limit
            if count == self.limit - 2:
                logger.info(f"User {user_id} approaching rate limit: {count}/{self.limit}")
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Don't block on rate limiter errors - fail open
        
        # Continue to next handler
        return await handler(event, data)
    
    async def close(self):
        """Close Redis connection."""
        await self.redis.close()


class AdaptiveRateLimiter(BaseMiddleware):
    """
    Advanced rate limiter with adaptive limits based on user behavior.
    
    Features:
    - Different limits for new vs trusted users
    - Burst protection
    - Cooldown periods for violators
    
    TODO: Implement in next phase if needed
    """
    
    def __init__(
        self,
        redis_url: str,
        new_user_limit: int = 5,
        trusted_user_limit: int = 20,
        burst_limit: int = 3,  # Max messages in 5 seconds
        cooldown_period: int = 300  # 5 minutes ban for violators
    ):
        super().__init__()
        
        if redis is None:
            raise ImportError("redis package required")
        
        self.redis = redis.from_url(redis_url)
        self.new_user_limit = new_user_limit
        self.trusted_user_limit = trusted_user_limit
        self.burst_limit = burst_limit
        self.cooldown_period = cooldown_period
        
        logger.info("AdaptiveRateLimiter configured (TODO: Implement)")
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """TODO: Implement adaptive rate limiting logic."""
        # For now, just pass through
        return await handler(event, data)


__all__ = ["RateLimitMiddleware", "AdaptiveRateLimiter"]
