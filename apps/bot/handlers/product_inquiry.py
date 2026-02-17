"""
Product inquiry handler - Search catalog and respond
"""
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.start import ConversationState

logger = logging.getLogger(__name__)

router = Router()


@router.message(ConversationState.product_inquiry, F.text)
async def handle_product_inquiry(message: types.Message, state: FSMContext):
    """Handle product inquiry"""
    api_client = message.bot["api_client"]
    prompt_manager = message.bot["prompt_manager"]
    
    query = message.text
    city_id = prompt_manager.city_id
    
    # Show searching message
    search_msg = await prompt_manager.get_prompt(
        "catalog_search",
        default="🔍 Ищу в каталоге..."
    )
    status = await message.answer(search_msg)
    
    # Search products
    products = await api_client.search_products(
        query=query,
        city_id=city_id,
        limit=5
    )
    
    await status.delete()
    
    if not products:
        no_results = await prompt_manager.get_prompt(
            "no_results",
            default="😔 К сожалению, ничего не найдено. Попробуйте другой запрос или свяжитесь с менеджером."
        )
        
        # Offer escalation
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 Связаться с менеджером", callback_data="escalate:manager")],
            [InlineKeyboardButton(text="🎫 Создать заявку", callback_data="escalate:ticket")]
        ])
        
        await message.answer(no_results, reply_markup=keyboard)
        await state.set_state(ConversationState.escalation)
        return
    
    # Format results
    response = "📦 <b>Найденные товары:</b>\n\n"
    
    keyboard_buttons = []
    for i, product in enumerate(products, 1):
        name = product.get("name", "Товар")
        price = product.get("price", 0)
        product_id = product.get("id")
        
        response += f"{i}. <b>{name}</b>\n"
        response += f"   💰 Цена: {price} ₽\n\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"🔗 {name}",
                callback_data=f"product:{product_id}"
            )
        ])
    
    # Add escalation options
    keyboard_buttons.append([
        InlineKeyboardButton(text="📞 Связаться с менеджером", callback_data="escalate:manager")
    ])
    keyboard_buttons.append([
        InlineKeyboardButton(text="🎫 Создать заявку", callback_data="escalate:ticket")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(response, reply_markup=keyboard)
    await state.update_data(query=query, products=products)
    await state.set_state(ConversationState.escalation)
    
    logger.info(f"User {message.from_user.id} searched: {query}")


@router.callback_query(F.data.startswith("product:"))
async def send_product_link(callback: types.CallbackQuery):
    """Send product link"""
    api_client = callback.message.bot["api_client"]
    prompt_manager = callback.message.bot["prompt_manager"]
    
    product_id = callback.data.split(":")[1]
    
    # In real scenario, fetch full product details
    # For now, construct a link
    product_url = f"https://shop.zeta.com/product/{product_id}"
    
    response = f"🔗 <b>Ссылка на товар:</b>\n{product_url}\n\n"
    response += "Нужна помощь с заказом? Обратитесь к менеджеру!"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Связаться с менеджером", callback_data="escalate:manager")],
        [InlineKeyboardButton(text="🎫 Создать заявку", callback_data="escalate:ticket")]
    ])
    
    await callback.message.answer(response, reply_markup=keyboard)
    await callback.answer()
    
    logger.info(f"User {callback.from_user.id} clicked product: {product_id}")
