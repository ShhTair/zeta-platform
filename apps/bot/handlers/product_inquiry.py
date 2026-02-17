"""
Product inquiry handler - Search catalog with smart clarifying questions
"""
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.start import ConversationState

logger = logging.getLogger(__name__)

router = Router()

# Vague keywords that trigger clarifying questions
VAGUE_KEYWORDS = [
    'стул', 'стол', 'кровать', 'диван', 'шкаф', 
    'кресло', 'тумба', 'полка', 'комод', 'матрас'
]


def is_vague_query(query: str) -> bool:
    """
    Detect if query is too vague and needs clarification
    Returns True if query is short and contains generic furniture keywords
    """
    query_lower = query.lower().strip()
    words = query_lower.split()
    
    # Query is vague if:
    # 1. Contains vague keyword AND
    # 2. Is short (≤2 words) OR has no descriptive adjectives
    has_vague_keyword = any(kw in query_lower for kw in VAGUE_KEYWORDS)
    is_short = len(words) <= 2
    
    return has_vague_keyword and is_short


@router.message(ConversationState.product_inquiry, F.text)
async def handle_product_inquiry(message: types.Message, state: FSMContext):
    """Handle product inquiry with smart clarifying questions"""
    api_client = message.bot.get("api_client")
    
    query = message.text
    city_id = "default"  # Default city for now
    
    # Check if query is too vague
    if is_vague_query(query):
        # Ask clarifying question with inline buttons
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Для дома", callback_data="filter_home")],
            [InlineKeyboardButton(text="🏢 Для офиса", callback_data="filter_office")],
            [InlineKeyboardButton(text="👶 Для детей", callback_data="filter_kids")],
            [InlineKeyboardButton(text="📋 Показать всё", callback_data="filter_all")]
        ])
        
        clarification = f"Какой именно <b>{query}</b> вас интересует?\n\n"
        clarification += "Уточните, пожалуйста:"
        
        await message.answer(clarification, reply_markup=keyboard)
        await state.update_data(vague_query=query)
        
        logger.info(f"User {message.from_user.id} sent vague query: {query}")
        return
    
    # Query is specific enough - proceed with search
    await _perform_product_search(message, state, query, api_client, city_id)


async def _perform_product_search(
    message: types.Message,
    state: FSMContext,
    query: str,
    api_client,
    city_id: str
):
    """
    Perform product search and display results with inline buttons
    """
    # Show searching message
    search_msg = "🔍 Ищу в каталоге..."
    status = await message.answer(search_msg)
    
    # Search products
    products = await api_client.search_products(
        query=query,
        city_id=city_id,
        limit=7
    )
    
    await status.delete()
    
    if not products:
        no_results = "😔 К сожалению, ничего не найдено. Попробуйте другой запрос или свяжитесь с менеджером."
        
        # Offer escalation
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📞 Связаться с менеджером", callback_data="escalate:manager")],
            [InlineKeyboardButton(text="🎫 Создать заявку", callback_data="escalate:ticket")]
        ])
        
        await message.answer(no_results, reply_markup=keyboard)
        await state.set_state(ConversationState.escalation)
        return
    
    # Display products with inline buttons (no numbered list!)
    response = f"📦 <b>Нашел несколько вариантов:</b>\n\n"
    response += f"По запросу: \"{query}\""
    
    keyboard_buttons = []
    for product in products:
        name = product.get("name", "Товар")
        price = product.get("price", 0)
        sku = product.get("sku") or product.get("id")
        
        # Truncate long names for buttons (Telegram limit ~64 chars)
        button_text = f"🪑 {name[:40]}" + ("..." if len(name) > 40 else "")
        button_text += f" • {price} ₽"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"product_{sku}"
            )
        ])
    
    # Limit to 7 products to avoid overwhelming UI
    if len(keyboard_buttons) > 7:
        keyboard_buttons = keyboard_buttons[:7]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(response, reply_markup=keyboard)
    await state.update_data(query=query, products=products)
    
    logger.info(f"User {message.from_user.id} searched: {query} - found {len(products)} products")
