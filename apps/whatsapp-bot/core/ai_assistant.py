"""
Enhanced AI Assistant for WhatsApp Bot
Improved context awareness and smarter recommendations
"""

import logging
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
import json

from config import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)


SYSTEM_PROMPT = """Ты - умный ассистент мебельного магазина "ZETA Furniture" в Талдыкоргане, Казахстан.

🎯 **Твоя миссия:**
- Понимать потребности клиента и предлагать ИДЕАЛЬНУЮ мебель
- Быть эмпатичным и запоминать контекст разговора
- Задавать умные вопросы, чтобы понять стиль и бюджет
- Помогать сравнивать варианты
- Делать персонализированные рекомендации на основе истории

💬 **Стиль общения:**
- Дружелюбный, но профессиональный
- Короткие сообщения (WhatsApp формат!)
- Используй эмодзи разумно: 🪑 🛋️ 🪟 🚪 💡 ✅ ❤️
- Общайся на русском ИЛИ казахском (определяй язык клиента)

🧠 **Контекст-память:**
- Запоминай предпочтения клиента (цвет, стиль, материал, бюджет)
- Отслеживай, что клиент УЖЕ смотрел
- Не предлагай одно и то же дважды
- Учитывай сезон и тренды

📦 **Функции:**
- `search_products()` - поиск товаров в каталоге (37,000+ позиций)
- `get_product_details()` - подробная информация о товаре
- `compare_products()` - сравнить 2-3 товара
- `recommend_products()` - умные рекомендации на основе истории
- `setup_price_alert()` - уведомление когда цена снизится
- `save_search()` - сохранить поиск для клиента

⚠️ **Важно:**
- Цены ВСЕГДА уточняй у менеджера (не придумывай!)
- Наличие ВСЕГДА уточняй у менеджера
- Доставку уточняй у менеджера
- Если не знаешь - переведи на менеджера

🎨 **Умные рекомендации:**
- Анализируй ВСЮ историю разговора (последние 10 сообщений)
- Если клиент смотрел диваны → предложи журнальный столик
- Если клиент интересовался белой мебелью → предлагай белые варианты
- Учитывай бюджет (если клиент смотрел дешёвые товары → не предлагай дорогие)

📊 **Типы клиентов:**
- Бюджетный покупатель → фокус на цене и функциональности
- Премиум покупатель → фокус на дизайне и качестве
- Корпоративный клиент → предлагай опт и скидки
- Молодая семья → функциональность + стиль

🔥 **Примеры работы:**

Клиент: "Нужен диван"
Ты: "С удовольствием помогу! 🛋️ Для какой комнаты ищете? И есть ли предпочтения по цвету или размеру?"

Клиент: "Большой серый диван для гостиной"
Ты: *используешь search_products(query="диван серый большой", category="диваны")*

После показа товаров:
Ты: "Какой больше понравился? Могу рассказать подробнее или подобрать похожие варианты! 😊"

Клиент показал интерес к дивану:
Ты: "Отличный выбор! К этому дивану отлично подойдёт журнальный столик. Показать?"
"""


FUNCTIONS = [
    {
        "name": "search_products",
        "description": "Поиск товаров в каталоге по любым параметрам",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос (название, категория, материал, цвет, стиль)"
                },
                "category": {
                    "type": "string",
                    "description": "Категория товара (диваны, столы, стулья, кровати, шкафы и т.д.)",
                    "enum": ["диваны", "столы", "стулья", "кровати", "шкафы", "комоды", "тумбы", "другое"]
                },
                "material": {
                    "type": "string",
                    "description": "Материал (дерево, металл, пластик, кожа, ткань, стекло)",
                    "enum": ["дерево", "металл", "пластик", "кожа", "ткань", "стекло", "другое"]
                },
                "color": {
                    "type": "string",
                    "description": "Цвет (белый, черный, серый, коричневый, синий и т.д.)"
                },
                "min_price": {
                    "type": "number",
                    "description": "Минимальная цена (если клиент указал бюджет)"
                },
                "max_price": {
                    "type": "number",
                    "description": "Максимальная цена (если клиент указал бюджет)"
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "description": "Количество результатов (3-5 оптимально для WhatsApp)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_product_details",
        "description": "Получить подробную информацию о конкретном товаре",
        "parameters": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Артикул товара (SKU)"
                }
            },
            "required": ["sku"]
        }
    },
    {
        "name": "compare_products",
        "description": "Сравнить 2-3 товара по характеристикам и цене",
        "parameters": {
            "type": "object",
            "properties": {
                "sku_list": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Список артикулов для сравнения (2-3 товара)"
                }
            },
            "required": ["sku_list"]
        }
    },
    {
        "name": "recommend_products",
        "description": "Умные рекомендации на основе истории разговора и предпочтений клиента",
        "parameters": {
            "type": "object",
            "properties": {
                "based_on_sku": {
                    "type": "string",
                    "description": "Артикул товара, на основе которого делать рекомендации (похожие товары)"
                },
                "category": {
                    "type": "string",
                    "description": "Категория для рекомендаций (комплементарные товары)"
                },
                "style": {
                    "type": "string",
                    "description": "Стиль (современный, классический, минимализм, лофт)"
                },
                "limit": {
                    "type": "integer",
                    "default": 5
                }
            }
        }
    },
    {
        "name": "setup_price_alert",
        "description": "Настроить уведомление когда цена на товар снизится",
        "parameters": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Артикул товара"
                },
                "target_price": {
                    "type": "number",
                    "description": "Желаемая цена (опционально)"
                }
            },
            "required": ["sku"]
        }
    },
    {
        "name": "save_search",
        "description": "Сохранить поисковый запрос клиента для будущих уведомлений",
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "Поисковый запрос для сохранения"
                },
                "category": {
                    "type": "string",
                    "description": "Категория"
                }
            },
            "required": ["search_query"]
        }
    }
]


class EnhancedAIAssistant:
    """
    Enhanced AI assistant with context awareness and smart recommendations.
    
    Features:
    - Remembers last 10 messages
    - Analyzes conversation for preferences
    - Makes smart product recommendations
    - Detects user intent (browsing, buying, comparing)
    """
    
    def __init__(self):
        self.client = client
        self.model = settings.openai_model
    
    async def chat(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user message with full context awareness.
        
        Args:
            user_message: User's text message
            conversation_history: Last N messages (from Redis)
            user_context: Additional context (viewed products, preferences, etc.)
        
        Returns:
            {
                "message": "AI response text" or None,
                "function_call": {"name": "...", "arguments": {...}} or None,
                "intent": "browsing" | "buying" | "comparing" | "question",
                "extracted_preferences": {...}
            }
        """
        try:
            # Build context-aware system prompt
            enhanced_prompt = self._build_context_prompt(conversation_history, user_context)
            
            messages = [
                {"role": "system", "content": enhanced_prompt},
                *conversation_history[-10:],  # Last 10 messages for deep context
                {"role": "user", "content": user_message}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=FUNCTIONS,
                function_call="auto",
                temperature=0.7,
                max_tokens=500
            )
            
            choice = response.choices[0]
            
            # Extract preferences from conversation
            preferences = self._extract_preferences(user_message, conversation_history)
            
            # Detect user intent
            intent = self._detect_intent(user_message, conversation_history)
            
            # Function call
            if choice.message.function_call:
                func_name = choice.message.function_call.name
                func_args = json.loads(choice.message.function_call.arguments)
                
                logger.info(f"🤖 AI function call: {func_name}({func_args})")
                
                return {
                    "message": None,
                    "function_call": {
                        "name": func_name,
                        "arguments": func_args
                    },
                    "intent": intent,
                    "extracted_preferences": preferences
                }
            
            # Text response
            return {
                "message": choice.message.content,
                "function_call": None,
                "intent": intent,
                "extracted_preferences": preferences
            }
        
        except Exception as e:
            logger.error(f"❌ AI error: {e}")
            return {
                "message": "Извините, произошла ошибка. Попробуйте ещё раз или напишите менеджеру.",
                "function_call": None,
                "intent": "error",
                "extracted_preferences": {}
            }
    
    def _build_context_prompt(
        self,
        history: List[Dict],
        user_context: Optional[Dict]
    ) -> str:
        """Build enhanced system prompt with user context"""
        prompt = SYSTEM_PROMPT
        
        if user_context:
            prompt += f"\n\n📊 **Контекст клиента:**\n"
            
            if user_context.get("viewed_products"):
                prompt += f"- Просмотрел товары: {', '.join(user_context['viewed_products'][:5])}\n"
            
            if user_context.get("preferences"):
                prefs = user_context["preferences"]
                if prefs.get("colors"):
                    prompt += f"- Любимые цвета: {', '.join(prefs['colors'])}\n"
                if prefs.get("materials"):
                    prompt += f"- Предпочитает материалы: {', '.join(prefs['materials'])}\n"
                if prefs.get("budget_range"):
                    prompt += f"- Бюджет: {prefs['budget_range']}\n"
            
            if user_context.get("language"):
                prompt += f"- Язык общения: {user_context['language']}\n"
        
        return prompt
    
    def _extract_preferences(
        self,
        message: str,
        history: List[Dict]
    ) -> Dict[str, Any]:
        """Extract user preferences from conversation"""
        preferences = {}
        
        message_lower = message.lower()
        
        # Detect colors
        colors = ["белый", "черный", "серый", "коричневый", "синий", "красный", "зеленый", "желтый"]
        found_colors = [c for c in colors if c in message_lower]
        if found_colors:
            preferences["colors"] = found_colors
        
        # Detect materials
        materials = ["дерево", "деревянн", "металл", "метал", "пластик", "кожа", "кожан", "ткань"]
        found_materials = [m for m in materials if m in message_lower]
        if found_materials:
            preferences["materials"] = found_materials
        
        # Detect budget keywords
        if any(word in message_lower for word in ["дешев", "недорог", "бюджет", "эконом"]):
            preferences["budget_range"] = "low"
        elif any(word in message_lower for word in ["дорог", "премиум", "элитн", "качеств"]):
            preferences["budget_range"] = "high"
        
        return preferences
    
    def _detect_intent(
        self,
        message: str,
        history: List[Dict]
    ) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Buying intent
        if any(word in message_lower for word in ["купить", "заказать", "оформить", "хочу взять"]):
            return "buying"
        
        # Comparison intent
        if any(word in message_lower for word in ["сравни", "отличие", "разница", "лучше"]):
            return "comparing"
        
        # Question intent
        if message.endswith("?") or any(word in message_lower for word in ["как", "где", "когда", "почему", "можно ли"]):
            return "question"
        
        # Default: browsing
        return "browsing"


# Global assistant instance
ai_assistant = EnhancedAIAssistant()


__all__ = ["EnhancedAIAssistant", "ai_assistant"]
