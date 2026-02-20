"""
Internationalization (i18n) Support
Multi-language support for ZETA bot (Russian and Kazakh)
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


# Translation dictionary
# TODO: Expand with more translations as needed
translations: Dict[str, Dict[str, str]] = {
    "ru": {
        # Greetings
        "greeting": "Привет! Помогу найти мебель 🪑",
        "greeting_returning": "С возвращением! Чем могу помочь?",
        
        # Search
        "search_prompt": "Что ищете?",
        "search_processing": "Ищу подходящие товары...",
        "search_no_results": "К сожалению, ничего не нашёл. Попробуйте другой запрос.",
        "search_results": "Нашёл {count} вариантов:",
        
        # Product
        "product_price": "Цена: {price} ₸",
        "product_availability": "В наличии: {stock} шт.",
        "product_out_of_stock": "Нет в наличии",
        "product_details": "Подробнее",
        
        # Cart & Orders
        "cart_add": "Добавить в корзину",
        "cart_empty": "Корзина пуста",
        "cart_total": "Итого: {total} ₸",
        "order_confirm": "Оформить заказ",
        "order_created": "✅ Заказ оформлен! Номер: {order_id}",
        
        # Errors
        "error_generic": "Произошла ошибка. Попробуйте позже.",
        "error_rate_limit": "⏳ Слишком много запросов. Подождите минуту.",
        
        # Help
        "help_message": (
            "🪑 ZETA - каталог мебели\n\n"
            "Команды:\n"
            "/start - Начать\n"
            "/search - Поиск мебели\n"
            "/cart - Корзина\n"
            "/help - Помощь\n\n"
            "Просто напишите что ищете!"
        ),
        
        # Contact
        "contact_manager": "Связаться с менеджером",
        "manager_contact": "📞 Менеджер свяжется с вами в ближайшее время.",
    },
    
    "kk": {
        # Greetings (Kazakh)
        "greeting": "Сәлем! Жиһаз табуға көмектесемін 🪑",
        "greeting_returning": "Қайта келуіңізбен! Не көмек қажет?",
        
        # Search
        "search_prompt": "Не іздеп жатырсыз?",
        "search_processing": "Қолайлы тауарларды іздеп жатырмын...",
        "search_no_results": "Өкінішке орай, ештеңе таппадым. Басқа сұрау жасаңыз.",
        "search_results": "{count} нұсқа таптым:",
        
        # Product
        "product_price": "Бағасы: {price} ₸",
        "product_availability": "Қолда бар: {stock} дана",
        "product_out_of_stock": "Қолда жоқ",
        "product_details": "Толығырақ",
        
        # Cart & Orders
        "cart_add": "Себетке қосу",
        "cart_empty": "Себет бос",
        "cart_total": "Барлығы: {total} ₸",
        "order_confirm": "Тапсырыс беру",
        "order_created": "✅ Тапсырыс ресімделді! Нөмірі: {order_id}",
        
        # Errors
        "error_generic": "Қате орын алды. Кейінірек қайталаңыз.",
        "error_rate_limit": "⏳ Тым көп сұрау. Бір минут күтіңіз.",
        
        # Help
        "help_message": (
            "🪑 ZETA - жиһаз каталогы\n\n"
            "Командалар:\n"
            "/start - Бастау\n"
            "/search - Жиһаз іздеу\n"
            "/cart - Себет\n"
            "/help - Көмек\n\n"
            "Не іздеп жатқаныңызды жазыңыз!"
        ),
        
        # Contact
        "contact_manager": "Менеджермен байланысу",
        "manager_contact": "📞 Менеджер сізбен жақын арада байланысады.",
    }
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Translate key to specified language.
    
    Args:
        key: Translation key
        lang: Language code ("ru" or "kk")
        **kwargs: Variables for string formatting
    
    Returns:
        Translated string with variables substituted
    
    Examples:
        t("greeting", lang="ru")
        t("product_price", lang="kk", price=45000)
        t("search_results", count=5)
    """
    # Get translation for language, fallback to Russian
    lang_dict = translations.get(lang, translations["ru"])
    text = lang_dict.get(key, key)  # Return key if translation not found
    
    # Substitute variables if provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing variable in translation: {e}")
    
    return text


def get_user_language(user_id: int) -> str:
    """
    Get user's preferred language.
    
    TODO: Implement user language preference storage
    - Store in database
    - Allow user to change language
    - Detect from Telegram language_code
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        Language code ("ru" or "kk")
    """
    # TODO: Query database for user preference
    # For now, default to Russian
    return "ru"


def set_user_language(user_id: int, lang: str):
    """
    Set user's preferred language.
    
    TODO: Implement language preference storage
    
    Args:
        user_id: Telegram user ID
        lang: Language code ("ru" or "kk")
    """
    # TODO: Store in database
    logger.info(f"Language preference for user {user_id}: {lang} (TODO: Implement storage)")


def add_translation(lang: str, key: str, value: str):
    """
    Add new translation dynamically.
    
    Args:
        lang: Language code
        key: Translation key
        value: Translation value
    """
    if lang not in translations:
        translations[lang] = {}
    
    translations[lang][key] = value
    logger.info(f"Added translation: {lang}.{key}")


def get_available_languages() -> list:
    """
    Get list of available languages.
    
    Returns:
        List of language codes
    """
    return list(translations.keys())


# Language names for UI
LANGUAGE_NAMES = {
    "ru": "Русский 🇷🇺",
    "kk": "Қазақша 🇰🇿"
}


__all__ = [
    "t",
    "get_user_language",
    "set_user_language",
    "add_translation",
    "get_available_languages",
    "translations",
    "LANGUAGE_NAMES"
]
