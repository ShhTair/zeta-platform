"""
Callback query handlers for inline buttons
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from handlers.start import ConversationState

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith("product_"))
async def show_product_details(callback: CallbackQuery, state: FSMContext):
    """
    Show detailed product information with action buttons
    Triggered when user clicks on a product from search results
    """
    api_client = callback.message.bot.get("api_client")
    
    # Extract SKU/ID from callback data
    sku = callback.data.split("_", 1)[1]
    
    # Get product details from state or fetch from API
    state_data = await state.get_data()
    products = state_data.get("products", [])
    
    # Find the product
    product = None
    for p in products:
        if str(p.get("id")) == sku or p.get("sku") == sku:
            product = p
            break
    
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
    
    # Format product details
    name = product.get("name", "Товар")
    sku_display = product.get("sku") or product.get("id", "N/A")
    description = product.get("description", "Описание отсутствует")
    price = product.get("price", 0)
    stock = product.get("stock", 0)
    image_url = product.get("image_url")
    
    message_text = f"""
🪑 <b>{name}</b>

📦 Артикул: <code>{sku_display}</code>
📝 {description}

💰 Цена: <b>{price} ₽</b>
📍 В наличии: {"✅ Да" if stock > 0 else "⏳ Уточните у менеджера"}
    """
    
    # Action buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Заказать", callback_data=f"order_{sku}")],
        [InlineKeyboardButton(text="📸 Посмотреть фото", callback_data=f"photo_{sku}")],
        [InlineKeyboardButton(text="↩️ Назад к поиску", callback_data="back_to_search")]
    ])
    
    # If product has image, send it with caption
    if image_url:
        try:
            await callback.message.answer_photo(
                photo=image_url,
                caption=message_text,
                reply_markup=keyboard
            )
            # Delete the original message with product list
            await callback.message.delete()
        except Exception as e:
            logger.warning(f"Failed to send product image: {e}")
            # Fallback to text message
            await callback.message.edit_text(
                message_text,
                reply_markup=keyboard
            )
    else:
        # Text-only message
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard
        )
    
    await callback.answer()
    await state.update_data(current_product=product)
    
    logger.info(f"User {callback.from_user.id} viewed product: {sku}")


@router.callback_query(F.data.startswith("order_"))
async def handle_order_request(callback: CallbackQuery, state: FSMContext):
    """
    Handle order request - escalate to manager or create Bitrix deal
    """
    api_client = callback.message.bot.get("api_client")
    city_id = "default"  # Default city for now
    
    sku = callback.data.split("_", 1)[1]
    state_data = await state.get_data()
    product = state_data.get("current_product")
    
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
    
    # Create escalation message
    user = callback.from_user
    customer_name = user.full_name or user.username or "Клиент"
    customer_telegram = f"@{user.username}" if user.username else f"ID: {user.id}"
    
    message = f"Запрос на заказ: {product.get('name')} (Артикул: {sku})"
    
    try:
        # Create Bitrix deal
        result = await api_client.create_bitrix_deal(
            customer_name=customer_name,
            customer_telegram=customer_telegram,
            product_id=sku,
            message=message,
            city_id=city_id
        )
        
        response = "✅ <b>Заявка создана!</b>\n\n"
        response += f"Заявка №{result.get('deal_id')} передана менеджеру.\n"
        response += "Мы свяжемся с вами в ближайшее время!"
        
        await callback.message.answer(response)
        await callback.answer("Заявка отправлена!")
        
        logger.info(f"Order request created: deal_id={result.get('deal_id')}")
        
    except Exception as e:
        logger.error(f"Failed to create order: {e}")
        await callback.answer(
            "Не удалось создать заявку. Пожалуйста, свяжитесь с менеджером напрямую.",
            show_alert=True
        )


@router.callback_query(F.data.startswith("photo_"))
async def show_product_photo(callback: CallbackQuery, state: FSMContext):
    """
    Show additional product photos
    """
    state_data = await state.get_data()
    product = state_data.get("current_product")
    
    if not product:
        await callback.answer("Товар не найден", show_alert=True)
        return
    
    image_url = product.get("image_url")
    
    if image_url:
        await callback.message.answer_photo(
            photo=image_url,
            caption=f"📸 {product.get('name')}"
        )
        await callback.answer()
    else:
        await callback.answer(
            "Фото товара отсутствует. Уточните у менеджера!",
            show_alert=True
        )


@router.callback_query(F.data == "back_to_search")
async def back_to_search(callback: CallbackQuery, state: FSMContext):
    """
    Return to product search - show original search results
    """
    state_data = await state.get_data()
    products = state_data.get("products", [])
    query = state_data.get("query", "")
    
    if not products:
        await callback.message.answer(
            "🔍 Введите новый поисковый запрос:"
        )
        await callback.answer()
        await state.set_state(ConversationState.product_inquiry)
        return
    
    # Re-display search results
    response = f"📦 <b>Результаты поиска:</b> \"{query}\"\n\n"
    
    keyboard_buttons = []
    for product in products:
        name = product.get("name", "Товар")
        price = product.get("price", 0)
        sku = product.get("sku") or product.get("id")
        
        # Truncate long names for buttons
        button_text = f"🪑 {name[:40]}" + ("..." if len(name) > 40 else "")
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"product_{sku}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(response, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("filter_"))
async def handle_filter_selection(callback: CallbackQuery, state: FSMContext):
    """
    Handle clarifying question filters (home, office, kids, all)
    """
    api_client = callback.message.bot.get("api_client")
    city_id = "default"  # Default city for now
    
    filter_type = callback.data.split("_", 1)[1]
    state_data = await state.get_data()
    original_query = state_data.get("vague_query", "")
    
    # Map filter to search modifier
    filter_modifiers = {
        "home": "для дома",
        "office": "для офиса",
        "kids": "детский",
        "all": ""
    }
    
    modifier = filter_modifiers.get(filter_type, "")
    enhanced_query = f"{original_query} {modifier}".strip()
    
    await callback.answer(f"Ищу: {enhanced_query}")
    
    # Show searching message
    search_msg = "🔍 Ищу в каталоге..."
    status = await callback.message.edit_text(search_msg)
    
    # Search products with enhanced query
    products = await api_client.search_products(
        query=enhanced_query,
        city_id=city_id,
        limit=7
    )
    
    if not products:
        no_results = "😔 К сожалению, ничего не найдено. Попробуйте другой запрос или свяжитесь с менеджером."
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 Связаться с менеджером", callback_data="escalate:manager")],
            [InlineKeyboardButton(text="🎫 Создать заявку", callback_data="escalate:ticket")]
        ])
        
        await status.edit_text(no_results, reply_markup=keyboard)
        await state.set_state(ConversationState.escalation)
        return
    
    # Show products with inline buttons
    response = f"📦 <b>Найдено:</b> \"{enhanced_query}\"\n\n"
    
    keyboard_buttons = []
    for product in products[:7]:  # Limit to 7 products
        name = product.get("name", "Товар")
        sku = product.get("sku") or product.get("id")
        
        button_text = f"🪑 {name[:40]}" + ("..." if len(name) > 40 else "")
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"product_{sku}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await status.edit_text(response, reply_markup=keyboard)
    await state.update_data(query=enhanced_query, products=products)
    
    logger.info(f"User {callback.from_user.id} filtered search: {enhanced_query}")
