"""
Start command handler - Greeting flow
"""
import logging
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)

router = Router()


class ConversationState(StatesGroup):
    """Conversation states"""
    greeting = State()
    product_inquiry = State()
    escalation = State()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command with beautiful interactive menu"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    greeting = (
        "👋 <b>Добро пожаловать в ZETA!</b>\n\n"
        "Я помогу вам найти идеальную мебель для дома или офиса.\n\n"
        "Выберите действие или просто напишите, что вы ищете:"
    )
    
    # Quick action menu
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Искать товар", callback_data="action_search")],
        [InlineKeyboardButton(text="🏷️ Популярные товары", callback_data="action_popular")],
        [InlineKeyboardButton(text="💬 Связаться", callback_data="action_contact")],
        [InlineKeyboardButton(text="ℹ️ О компании", callback_data="action_about")]
    ])
    
    await message.answer(greeting, reply_markup=keyboard)
    await state.set_state(ConversationState.product_inquiry)
    
    logger.info(f"User {message.from_user.id} started conversation")
