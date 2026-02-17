"""
Escalation handler - Manager tag and Bitrix ticket creation
"""
import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from handlers.start import ConversationState

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "escalate:manager")
async def escalate_to_manager(callback: types.CallbackQuery, state: FSMContext):
    """Tag manager in Telegram"""
    prompt_manager = callback.message.bot["prompt_manager"]
    manager_id = prompt_manager.manager_telegram_id
    
    if not manager_id:
        await callback.message.answer(
            "⚠️ Менеджер не настроен для этого города. Попробуйте создать заявку."
        )
        await callback.answer()
        return
    
    user = callback.from_user
    username = user.username or user.first_name or "Клиент"
    user_link = f"tg://user?id={user.id}"
    
    # Get conversation data
    data = await state.get_data()
    query = data.get("query", "не указан")
    
    # Tag manager
    message = (
        f"🔔 <b>Новое обращение!</b>\n\n"
        f"👤 Клиент: <a href='{user_link}'>{username}</a>\n"
        f"🔍 Запрос: {query}\n\n"
        f"{manager_id}, пожалуйста, помогите клиенту!"
    )
    
    await callback.message.answer(message)
    await callback.message.answer(
        "✅ Менеджер уведомлен! Он свяжется с вами в ближайшее время."
    )
    
    await callback.answer()
    await state.clear()
    
    logger.info(f"User {user.id} escalated to manager: {manager_id}")


@router.callback_query(F.data == "escalate:ticket")
async def create_ticket(callback: types.CallbackQuery, state: FSMContext):
    """Create Bitrix CRM deal"""
    api_client = callback.message.bot["api_client"]
    prompt_manager = callback.message.bot["prompt_manager"]
    
    user = callback.from_user
    username = user.username or user.first_name or "Клиент"
    telegram_handle = f"@{user.username}" if user.username else f"ID: {user.id}"
    
    # Get conversation data
    data = await state.get_data()
    query = data.get("query", "Не указан")
    products = data.get("products", [])
    product_id = products[0].get("id") if products else None
    
    # Create deal
    try:
        result = await api_client.create_bitrix_deal(
            customer_name=username,
            customer_telegram=telegram_handle,
            product_id=product_id,
            message=f"Запрос: {query}",
            city_id=prompt_manager.city_id
        )
        
        deal_id = result.get("deal_id")
        deal_url = result.get("deal_url", "")
        
        response = (
            f"✅ <b>Заявка создана!</b>\n\n"
            f"🎫 Номер заявки: {deal_id}\n"
            f"Наш менеджер свяжется с вами в ближайшее время.\n\n"
            f"Спасибо за обращение!"
        )
        
        await callback.message.answer(response)
        await callback.answer()
        await state.clear()
        
        logger.info(f"Bitrix ticket created for user {user.id}: {deal_id}")
        
    except Exception as e:
        logger.error(f"Failed to create ticket: {e}")
        await callback.message.answer(
            "❌ Ошибка при создании заявки. Попробуйте связаться с менеджером напрямую."
        )
        await callback.answer()
