"""
Enhanced Conversation Handler with Interactive UI
Replaces old conversation.py with beautiful inline keyboards
"""
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.start import ConversationState
from handlers.interactive import (
    create_product_list_keyboard,
    create_quick_filters_keyboard,
    send_product_carousel,
    MAX_PRODUCTS_PER_PAGE
)

logger = logging.getLogger(__name__)

router = Router()

# Vague keywords that need clarification
VAGUE_KEYWORDS = [
    'стул', 'стол', 'кровать', 'диван', 'шкаф',
    'кресло', 'тумба', 'полка', 'комод', 'матрас',
    'мебель', 'офисная', 'домашняя'
]


def is_vague_query(query: str) -> bool:
    """
    Check if query needs clarification
    Returns True for short generic queries
    """
    query_lower = query.lower().strip()
    words = query_lower.split()
    
    has_vague_keyword = any(kw in query_lower for kw in VAGUE_KEYWORDS)
    is_short = len(words) <= 2
    
    return has_vague_keyword and is_short


@router.message(ConversationState.product_inquiry, F.text & ~F.text.startswith("/"))
async def handle_product_search(message: types.Message, state: FSMContext):
    """
    Handle product search with smart clarifying questions
    Uses beautiful inline keyboards instead of text responses
    """
    api_client = message.bot.get("api_client")
    query = message.text.strip()
    
    logger.info(f"User {message.from_user.id} search query: {query}")
    
    # Check if query is too vague
    if is_vague_query(query):
        # Show clarifying options
        await message.answer(
            f"🤔 <b>Уточните, пожалуйста</b>\n\n"
            f"Какой именно <b>{query}</b> вас интересует?",
            reply_markup=create_quick_filters_keyboard()
        )
        
        # Save vague query to state
        await state.update_data(vague_query=query)
        return
    
    # Query is specific enough - search products
    await perform_product_search(message, state, query, api_client)


async def perform_product_search(
    message: types.Message,
    state: FSMContext,
    query: str,
    api_client,
    show_carousel: bool = False
):
    """
    Execute product search and display results beautifully
    
    Args:
        message: Telegram message
        state: FSM context
        query: Search query
        api_client: API client instance
        show_carousel: If True, show photos as carousel (media group)
    """
    # Show "searching..." indicator
    status_msg = await message.answer("🔍 Ищу в каталоге...")
    
    try:
        # Search products via API
        products = await api_client.search_products(
            query=query,
            city_id="default",
            limit=20  # Fetch more for pagination
        )
        
        await status_msg.delete()
        
        # No results
        if not products:
            no_results_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="💬 Связаться с менеджером",
                    callback_data="action_contact"
                )],
                [InlineKeyboardButton(
                    text="🔄 Новый поиск",
                    callback_data="new_search"
                )]
            ])
            
            await message.answer(
                "😔 <b>Ничего не найдено</b>\n\n"
                "К сожалению, по вашему запросу ничего не нашлось.\n"
                "Попробуйте уточнить запрос или свяжитесь с менеджером!",
                reply_markup=no_results_keyboard
            )
            return
        
        # Save to state
        await state.update_data(
            products=products,
            query=query,
            offset=0
        )
        
        # Display results
        count_text = format_product_count(len(products))
        
        # Option 1: Photo carousel (if products have images)
        if show_carousel:
            products_with_images = [
                p for p in products[:10]
                if p.get("image_url") or p.get("primary_image")
            ]
            
            if products_with_images:
                await send_product_carousel(message, products_with_images, state)
                logger.info(f"Sent carousel with {len(products_with_images)} photos")
                return
        
        # Option 2: Interactive button list (default)
        response = f"📦 <b>Нашёл {count_text}!</b>\n\n"
        response += f"По запросу: «{query}»\n"
        response += "Выберите товар для подробностей:"
        
        keyboard = create_product_list_keyboard(
            products,
            offset=0,
            show_more=True
        )
        
        await message.answer(response, reply_markup=keyboard)
        logger.info(f"Found {len(products)} products for query: {query}")
    
    except Exception as e:
        logger.error(f"Product search failed: {e}")
        await status_msg.delete()
        await message.answer(
            "❌ <b>Ошибка поиска</b>\n\n"
            "Не удалось выполнить поиск. Попробуйте ещё раз или свяжитесь с поддержкой."
        )


def format_product_count(count: int) -> str:
    """Format product count in Russian"""
    if count == 1:
        return "1 товар"
    elif 2 <= count <= 4:
        return f"{count} товара"
    else:
        return f"{count} товаров"


# ==================== FILTER CALLBACK HANDLERS ====================

@router.callback_query(F.data.startswith("filter_"))
async def apply_search_filter(callback: types.CallbackQuery, state: FSMContext):
    """
    Apply quick filter from clarifying question
    """
    api_client = callback.message.bot.get("api_client")
    filter_type = callback.data.split("_", 1)[1]
    
    state_data = await state.get_data()
    original_query = state_data.get("vague_query", "")
    
    # Map filter to query modifier
    filter_map = {
        "home": "для дома",
        "office": "для офиса",
        "color": "",  # Will ask user to specify color
        "price": "",  # Will ask user to specify price range
        "all": ""
    }
    
    modifier = filter_map.get(filter_type, "")
    
    # Special handling for color/price filters
    if filter_type == "color":
        await callback.message.edit_text(
            f"🎨 <b>Какой цвет {original_query}?</b>\n\n"
            "Напишите цвет (например: белый, чёрный, серый, бежевый):",
            reply_markup=None
        )
        await state.update_data(filter_stage="color")
        await callback.answer()
        return
    
    elif filter_type == "price":
        price_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💸 До 50,000 ₸", callback_data="price_low")],
            [InlineKeyboardButton(text="💰 50,000 - 150,000 ₸", callback_data="price_mid")],
            [InlineKeyboardButton(text="💎 Более 150,000 ₸", callback_data="price_high")],
            [InlineKeyboardButton(text="📋 Показать все", callback_data="price_all")]
        ])
        
        await callback.message.edit_text(
            f"💰 <b>Какой бюджет на {original_query}?</b>",
            reply_markup=price_keyboard
        )
        await callback.answer()
        return
    
    # Build enhanced query
    enhanced_query = f"{original_query} {modifier}".strip()
    
    await callback.answer(f"Поиск: {enhanced_query}")
    
    # Show searching status
    await callback.message.edit_text("🔍 Ищу в каталоге...")
    
    # Perform search with enhanced query
    await perform_product_search(
        callback.message,
        state,
        enhanced_query,
        api_client
    )


@router.callback_query(F.data.startswith("price_"))
async def apply_price_filter(callback: types.CallbackQuery, state: FSMContext):
    """Apply price range filter"""
    api_client = callback.message.bot.get("api_client")
    price_range = callback.data.split("_", 1)[1]
    
    state_data = await state.get_data()
    original_query = state_data.get("vague_query", "")
    
    # Build query with price hint
    price_hints = {
        "low": "недорогой",
        "mid": "средняя цена",
        "high": "премиум",
        "all": ""
    }
    
    hint = price_hints.get(price_range, "")
    enhanced_query = f"{original_query} {hint}".strip()
    
    await callback.answer(f"Поиск: {enhanced_query}")
    await callback.message.edit_text("🔍 Ищу в каталоге...")
    
    await perform_product_search(
        callback.message,
        state,
        enhanced_query,
        api_client
    )


@router.message(ConversationState.product_inquiry, F.text)
async def handle_color_filter(message: types.Message, state: FSMContext):
    """
    Handle color specification after user chose color filter
    """
    state_data = await state.get_data()
    filter_stage = state_data.get("filter_stage")
    
    if filter_stage == "color":
        # User specified color
        color = message.text.strip()
        original_query = state_data.get("vague_query", "")
        
        enhanced_query = f"{original_query} {color}"
        
        api_client = message.bot.get("api_client")
        
        await perform_product_search(
            message,
            state,
            enhanced_query,
            api_client
        )
        
        # Clear filter stage
        await state.update_data(filter_stage=None)


# ==================== GENERAL MESSAGE HANDLER ====================

@router.message(F.text & ~F.text.startswith("/"))
async def handle_general_message(message: types.Message, state: FSMContext):
    """
    Handle any text message (fallback)
    Assumes user wants to search products
    """
    # Set state to product inquiry
    await state.set_state(ConversationState.product_inquiry)
    
    # Handle as product search
    await handle_product_search(message, state)
