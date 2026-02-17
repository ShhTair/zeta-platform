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
    """Handle /start command"""
    greeting = "👋 Здравствуйте! Чем могу помочь?\n\n" \
                "Если вы ищете мебель или хотите узнать больше о наших товарах, " \
                "напишите, пожалуйста, что именно вас интересует."
    
    await message.answer(greeting)
    await state.set_state(ConversationState.product_inquiry)
    
    logger.info(f"User {message.from_user.id} started conversation")
