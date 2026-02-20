"""
Conversation Memory System
Redis-based conversation history storage for context-aware responses
"""

from typing import List, Dict, Optional
import logging
import json
from datetime import datetime

try:
    import redis.asyncio as redis
except ImportError:
    # Fallback if redis not installed yet
    redis = None

logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    Manages conversation history using Redis.
    
    Features:
    - Store last N messages per user
    - Automatic expiration (24h default)
    - JSON serialization
    - Async operations
    
    Usage:
        memory = ConversationMemory(redis_url="redis://localhost:6379")
        await memory.save_message(user_id=123, role="user", content="Hello")
        history = await memory.get_history(user_id=123)
    """
    
    def __init__(
        self,
        redis_url: str,
        max_messages: int = 20,
        ttl_seconds: int = 86400  # 24 hours
    ):
        """
        Initialize conversation memory.
        
        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
            max_messages: Maximum messages to keep per user
            ttl_seconds: Time-to-live for conversation history (default 24h)
        """
        if redis is None:
            logger.error("redis.asyncio not available - install with: pip install redis")
            raise ImportError("redis package required for ConversationMemory")
        
        self.redis_url = redis_url
        self.max_messages = max_messages
        self.ttl_seconds = ttl_seconds
        self.redis: Optional[redis.Redis] = None
        
        logger.info(f"ConversationMemory configured: max={max_messages}, ttl={ttl_seconds}s")
    
    async def connect(self):
        """Establish Redis connection."""
        if self.redis is None:
            self.redis = redis.from_url(self.redis_url)
            logger.info("✓ Connected to Redis")
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("✓ Redis connection closed")
    
    def _get_key(self, user_id: int) -> str:
        """Generate Redis key for user conversation."""
        return f"conv:{user_id}"
    
    async def save_message(
        self,
        user_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Save message to conversation history.
        
        Args:
            user_id: Telegram user ID
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Additional metadata (optional)
        """
        if self.redis is None:
            await self.connect()
        
        key = self._get_key(user_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        # Add message to list (left push = newest first)
        await self.redis.lpush(key, json.dumps(message))
        
        # Trim to max_messages
        await self.redis.ltrim(key, 0, self.max_messages - 1)
        
        # Set expiration
        await self.redis.expire(key, self.ttl_seconds)
        
        logger.debug(f"Saved message for user {user_id}: {role}")
    
    async def get_history(
        self,
        user_id: int,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get conversation history for user.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum messages to return (None = all)
        
        Returns:
            List of messages (oldest first)
        """
        if self.redis is None:
            await self.connect()
        
        key = self._get_key(user_id)
        
        # Get messages (newest first in Redis)
        messages_raw = await self.redis.lrange(key, 0, limit or -1)
        
        # Parse and reverse (to get chronological order)
        messages = [json.loads(msg) for msg in messages_raw]
        messages.reverse()
        
        logger.debug(f"Retrieved {len(messages)} messages for user {user_id}")
        return messages
    
    async def clear_history(self, user_id: int):
        """Clear conversation history for user."""
        if self.redis is None:
            await self.connect()
        
        key = self._get_key(user_id)
        await self.redis.delete(key)
        
        logger.info(f"Cleared history for user {user_id}")
    
    async def get_context_for_llm(
        self,
        user_id: int,
        max_tokens: int = 2000
    ) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for LLM context.
        
        Args:
            user_id: Telegram user ID
            max_tokens: Approximate max tokens (rough estimate: 1 token ~= 4 chars)
        
        Returns:
            List of messages in OpenAI format: [{"role": "user", "content": "..."}]
        """
        history = await self.get_history(user_id)
        
        # Simple token approximation
        max_chars = max_tokens * 4
        total_chars = 0
        result = []
        
        # Start from most recent and work backwards
        for msg in reversed(history):
            msg_chars = len(msg["content"])
            if total_chars + msg_chars > max_chars:
                break
            
            result.insert(0, {
                "role": msg["role"],
                "content": msg["content"]
            })
            total_chars += msg_chars
        
        logger.debug(f"Prepared {len(result)} messages for LLM context (~{total_chars} chars)")
        return result


# Global memory instance (initialize in main app)
conversation_memory: Optional[ConversationMemory] = None


def init_conversation_memory(redis_url: str, **kwargs):
    """Initialize global conversation memory instance."""
    global conversation_memory
    conversation_memory = ConversationMemory(redis_url, **kwargs)
    return conversation_memory


__all__ = ["ConversationMemory", "conversation_memory", "init_conversation_memory"]
