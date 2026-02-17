"""
AI Assistant Module - OpenAI integration for natural conversation
"""
import os
import json
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """Ты - ассистент мебельного магазина "Zeta Furniture" в Талдыкоргане.

Твоя задача:
- Понимать запросы клиентов на естественном языке (русский и казахский)
- Задавать уточняющие вопросы когда нужно (но не навязчиво!)
- Искать товары в каталоге (37,000+ позиций мебели)
- Рекомендовать подходящие варианты
- Помогать с заказом

Стиль общения:
- Дружелюбный, профессиональный
- Без излишней формальности
- Короткие понятные ответы
- Используй эмодзи умеренно (🪑 для мебели, ✅ для подтверждений)

У тебя есть функция search_products() - используй её когда клиент ищет товар.

Важно:
- Цены уточняй у менеджера (не придумывай!)
- Наличие уточняй у менеджера
- Доставку уточняй у менеджера
"""

FUNCTIONS = [
    {
        "name": "search_products",
        "description": "Поиск товаров в каталоге по описанию, категории, материалу",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Поисковый запрос (название товара, категория, материал, цвет)"
                },
                "category": {
                    "type": "string",
                    "description": "Категория товара если понятна из запроса"
                },
                "material": {
                    "type": "string",
                    "description": "Материал (пластик, дерево, металл, кожа и т.д.)"
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "description": "Количество результатов (обычно 3-5)"
                }
            },
            "required": ["query"]
        }
    }
]


async def chat_with_ai(user_message: str, conversation_history: list) -> dict:
    """
    Send message to OpenAI and get response
    
    Args:
        user_message: User's text message
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        {
            "message": "AI response text" or None,
            "function_call": {"name": "search_products", "arguments": {...}} or None,
            "needs_buttons": True/False
        }
    """
    
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation_history[-20:],  # Last 20 messages for context
            {"role": "user", "content": user_message}
        ]
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            functions=FUNCTIONS,
            function_call="auto",
            temperature=0.7,
            max_tokens=500
        )
        
        choice = response.choices[0]
        
        # If AI wants to call a function (search products)
        if choice.message.function_call:
            func_name = choice.message.function_call.name
            func_args = json.loads(choice.message.function_call.arguments)
            
            logger.info(f"AI called function: {func_name} with args: {func_args}")
            
            return {
                "message": None,
                "function_call": {
                    "name": func_name,
                    "arguments": func_args
                },
                "needs_buttons": True
            }
        
        # Regular text response
        return {
            "message": choice.message.content,
            "function_call": None,
            "needs_buttons": False
        }
    
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return {
            "message": "Извините, произошла ошибка. Попробуйте ещё раз или обратитесь к менеджеру.",
            "function_call": None,
            "needs_buttons": False
        }
