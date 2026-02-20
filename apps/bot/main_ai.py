"""
ZETA Telegram Bot - AI-Powered with Webhook
Natural conversation using OpenAI GPT-4o-mini
"""
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from handlers import start, conversation, callbacks, escalation

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "20.234.16.216")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8443))
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

# Check API keys
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not set! Bot will not work properly.")
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize bot and dispatcher with FSM storage
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def on_startup(bot: Bot) -> None:
    """Setup webhook on startup"""
    from aiogram.types import FSInputFile
    logger.info("🚀 Starting AI-powered ZETA bot...")
    logger.info(f"🤖 OpenAI API key: {'✅ Set' if OPENAI_API_KEY else '❌ Missing'}")
    
    # Upload self-signed certificate to Telegram
    certificate = FSInputFile("/home/azureuser/webhook_cert.pem")
    await bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=certificate,
        drop_pending_updates=True
    )
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}")


async def on_shutdown(bot: Bot) -> None:
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    await bot.delete_webhook()
    await bot.session.close()


def register_handlers(dp: Dispatcher) -> None:
    """Register all handlers"""
    from handlers import interactive, conversation_interactive
    
    dp.include_router(start.router)
    dp.include_router(interactive.router)  # NEW: Interactive UI (buttons, photos, links)
    dp.include_router(conversation.router)  # AI-powered conversation (legacy)
    dp.include_router(conversation_interactive.router)  # NEW: Enhanced interactive conversation
    dp.include_router(callbacks.router)
    dp.include_router(escalation.router)


def create_app() -> web.Application:
    """Create aiohttp application"""
    # Register handlers
    register_handlers(dp)
    
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
    logger.info("=" * 60)
    logger.info("🤖 ZETA AI Bot - Intelligent Furniture Assistant")
    logger.info("=" * 60)
    logger.info(f"📡 Webhook: {WEBHOOK_URL}")
    logger.info(f"🧠 AI Model: GPT-4o-mini")
    logger.info(f"💬 Mode: Natural conversation with function calling")
    logger.info("=" * 60)
    
    app = create_app()
    
    # Run on localhost only - Nginx proxies external traffic
    web.run_app(app, host="127.0.0.1", port=3000)


if __name__ == "__main__":
    main()
