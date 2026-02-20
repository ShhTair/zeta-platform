"""
Media Handler
Processes images (OCR + Vision API) and voice messages (Whisper)
"""

import logging
import os
import tempfile
from typing import Dict, Any

from core.whatsapp_client import whatsapp_client
from core.product_search import product_api
from handlers.interactive import send_product_list

logger = logging.getLogger(__name__)

# Whisper for voice transcription
try:
    import whisper
    WHISPER_MODEL = whisper.load_model("base")
    WHISPER_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Whisper not available - voice messages disabled")
    WHISPER_AVAILABLE = False


async def handle_image_message(message: Dict[str, Any]):
    """
    Handle incoming image message.
    
    Use cases:
    1. User sends product screenshot → OCR extracts SKU
    2. User sends product photo → Vision API describes and searches
    3. User sends catalog screenshot → OCR + search
    """
    try:
        from_number = message.get("from")
        message_id = message.get("id")
        image_data = message.get("image", {})
        media_id = image_data.get("id")
        caption = image_data.get("caption", "")
        
        if not media_id:
            return
        
        logger.info(f"🖼️ Image received from {from_number}")
        
        # Mark as read
        await whatsapp_client.mark_as_read(message_id)
        
        # Send thinking reaction
        await whatsapp_client.send_reaction(
            to=from_number,
            message_id=message_id,
            emoji="👀"
        )
        
        # Download image
        media_url = await whatsapp_client.get_media_url(media_id)
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            await whatsapp_client.download_media(media_url, tmp_path)
        
        try:
            # Search by image (OCR + Vision API)
            products = await product_api.search_by_image(
                image_path=tmp_path,
                use_ocr=True,
                use_vision=True
            )
            
            if products:
                # Success reaction
                await whatsapp_client.send_reaction(
                    to=from_number,
                    message_id=message_id,
                    emoji="✅"
                )
                
                await send_product_list(
                    to=from_number,
                    products=products,
                    header="Нашёл! 🔍",
                    body="Вот что нашёл по вашему фото:"
                )
            else:
                await whatsapp_client.send_text(
                    to=from_number,
                    text="""😔 К сожалению, не смог найти товар по этому фото.

Попробуйте:
• Отправить фото чётче
• Написать описание товара текстом
• Связаться с менеджером

Я всегда рад помочь! 😊"""
                )
        
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"❌ Image handling error: {e}", exc_info=True)
        await whatsapp_client.send_text(
            to=from_number,
            text="Произошла ошибка при обработке фото. Попробуйте ещё раз!"
        )


async def handle_audio_message(message: Dict[str, Any]):
    """
    Handle voice message.
    
    Process:
    1. Download audio
    2. Transcribe with Whisper
    3. Process as text message
    """
    try:
        if not WHISPER_AVAILABLE:
            from_number = message.get("from")
            await whatsapp_client.send_text(
                to=from_number,
                text="Извините, голосовые сообщения пока не поддерживаются. Напишите текстом! 😊"
            )
            return
        
        from_number = message.get("from")
        message_id = message.get("id")
        audio_data = message.get("audio", {})
        media_id = audio_data.get("id")
        
        if not media_id:
            return
        
        logger.info(f"🎤 Voice message from {from_number}")
        
        # Mark as read
        await whatsapp_client.mark_as_read(message_id)
        
        # Send thinking reaction
        await whatsapp_client.send_reaction(
            to=from_number,
            message_id=message_id,
            emoji="👂"
        )
        
        # Download audio
        media_url = await whatsapp_client.get_media_url(media_id)
        
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            await whatsapp_client.download_media(media_url, tmp_path)
        
        try:
            # Transcribe with Whisper
            result = WHISPER_MODEL.transcribe(tmp_path, language="ru")
            transcribed_text = result["text"]
            
            logger.info(f"🎤 Transcribed: {transcribed_text}")
            
            # Send confirmation
            await whatsapp_client.send_text(
                to=from_number,
                text=f"🎤 Вы сказали: \"{transcribed_text}\"\n\nОбрабатываю запрос..."
            )
            
            # Process as text message
            from handlers.messages import handle_text_message
            text_message = {
                "from": from_number,
                "id": message_id,
                "text": {"body": transcribed_text}
            }
            await handle_text_message(text_message)
        
        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"❌ Audio handling error: {e}", exc_info=True)
        await whatsapp_client.send_text(
            to=from_number,
            text="Не удалось распознать голосовое сообщение. Попробуйте написать текстом!"
        )


async def handle_document_message(message: Dict[str, Any]):
    """
    Handle document message (PDF, DOCX, etc.).
    
    Possible use cases:
    - User sends product catalog PDF
    - User sends order form
    """
    try:
        from_number = message.get("from")
        document_data = message.get("document", {})
        filename = document_data.get("filename", "document")
        
        logger.info(f"📄 Document received from {from_number}: {filename}")
        
        await whatsapp_client.send_text(
            to=from_number,
            text=f"""📄 Получил ваш документ: *{filename}*

Для работы с документами обратитесь к менеджеру:
📞 +7 (XXX) XXX-XX-XX

Или напишите ваш вопрос текстом - я с радостью помогу! 😊"""
        )
    
    except Exception as e:
        logger.error(f"❌ Document handling error: {e}")


__all__ = [
    "handle_image_message",
    "handle_audio_message",
    "handle_document_message"
]
