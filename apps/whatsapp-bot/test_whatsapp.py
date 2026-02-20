"""
Test Suite for WhatsApp Bot
Tests core functionality without requiring live WhatsApp API
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json

# Test configuration
pytestmark = pytest.mark.asyncio


class TestWhatsAppClient:
    """Test WhatsApp API client"""
    
    async def test_send_text_message(self):
        """Test sending simple text message"""
        from core.whatsapp_client import WhatsAppClient
        
        client = WhatsAppClient()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "messages": [{"id": "wamid.123"}]
            }
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.send_text(
                to="77001234567",
                text="Test message"
            )
            
            assert result is not None
            assert "messages" in result
    
    async def test_send_buttons(self):
        """Test sending message with buttons (max 3)"""
        from core.whatsapp_client import WhatsAppClient
        
        client = WhatsAppClient()
        
        buttons = [
            {"id": "btn_1", "title": "Yes"},
            {"id": "btn_2", "title": "No"},
            {"id": "btn_3", "title": "Maybe"}
        ]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"messages": [{"id": "wamid.123"}]}
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.send_buttons(
                to="77001234567",
                text="Choose an option:",
                buttons=buttons
            )
            
            assert result is not None
    
    async def test_send_list_message(self):
        """Test sending interactive list"""
        from core.whatsapp_client import WhatsAppClient
        
        client = WhatsAppClient()
        
        sections = [{
            "title": "Products",
            "rows": [
                {"id": "prod_1", "title": "Sofa", "description": "Gray sofa"},
                {"id": "prod_2", "title": "Table", "description": "Wood table"}
            ]
        }]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"messages": [{"id": "wamid.123"}]}
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            result = await client.send_list(
                to="77001234567",
                header="Products",
                body="Choose a product:",
                button_text="Select",
                sections=sections
            )
            
            assert result is not None


class TestAIAssistant:
    """Test AI assistant with context awareness"""
    
    async def test_simple_chat(self):
        """Test basic chat without function calls"""
        from core.ai_assistant import EnhancedAIAssistant
        
        assistant = EnhancedAIAssistant()
        
        with patch.object(assistant.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Hello! How can I help?"
            mock_response.choices[0].message.function_call = None
            mock_create.return_value = mock_response
            
            result = await assistant.chat(
                user_message="Hello",
                conversation_history=[],
                user_context={}
            )
            
            assert result["message"] == "Hello! How can I help?"
            assert result["function_call"] is None
            assert result["intent"] in ["browsing", "question"]
    
    async def test_product_search_function_call(self):
        """Test AI calling search_products function"""
        from core.ai_assistant import EnhancedAIAssistant
        
        assistant = EnhancedAIAssistant()
        
        with patch.object(assistant.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = None
            mock_response.choices[0].message.function_call = Mock()
            mock_response.choices[0].message.function_call.name = "search_products"
            mock_response.choices[0].message.function_call.arguments = json.dumps({
                "query": "gray sofa",
                "category": "диваны",
                "limit": 5
            })
            mock_create.return_value = mock_response
            
            result = await assistant.chat(
                user_message="Нужен серый диван",
                conversation_history=[],
                user_context={}
            )
            
            assert result["function_call"] is not None
            assert result["function_call"]["name"] == "search_products"
            assert "query" in result["function_call"]["arguments"]
    
    async def test_preference_extraction(self):
        """Test extracting user preferences from message"""
        from core.ai_assistant import EnhancedAIAssistant
        
        assistant = EnhancedAIAssistant()
        
        preferences = assistant._extract_preferences(
            message="Нужен белый диван из кожи",
            history=[]
        )
        
        assert "белый" in preferences.get("colors", [])
        assert any("кожа" in m for m in preferences.get("materials", []))
    
    async def test_intent_detection(self):
        """Test detecting user intent"""
        from core.ai_assistant import EnhancedAIAssistant
        
        assistant = EnhancedAIAssistant()
        
        # Buying intent
        intent1 = assistant._detect_intent("Хочу купить этот диван", [])
        assert intent1 == "buying"
        
        # Comparison intent
        intent2 = assistant._detect_intent("Сравни эти два товара", [])
        assert intent2 == "comparing"
        
        # Question intent
        intent3 = assistant._detect_intent("Какая цена?", [])
        assert intent3 == "question"
        
        # Browsing intent (default)
        intent4 = assistant._detect_intent("Покажи диваны", [])
        assert intent4 == "browsing"


class TestConversationMemory:
    """Test Redis-based conversation memory"""
    
    async def test_save_and_retrieve_message(self):
        """Test saving message to Redis"""
        from core.memory import ConversationMemory
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            memory = ConversationMemory(redis_url="redis://localhost:6379")
            await memory.connect()
            
            await memory.save_message(
                user_id=123,
                role="user",
                content="Test message"
            )
            
            # Verify lpush was called
            mock_redis_client.lpush.assert_called_once()
            mock_redis_client.ltrim.assert_called_once()
            mock_redis_client.expire.assert_called_once()
    
    async def test_get_history(self):
        """Test retrieving conversation history"""
        from core.memory import ConversationMemory
        
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis_client = AsyncMock()
            mock_redis_client.lrange.return_value = [
                json.dumps({"role": "user", "content": "Hello"}),
                json.dumps({"role": "assistant", "content": "Hi!"})
            ]
            mock_redis.return_value = mock_redis_client
            
            memory = ConversationMemory(redis_url="redis://localhost:6379")
            await memory.connect()
            
            history = await memory.get_history(user_id=123)
            
            assert len(history) == 2
            assert history[0]["role"] == "user"
            assert history[1]["role"] == "assistant"


class TestProductSearch:
    """Test product search API"""
    
    async def test_search_products(self):
        """Test product search"""
        from core.product_search import ProductSearchAPI
        
        api = ProductSearchAPI()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "products": [
                    {"sku": "SOFA-123", "name": "Gray Sofa"},
                    {"sku": "SOFA-456", "name": "White Sofa"}
                ]
            }
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            products = await api.search_products(query="sofa", limit=5)
            
            assert len(products) == 2
            assert products[0]["sku"] == "SOFA-123"
    
    async def test_get_product_by_sku(self):
        """Test getting single product"""
        from core.product_search import ProductSearchAPI
        
        api = ProductSearchAPI()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                "sku": "SOFA-123",
                "name": "Gray Sofa",
                "price": 95000
            }
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            product = await api.get_product_by_sku("SOFA-123")
            
            assert product is not None
            assert product["sku"] == "SOFA-123"


class TestUserContext:
    """Test user context tracking"""
    
    async def test_save_and_get_user_context(self):
        """Test saving user preferences"""
        from core.user_context import update_user_preferences, get_user_context
        
        with patch('core.memory.conversation_memory') as mock_memory:
            mock_memory.redis = AsyncMock()
            mock_memory.redis.get.return_value = None
            mock_memory.redis.setex = AsyncMock()
            
            # Save preferences
            await update_user_preferences(
                phone="77001234567",
                preferences={"colors": ["белый", "серый"]}
            )
            
            # Verify setex was called
            mock_memory.redis.setex.assert_called_once()
    
    async def test_track_viewed_products(self):
        """Test tracking viewed products"""
        from core.user_context import track_viewed_products, get_user_context
        
        with patch('core.memory.conversation_memory') as mock_memory:
            mock_memory.redis = AsyncMock()
            mock_memory.redis.get.return_value = json.dumps({
                "viewed_products": ["SOFA-111"],
                "preferences": {},
                "language": "ru"
            })
            mock_memory.redis.setex = AsyncMock()
            
            await track_viewed_products(
                phone="77001234567",
                sku_list=["SOFA-222", "SOFA-333"]
            )
            
            # Verify products were added
            mock_memory.redis.setex.assert_called_once()


class TestRateLimiter:
    """Test rate limiting"""
    
    def test_rate_limit_check(self):
        """Test rate limit checking"""
        from core.rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        user_id = "77001234567"
        
        # First 5 requests should pass
        for i in range(5):
            assert limiter.check_rate_limit(user_id) is True
        
        # 6th request should fail
        assert limiter.check_rate_limit(user_id) is False


class TestMessageHandlers:
    """Test message handlers"""
    
    async def test_handle_text_message(self):
        """Test text message handling"""
        from handlers.messages import handle_text_message
        
        message = {
            "from": "77001234567",
            "id": "wamid.123",
            "text": {"body": "Hello"}
        }
        
        with patch('handlers.messages.whatsapp_client') as mock_client, \
             patch('handlers.messages.ai_assistant') as mock_ai, \
             patch('handlers.messages.conversation_memory') as mock_memory:
            
            mock_client.mark_as_read = AsyncMock()
            mock_client.send_text = AsyncMock()
            mock_memory.get_context_for_llm = AsyncMock(return_value=[])
            mock_memory.save_message = AsyncMock()
            mock_ai.chat = AsyncMock(return_value={
                "message": "Hello! How can I help?",
                "function_call": None,
                "intent": "question",
                "extracted_preferences": {}
            })
            
            await handle_text_message(message)
            
            # Verify message was marked as read
            mock_client.mark_as_read.assert_called_once_with("wamid.123")
            
            # Verify response was sent
            mock_client.send_text.assert_called_once()


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
