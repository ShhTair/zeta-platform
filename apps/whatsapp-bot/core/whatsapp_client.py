"""
WhatsApp Cloud API Client
Handles all communication with WhatsApp Business Cloud API
"""

import logging
import httpx
from typing import Dict, List, Optional, Any, Union
import json
from config import settings, WHATSAPP_MESSAGES_ENDPOINT, WHATSAPP_MEDIA_ENDPOINT

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """
    WhatsApp Cloud API wrapper.
    
    Features:
    - Send text messages
    - Send images/documents/audio
    - Send quick reply buttons (max 3)
    - Send list messages (interactive lists)
    - Send location messages
    - Mark messages as read
    - React to messages
    - Use templates (pre-approved messages)
    """
    
    def __init__(self):
        self.token = settings.whatsapp_token
        self.phone_number_id = settings.whatsapp_phone_number_id
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def send_text(
        self,
        to: str,
        text: str,
        preview_url: bool = False
    ) -> Dict:
        """
        Send simple text message.
        
        Args:
            to: Recipient phone number (international format, e.g., "77001234567")
            text: Message text (max 4096 chars)
            preview_url: Enable URL preview
        
        Returns:
            API response with message ID
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": text
            }
        }
        
        return await self._send_message(payload)
    
    async def send_image(
        self,
        to: str,
        image_url: Optional[str] = None,
        image_id: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict:
        """
        Send image message.
        
        Args:
            to: Recipient phone number
            image_url: Public URL of the image (OR)
            image_id: Media ID (uploaded via upload_media)
            caption: Image caption (optional)
        
        Returns:
            API response
        """
        if not image_url and not image_id:
            raise ValueError("Either image_url or image_id must be provided")
        
        image_obj = {}
        if image_id:
            image_obj["id"] = image_id
        else:
            image_obj["link"] = image_url
        
        if caption:
            image_obj["caption"] = caption
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": image_obj
        }
        
        return await self._send_message(payload)
    
    async def send_document(
        self,
        to: str,
        document_url: Optional[str] = None,
        document_id: Optional[str] = None,
        filename: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict:
        """Send document (PDF, DOCX, etc.)"""
        if not document_url and not document_id:
            raise ValueError("Either document_url or document_id must be provided")
        
        doc_obj = {}
        if document_id:
            doc_obj["id"] = document_id
        else:
            doc_obj["link"] = document_url
        
        if filename:
            doc_obj["filename"] = filename
        if caption:
            doc_obj["caption"] = caption
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "document",
            "document": doc_obj
        }
        
        return await self._send_message(payload)
    
    async def send_audio(
        self,
        to: str,
        audio_url: Optional[str] = None,
        audio_id: Optional[str] = None
    ) -> Dict:
        """Send audio message"""
        if not audio_url and not audio_id:
            raise ValueError("Either audio_url or audio_id must be provided")
        
        audio_obj = {}
        if audio_id:
            audio_obj["id"] = audio_id
        else:
            audio_obj["link"] = audio_url
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "audio",
            "audio": audio_obj
        }
        
        return await self._send_message(payload)
    
    async def send_location(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: str,
        address: str
    ) -> Dict:
        """
        Send location message.
        
        Args:
            to: Recipient phone number
            latitude: Location latitude
            longitude: Location longitude
            name: Location name (e.g., "ZETA Showroom")
            address: Location address
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "location",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "name": name,
                "address": address
            }
        }
        
        return await self._send_message(payload)
    
    async def send_buttons(
        self,
        to: str,
        text: str,
        buttons: List[Dict[str, str]]
    ) -> Dict:
        """
        Send message with quick reply buttons (max 3 buttons).
        
        Args:
            to: Recipient phone number
            text: Message body text
            buttons: List of buttons, each with 'id' and 'title'
                Example: [
                    {"id": "btn_1", "title": "Да ✅"},
                    {"id": "btn_2", "title": "Нет ❌"}
                ]
        
        Note: WhatsApp limits to 3 buttons max per message
        """
        if len(buttons) > 3:
            logger.warning(f"Too many buttons ({len(buttons)}), truncating to 3")
            buttons = buttons[:3]
        
        button_objects = [
            {
                "type": "reply",
                "reply": {
                    "id": btn["id"],
                    "title": btn["title"][:20]  # Max 20 chars
                }
            }
            for btn in buttons
        ]
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": text
                },
                "action": {
                    "buttons": button_objects
                }
            }
        }
        
        return await self._send_message(payload)
    
    async def send_list(
        self,
        to: str,
        header: str,
        body: str,
        button_text: str,
        sections: List[Dict]
    ) -> Dict:
        """
        Send interactive list message (better for product catalogs).
        
        Args:
            to: Recipient phone number
            header: List header text
            body: List body text
            button_text: Button text (e.g., "Выбрать товар")
            sections: List of sections, each containing rows
                Example: [
                    {
                        "title": "Диваны",
                        "rows": [
                            {"id": "prod_1", "title": "Диван угловой", "description": "50000 ₸"},
                            {"id": "prod_2", "title": "Диван прямой", "description": "40000 ₸"}
                        ]
                    }
                ]
        
        Note: Max 10 sections, max 10 rows per section
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": header
                },
                "body": {
                    "text": body
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }
        
        return await self._send_message(payload)
    
    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "ru",
        components: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Send pre-approved template message.
        
        Used for:
        - Notifications after 24-hour window
        - Order confirmations
        - Price alerts
        
        Args:
            to: Recipient phone number
            template_name: Template name (must be pre-approved in Meta Business Manager)
            language_code: Template language (ru, kz, en, etc.)
            components: Template parameters (optional)
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        return await self._send_message(payload)
    
    async def mark_as_read(self, message_id: str) -> Dict:
        """Mark message as read (blue checkmark)"""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        return await self._send_message(payload)
    
    async def send_reaction(
        self,
        to: str,
        message_id: str,
        emoji: str
    ) -> Dict:
        """
        React to a message with emoji.
        
        Args:
            to: Recipient phone number
            message_id: ID of message to react to
            emoji: Emoji (e.g., "👍", "❤️")
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "reaction",
            "reaction": {
                "message_id": message_id,
                "emoji": emoji
            }
        }
        
        return await self._send_message(payload)
    
    async def upload_media(
        self,
        file_path: str,
        mime_type: str
    ) -> str:
        """
        Upload media to WhatsApp servers and get media_id.
        
        Args:
            file_path: Path to local file
            mime_type: MIME type (e.g., "image/jpeg", "audio/ogg")
        
        Returns:
            media_id (can be used in send_image/send_audio/etc.)
        """
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                files = {"file": (file_path, f, mime_type)}
                headers = {"Authorization": f"Bearer {self.token}"}
                
                response = await client.post(
                    WHATSAPP_MEDIA_ENDPOINT,
                    headers=headers,
                    files=files
                )
                response.raise_for_status()
                
                data = response.json()
                media_id = data.get("id")
                
                logger.info(f"✓ Uploaded media: {media_id}")
                return media_id
    
    async def get_media_url(self, media_id: str) -> str:
        """
        Get download URL for media received from user.
        
        Args:
            media_id: Media ID from incoming message
        
        Returns:
            Direct download URL (valid for ~5 minutes)
        """
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("url")
    
    async def download_media(
        self,
        media_url: str,
        save_path: str
    ):
        """
        Download media from WhatsApp servers.
        
        Args:
            media_url: URL from get_media_url()
            save_path: Local path to save file
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(media_url, headers=self.headers)
            response.raise_for_status()
            
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"✓ Downloaded media to: {save_path}")
    
    async def _send_message(self, payload: Dict) -> Dict:
        """Internal method to send message via API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    WHATSAPP_MESSAGES_ENDPOINT,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"✓ Message sent: {data.get('messages', [{}])[0].get('id', 'unknown')}")
                return data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"WhatsApp API error: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                raise


# Global client instance
whatsapp_client = WhatsAppClient()


__all__ = ["WhatsAppClient", "whatsapp_client"]
