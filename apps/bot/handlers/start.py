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
    prompt_manager = message.bot["prompt_manager"]
    
    # Get dynamic greeting prompt
    greeting = await prompt_manager.get_prompt(
        "greeting",
        default="👋 Добро пожаловать! Я помогу вам найти нужный товар."
    )
    
    await message.answer(greeting)
    await state.set_state(ConversationState.product_inquiry)
    
    logger.info(f"User {message.from_user.id} started conversation")
