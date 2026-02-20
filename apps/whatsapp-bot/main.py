"""
ZETA WhatsApp Bot - Main Application
FastAPI webhook server for WhatsApp Business Cloud API
"""

import logging
from fastapi import FastAPI, Request, Response, HTTPException
from contextlib import asynccontextmanager

from config import settings, WEBHOOK_PATH
from core.memory import init_conversation_memory
from handlers.messages import handle_text_message
from handlers.interactive import handle_button_response, handle_list_response, send_welcome_menu
from handlers.media import handle_image_message, handle_audio_message, handle_document_message

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown"""
    # Startup
    logger.info("🚀 Starting ZETA WhatsApp Bot")
    logger.info(f"📱 Phone Number ID: {settings.whatsapp_phone_number_id}")
    logger.info(f"🤖 AI Model: {settings.openai_model}")
    logger.info(f"🏙️ City ID: {settings.city_id}")
    
    # Initialize conversation memory (Redis)
    try:
        memory = init_conversation_memory(
            redis_url=settings.redis_url,
            max_messages=settings.max_conversation_history,
            ttl_seconds=settings.session_timeout_seconds
        )
        await memory.connect()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        logger.warning("⚠️ Bot will work WITHOUT memory - limited context awareness")
    
    # Log enabled features
    logger.info("📋 Enabled features:")
    logger.info(f"  🎤 Voice transcription: {settings.enable_voice_transcription}")
    logger.info(f"  🔔 Price alerts: {settings.enable_price_alerts}")
    logger.info(f"  📦 Order tracking: {settings.enable_order_tracking}")
    logger.info(f"  💾 Saved searches: {settings.enable_saved_searches}")
    
    logger.info("✅ WhatsApp bot ready!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down...")
    try:
        from core.memory import conversation_memory
        if conversation_memory:
            await conversation_memory.close()
    except:
        pass


# Create FastAPI app
app = FastAPI(
    title="ZETA WhatsApp Bot",
    description="Intelligent furniture assistant for WhatsApp",
    version="2.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "ZETA WhatsApp Bot",
        "version": "2.0.0",
        "phone_number_id": settings.whatsapp_phone_number_id
    }


@app.get(WEBHOOK_PATH)
async def verify_webhook(request: Request):
    """
    Webhook verification (GET).
    WhatsApp sends this during webhook setup.
    
    Params:
        hub.mode=subscribe
        hub.verify_token=<your_verify_token>
        hub.challenge=<random_string>
    
    Response:
        Return hub.challenge if verify_token matches
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        logger.info("✅ Webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")
    else:
        logger.warning(f"❌ Webhook verification failed: mode={mode}, token={token}")
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    """
    Main webhook endpoint (POST).
    Receives all WhatsApp events (messages, statuses, etc.)
    
    Payload structure:
    {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [...],  # Incoming messages
                    "statuses": [...]   # Message statuses (sent, delivered, read)
                }
            }]
        }]
    }
    """
    try:
        data = await request.json()
        
        # Log raw payload (for debugging)
        logger.debug(f"Webhook payload: {data}")
        
        # Extract messages
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Handle incoming messages
                messages = value.get("messages", [])
                for message in messages:
                    await process_message(message)
                
                # Handle message statuses (delivered, read, etc.)
                statuses = value.get("statuses", [])
                for status in statuses:
                    logger.debug(f"Message status: {status.get('status')} - {status.get('id')}")
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


async def process_message(message: dict):
    """
    Process incoming WhatsApp message.
    Routes to appropriate handler based on message type.
    
    Message types:
    - text: Text message
    - image: Image message
    - audio: Voice message
    - video: Video message
    - document: Document (PDF, DOCX, etc.)
    - location: Location message
    - contacts: Contact card
    - interactive: Button/list response
    """
    try:
        msg_type = message.get("type")
        from_number = message.get("from")
        
        logger.info(f"📩 Message type: {msg_type} from {from_number}")
        
        # Text message
        if msg_type == "text":
            text = message.get("text", {}).get("body", "").lower()
            
            # Handle /start or greeting
            if text in ["/start", "start", "привет", "здравствуйте", "сәлем"]:
                await send_welcome_menu(from_number)
            else:
                await handle_text_message(message)
        
        # Image message
        elif msg_type == "image":
            await handle_image_message(message)
        
        # Voice message
        elif msg_type == "audio":
            if settings.enable_voice_transcription:
                await handle_audio_message(message)
            else:
                from core.whatsapp_client import whatsapp_client
                await whatsapp_client.send_text(
                    to=from_number,
                    text="Голосовые сообщения пока не поддерживаются. Напишите текстом! 😊"
                )
        
        # Document
        elif msg_type == "document":
            await handle_document_message(message)
        
        # Interactive response (button click or list selection)
        elif msg_type == "interactive":
            interactive_type = message.get("interactive", {}).get("type")
            
            if interactive_type == "button_reply":
                await handle_button_response(message)
            elif interactive_type == "list_reply":
                await handle_list_response(message)
        
        # Location (user shared location)
        elif msg_type == "location":
            # Could be used for "find nearest store"
            logger.info(f"📍 Location received from {from_number}")
            from core.whatsapp_client import whatsapp_client
            await whatsapp_client.send_text(
                to=from_number,
                text="Спасибо! Вы можете написать ваш вопрос, я помогу с выбором мебели! 😊"
            )
        
        # Contacts
        elif msg_type == "contacts":
            logger.info(f"👤 Contact card received from {from_number}")
        
        # Unsupported type
        else:
            logger.warning(f"⚠️ Unsupported message type: {msg_type}")
    
    except Exception as e:
        logger.error(f"❌ Process message error: {e}", exc_info=True)


@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "redis": "connected" if conversation_memory else "disconnected"
    }


@app.get("/stats")
async def stats():
    """Bot statistics (optional)"""
    # Could return: total messages, active users, escalations, etc.
    return {
        "status": "ok",
        "message": "Statistics endpoint - implement as needed"
    }


def main():
    """Run the bot with uvicorn"""
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=False  # Disable reload in production
    )


if __name__ == "__main__":
    main()
