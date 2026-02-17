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

from handlers import start, product_inquiry, escalation, callbacks
from services.api_client import APIClient
from services.prompt_manager import PromptManager

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
CITY_ID = os.getenv("CITY_ID", "default")
API_URL = os.getenv("API_URL", "http://localhost:8000")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://your-domain.com/webhook
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN.split(':')[0]}"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Initialize services
api_client = APIClient(base_url=API_URL)
prompt_manager = PromptManager(api_client=api_client, city_id=CITY_ID)


async def on_startup(bot: Bot) -> None:
    """Setup webhook on startup"""
    logger.info("Starting bot...")
    
    # Load city config and prompts
    try:
        await prompt_manager.load_config()
        logger.info(f"✅ Loaded config for city: {CITY_ID}")
    except Exception as e:
        logger.error(f"❌ Failed to load config: {e}")
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
    await bot.delete_webhook()
    await bot.session.close()


def register_handlers(dp: Dispatcher) -> None:
    """Register all handlers"""
    dp.include_router(start.router)
    dp.include_router(callbacks.router)  # Register callbacks before product_inquiry
    dp.include_router(product_inquiry.router)
    dp.include_router(escalation.router)


def create_app() -> web.Application:
    """Create aiohttp application"""
    # Register handlers
    register_handlers(dp)
    
    # Attach services to bot context (so handlers can access via message.bot["api_client"])
    bot["api_client"] = api_client
    bot["prompt_manager"] = prompt_manager
    
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
