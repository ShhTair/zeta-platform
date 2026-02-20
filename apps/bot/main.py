"""
ZETA Telegram Bot - Webhook Mode
Multi-city support with dynamic prompts from API/DB
"""
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from handlers import start, product_inquiry, escalation, callbacks, image_search
from services.api_client import APIClient
from services.prompt_manager import PromptManager
from core.config_manager import ConfigManager
from core.escalation_logger import EscalationLogger
from core.analytics_tracker import AnalyticsTracker

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CITY_ID = int(os.getenv("CITY_ID", "1"))
API_URL = os.getenv("API_URL", "http://localhost:8000")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://your-domain.com/webhook
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN.split(':')[0]}"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Initialize services (legacy)
api_client = APIClient(base_url=API_URL)
prompt_manager = PromptManager(api_client=api_client, city_id=str(CITY_ID))

# Initialize new services (admin integration)
config_manager = ConfigManager(api_url=API_URL, city_id=CITY_ID, reload_interval=300)
escalation_logger = EscalationLogger(api_url=API_URL)
analytics_tracker = AnalyticsTracker(api_url=API_URL)


async def on_startup(bot: Bot) -> None:
    """Setup webhook on startup"""
    logger.info("Starting bot...")
    
    # Load city config and prompts (legacy)
    try:
        await prompt_manager.load_config()
        logger.info(f"✅ Loaded legacy config for city: {CITY_ID}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load legacy config: {e}")
    
    # Load new config from admin platform
    try:
        await config_manager.load_config()
        config_manager.start_auto_reload()
        logger.info(f"✅ Config loaded + auto-reload started (every {config_manager.reload_interval}s)")
    except Exception as e:
        logger.error(f"❌ Failed to load admin config: {e}")
        raise
    
    # Set webhook
    webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True
    )
    logger.info(f"✅ Webhook set: {webhook_url}")


async def on_shutdown(bot: Bot) -> None:
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    config_manager.stop_auto_reload()
    await bot.delete_webhook()
    await bot.session.close()


def register_handlers(dp: Dispatcher) -> None:
    """Register all handlers"""
    # Import interactive handlers
    from handlers import interactive, conversation_interactive
    
    # Register in order of priority
    dp.include_router(start.router)
    dp.include_router(image_search.router)  # Image search (OCR + Vision API)
    dp.include_router(interactive.router)  # NEW: Interactive UI handlers (buttons, photos, links)
    dp.include_router(callbacks.router)  # Old callback handlers (backward compatibility)
    dp.include_router(conversation_interactive.router)  # NEW: Enhanced conversation with inline keyboards
    dp.include_router(product_inquiry.router)  # Old product inquiry (backward compatibility)
    dp.include_router(escalation.router)


def create_app() -> web.Application:
    """Create aiohttp application"""
    # Register handlers
    register_handlers(dp)
    
    # Attach services to bot context (so handlers can access via message.bot["api_client"])
    bot["api_client"] = api_client
    bot["prompt_manager"] = prompt_manager
    bot["config_manager"] = config_manager
    bot["escalation_logger"] = escalation_logger
    bot["analytics_tracker"] = analytics_tracker
    bot["city_id"] = CITY_ID
    
    # Setup startup/shutdown hooks
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Create aiohttp app
    app = web.Application()
    
    # Setup webhook handler
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_handler.register(app, path=WEBHOOK_PATH)
    
    # Setup dispatcher
    setup_application(app, dp, bot=bot)
    
    return app


def main():
    """Run the bot"""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is required")
    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL environment variable is required")
    
    logger.info(f"🚀 Starting ZETA bot for city: {CITY_ID}")
    logger.info(f"📡 Webhook path: {WEBHOOK_PATH}")
    
    app = create_app()
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
