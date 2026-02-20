"""
Main Message Handler
Processes all incoming text messages with AI
"""

import logging
from typing import Dict, Any

from core.whatsapp_client import whatsapp_client
from core.ai_assistant import ai_assistant
from core.memory import conversation_memory
from core.product_search import product_api
from core.rate_limiter import RateLimiter
from handlers.interactive import send_product_list, send_product_details

logger = logging.getLogger(__name__)

# Rate limiter
rate_limiter = RateLimiter(max_requests=20, window_seconds=60)


async def handle_text_message(message: Dict[str, Any]):
    """
    Handle incoming text message.
    
    Flow:
    1. Extract user info and message
    2. Check rate limit
    3. Get conversation history from Redis
    4. Send to AI assistant
    5. Execute function calls (search, recommend, etc.)
    6. Send response with interactive elements
    7. Save to conversation memory
    """
    try:
        # Extract message data
        from_number = message.get("from")
        message_id = message.get("id")
        text = message.get("text", {}).get("body", "")
        
        if not text:
            return
        
        logger.info(f"📥 Message from {from_number}: {text[:100]}")
        
        # Check rate limit
        if not rate_limiter.check_rate_limit(from_number):
            await whatsapp_client.send_text(
                to=from_number,
                text="⚠️ Слишком много сообщений. Пожалуйста, подождите немного."
            )
            return
        
        # Mark as read
        await whatsapp_client.mark_as_read(message_id)
        
        # Get conversation history
        history = await conversation_memory.get_context_for_llm(
            user_id=int(from_number) if from_number.isdigit() else hash(from_number),
            max_tokens=2000
        )
        
        # Get user context (viewed products, preferences)
        user_context = await _get_user_context(from_number)
        
        # Send to AI
        ai_response = await ai_assistant.chat(
            user_message=text,
            conversation_history=history,
            user_context=user_context
        )
        
        # Save user message to memory
        await conversation_memory.save_message(
            user_id=int(from_number) if from_number.isdigit() else hash(from_number),
            role="user",
            content=text
        )
        
        # Handle function calls
        if ai_response["function_call"]:
            await _handle_function_call(
                from_number=from_number,
                function_call=ai_response["function_call"],
                user_context=user_context
            )
        
        # Send text response
        elif ai_response["message"]:
            await whatsapp_client.send_text(
                to=from_number,
                text=ai_response["message"]
            )
            
            # Save assistant response to memory
            await conversation_memory.save_message(
                user_id=int(from_number) if from_number.isdigit() else hash(from_number),
                role="assistant",
                content=ai_response["message"]
            )
        
        # Update user context with extracted preferences
        if ai_response.get("extracted_preferences"):
            await _update_user_context(from_number, ai_response["extracted_preferences"])
    
    except Exception as e:
        logger.error(f"❌ Error handling message: {e}", exc_info=True)
        await whatsapp_client.send_text(
            to=from_number,
            text="😔 Произошла ошибка. Попробуйте ещё раз или напишите менеджеру."
        )


async def _handle_function_call(
    from_number: str,
    function_call: Dict[str, Any],
    user_context: Dict[str, Any]
):
    """Execute AI function calls"""
    func_name = function_call["name"]
    func_args = function_call["arguments"]
    
    logger.info(f"🔧 Executing function: {func_name}({func_args})")
    
    try:
        # Search products
        if func_name == "search_products":
            products = await product_api.search_products(**func_args)
            
            if not products:
                await whatsapp_client.send_text(
                    to=from_number,
                    text="😔 К сожалению, ничего не нашёл по вашему запросу.\n\nПопробуйте уточнить или спросите по-другому!"
                )
                return
            
            # Send product list (interactive list message)
            await send_product_list(
                to=from_number,
                products=products,
                header="Вот что нашёл! 🪑",
                body=f"Нашёл {len(products)} вариантов. Выберите товар для подробностей:"
            )
            
            # Track viewed products
            await _track_viewed_products(from_number, [p["sku"] for p in products])
        
        # Get product details
        elif func_name == "get_product_details":
            product = await product_api.get_product_by_sku(func_args["sku"])
            
            if not product:
                await whatsapp_client.send_text(
                    to=from_number,
                    text="😔 Товар не найден."
                )
                return
            
            await send_product_details(to=from_number, product=product)
        
        # Compare products
        elif func_name == "compare_products":
            products = await product_api.compare_products(func_args["sku_list"])
            
            if len(products) < 2:
                await whatsapp_client.send_text(
                    to=from_number,
                    text="Не могу сравнить - недостаточно товаров."
                )
                return
            
            # Format comparison
            comparison_text = _format_product_comparison(products)
            await whatsapp_client.send_text(
                to=from_number,
                text=comparison_text
            )
        
        # Recommend products
        elif func_name == "recommend_products":
            products = await product_api.recommend_products(**func_args)
            
            if not products:
                await whatsapp_client.send_text(
                    to=from_number,
                    text="Пока не могу подобрать рекомендации. Попробуйте указать предпочтения!"
                )
                return
            
            await send_product_list(
                to=from_number,
                products=products,
                header="Рекомендую! ⭐",
                body="Эти товары могут вам понравиться:"
            )
        
        # Setup price alert
        elif func_name == "setup_price_alert":
            # Save to Redis
            from core.alerts import save_price_alert
            await save_price_alert(
                user_phone=from_number,
                sku=func_args["sku"],
                target_price=func_args.get("target_price")
            )
            
            await whatsapp_client.send_text(
                to=from_number,
                text="✅ Отлично! Я уведомлю вас, когда цена снизится.\n\nМожете продолжить поиск!"
            )
        
        # Save search
        elif func_name == "save_search":
            from core.alerts import save_search_query
            await save_search_query(
                user_phone=from_number,
                query=func_args["search_query"],
                category=func_args.get("category")
            )
            
            await whatsapp_client.send_text(
                to=from_number,
                text="✅ Поиск сохранён! Я буду присылать новые подходящие товары."
            )
    
    except Exception as e:
        logger.error(f"❌ Function call error: {e}", exc_info=True)
        await whatsapp_client.send_text(
            to=from_number,
            text="Произошла ошибка. Попробуйте ещё раз!"
        )


async def _get_user_context(phone: str) -> Dict[str, Any]:
    """Get user context from Redis"""
    from core.user_context import get_user_context
    return await get_user_context(phone)


async def _update_user_context(phone: str, preferences: Dict[str, Any]):
    """Update user preferences in Redis"""
    from core.user_context import update_user_preferences
    await update_user_preferences(phone, preferences)


async def _track_viewed_products(phone: str, sku_list: list):
    """Track which products user viewed"""
    from core.user_context import track_viewed_products
    await track_viewed_products(phone, sku_list)


def _format_product_comparison(products: list) -> str:
    """Format product comparison as text"""
    lines = ["📊 *Сравнение товаров:*\n"]
    
    for i, product in enumerate(products, 1):
        lines.append(f"*{i}. {product['name']}*")
        lines.append(f"   📦 Артикул: {product['sku']}")
        lines.append(f"   📏 Размеры: {product.get('dimensions', 'не указаны')}")
        lines.append(f"   🎨 Цвет: {product.get('color', 'не указан')}")
        lines.append(f"   🪑 Материал: {product.get('material', 'не указан')}")
        lines.append(f"   💰 Цена: уточните у менеджера")
        lines.append("")
    
    lines.append("Какой вариант больше понравился? Могу рассказать подробнее!")
    
    return "\n".join(lines)


__all__ = ["handle_text_message"]
