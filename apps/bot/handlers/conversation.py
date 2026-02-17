"""
Conversation Handler - AI-powered natural language processing
"""
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.ai_assistant import chat_with_ai
from core.api_client import search_products_api, get_product_by_sku

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_message(message: types.Message, state: FSMContext):
    """Handle all text messages with AI"""
    
    # Get conversation history from state
    data = await state.get_data()
    history = data.get("history", [])
    
    logger.info(f"User {message.from_user.id}: {message.text}")
    
    # Send to AI
    ai_response = await chat_with_ai(message.text, history)
    
    # If AI wants to search products
    if ai_response["function_call"]:
        func = ai_response["function_call"]
        
        if func["name"] == "search_products":
            # Search in DB via API
            products = await search_products_api(**func["arguments"])
            
            if not products:
                await message.answer("К сожалению, ничего не нашёл по вашему запросу 😔\n\nПопробуйте уточнить, что именно вы ищете!")
                return
            
            # Show products with inline buttons
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"🪑 {p['name'][:50]}{'...' if len(p['name']) > 50 else ''}",
                    callback_data=f"product_{p['sku']}"
                )]
                for p in products[:5]
            ])
            
            count_text = f"{len(products)} вариант" if len(products) == 1 else f"{len(products)} варианта" if len(products) < 5 else f"{len(products)} вариантов"
            
            await message.answer(
                f"Нашёл {count_text}! Выберите товар для подробностей:",
                reply_markup=keyboard
            )
    
    # Regular AI response
    elif ai_response["message"]:
        await message.answer(ai_response["message"])
    
    # Update history
    history.append({"role": "user", "content": message.text})
    if ai_response["message"]:
        history.append({"role": "assistant", "content": ai_response["message"]})
    
    # Keep last 20 messages
    await state.update_data(history=history[-20:])


@router.callback_query(F.data.startswith("product_"))
async def show_product_details(callback: types.CallbackQuery):
    """Show detailed product information when user clicks product button"""
    
    sku = callback.data.split("_", 1)[1]
    
    logger.info(f"User {callback.from_user.id} requested product: {sku}")
    
    # Get product from API
    product = await get_product_by_sku(sku)
    
    if not product:
        await callback.answer("Товар не найден 😔", show_alert=True)
        return
    
    # Format product details
    details = f"""
🪑 **{product.get('name', 'Без названия')}**

📦 **Артикул:** {product.get('sku', 'N/A')}

📝 **Описание:**
{product.get('description', 'Описание отсутствует')[:500]}

📏 **Характеристики:**
• Материал: {product.get('material', 'не указан')}
• Цвет: {product.get('color', 'не указан')}
• Размеры: {product.get('dimensions', 'не указаны')}

💰 **Цена и наличие:** Уточните у менеджера
🚚 **Доставка:** Уточните у менеджера
"""
    
    # Action buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Фото", callback_data=f"photo_{sku}")],
        [InlineKeyboardButton(text="🛒 Заказать", callback_data=f"order_{sku}")],
        [InlineKeyboardButton(text="↩️ Назад к списку", callback_data="back_to_search")]
    ])
    
    await callback.message.edit_text(
        details,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("photo_"))
async def show_product_photo(callback: types.CallbackQuery):
    """Show product photos"""
    
    sku = callback.data.split("_", 1)[1]
    product = await get_product_by_sku(sku)
    
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
    
    # Get image URL
    image_url = product.get('link') or product.get('primary_image')
    
    if image_url:
        try:
            await callback.message.answer_photo(
                photo=image_url,
                caption=f"🪑 {product.get('name', 'Товар')}\n📦 Артикул: {sku}"
            )
            await callback.answer("Фото отправлено!")
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            await callback.answer("К сожалению, не удалось загрузить фото 😔", show_alert=True)
    else:
        await callback.answer("Фото отсутствует", show_alert=True)


@router.callback_query(F.data.startswith("order_"))
async def order_product(callback: types.CallbackQuery):
    """Handle product order"""
    
    sku = callback.data.split("_", 1)[1]
    
    await callback.answer("Для заказа обратитесь к менеджеру!", show_alert=True)
    
    # You can integrate with Bitrix24 or other CRM here
    logger.info(f"User {callback.from_user.id} wants to order {sku}")


@router.callback_query(F.data == "back_to_search")
async def back_to_search(callback: types.CallbackQuery):
    """Go back to search results"""
    
    await callback.message.edit_text("Напишите, что вы ищете, и я подберу для вас варианты! 🪑")
    await callback.answer()
