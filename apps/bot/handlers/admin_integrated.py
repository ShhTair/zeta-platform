"""
Admin-Integrated Handlers
Demonstrates how to use ConfigManager, EscalationLogger, and AnalyticsTracker
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("contact"))
async def send_manager_contact(message: Message):
    """Send manager contact info from admin config"""
    config_manager = message.bot.get("config_manager")
    city_id = message.bot.get("city_id")
    analytics_tracker = message.bot.get("analytics_tracker")
    
    manager_contact = config_manager.manager_contact
    
    if manager_contact:
        await message.answer(
            f"💬 <b>Связаться с менеджером:</b>\n\n"
            f"📞 {manager_contact}\n\n"
            f"Укажите ваш вопрос и мы свяжемся с вами!"
        )
    else:
        await message.answer(
            "К сожалению, контакт менеджера не указан. "
            "Пожалуйста, попробуйте позже."
        )
    
    # Track event
    await analytics_tracker.track_event(
        city_id=city_id,
        event_type="manager_contact_requested",
        data={"user_id": message.from_user.id}
    )


@router.message(Command("escalate"))
async def escalate_to_manager(message: Message):
    """
    Escalate conversation to manager
    Usage: /escalate <reason> [product_sku]
    """
    config_manager = message.bot.get("config_manager")
    escalation_logger = message.bot.get("escalation_logger")
    analytics_tracker = message.bot.get("analytics_tracker")
    city_id = message.bot.get("city_id")
    
    # Parse command arguments
    args = message.text.split(maxsplit=2)
    reason = args[1] if len(args) > 1 else "complex_query"
    product_sku = args[2] if len(args) > 2 else None
    
    user_name = message.from_user.full_name or f"User{message.from_user.id}"
    
    # Log escalation to admin platform
    success = await escalation_logger.log_escalation(
        city_id=city_id,
        user_id=message.from_user.id,
        user_name=user_name,
        product_sku=product_sku,
        reason=reason,
        conversation_history=[
            {"role": "user", "text": message.text, "timestamp": message.date.isoformat()}
        ]
    )
    
    if success:
        # Check escalation action from config
        action = config_manager.escalation_action
        
        if action == "notify":
            manager_contact = config_manager.manager_contact
            await message.answer(
                f"✅ <b>Запрос передан менеджеру!</b>\n\n"
                f"📞 Контакт: {manager_contact}\n"
                f"Мы свяжемся с вами в ближайшее время."
            )
        elif action == "transfer":
            await message.answer(
                f"✅ <b>Переключаем на менеджера...</b>\n\n"
                f"Пожалуйста, опишите вашу проблему подробнее, "
                f"и менеджер ответит в ближайшее время."
            )
        else:  # log_only
            await message.answer(
                f"✅ Ваш запрос зарегистрирован. Спасибо!"
            )
        
        # Track analytics
        await analytics_tracker.track_escalation(city_id=city_id, reason=reason)
    else:
        await message.answer(
            "⚠️ Не удалось передать запрос. Попробуйте позже."
        )


@router.message(Command("config"))
async def show_current_config(message: Message):
    """Show current bot config (for debugging)"""
    config_manager = message.bot.get("config_manager")
    
    config_info = (
        f"📋 <b>Текущая конфигурация:</b>\n\n"
        f"🏙️ City ID: {config_manager.city_id}\n"
        f"💬 Приветствие: {config_manager.greeting_message[:50]}...\n"
        f"📞 Контакт менеджера: {config_manager.manager_contact or 'Не указан'}\n"
        f"🚨 Действие эскалации: {config_manager.escalation_action}\n"
        f"🔄 Последняя загрузка: {config_manager.last_reload.strftime('%Y-%m-%d %H:%M:%S') if config_manager.last_reload else 'Не загружено'}"
    )
    
    await message.answer(config_info)


@router.message(F.text.startswith("🔍"))
async def track_search_example(message: Message):
    """
    Example: Track product search
    This would typically be integrated into your search handler
    """
    analytics_tracker = message.bot.get("analytics_tracker")
    city_id = message.bot.get("city_id")
    
    query = message.text.replace("🔍", "").strip()
    
    # Your search logic here...
    # results = await search_products(query)
    results_count = 5  # Example
    
    # Track the search
    await analytics_tracker.track_search(
        city_id=city_id,
        query=query,
        results_count=results_count
    )
    
    await message.answer(f"Поиск: {query} (найдено: {results_count})")
