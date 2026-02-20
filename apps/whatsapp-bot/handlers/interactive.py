"""
Interactive Message Handlers
Handles buttons, lists, and rich media interactions
"""

import logging
from typing import Dict, Any, List

from core.whatsapp_client import whatsapp_client
from core.product_search import product_api

logger = logging.getLogger(__name__)


async def send_product_list(
    to: str,
    products: List[Dict[str, Any]],
    header: str = "Товары",
    body: str = "Выберите товар:"
):
    """
    Send product list as interactive WhatsApp list message.
    
    Better than buttons for product catalogs (up to 10 items per section).
    """
    try:
        # Group products by category (if available)
        sections = []
        
        # For simplicity, create one section
        rows = []
        for product in products[:10]:  # Max 10 products in WhatsApp list
            rows.append({
                "id": f"product_{product['sku']}",
                "title": product['name'][:24],  # Max 24 chars
                "description": f"{product.get('category', '')} • {product.get('sku', '')}"[:72]  # Max 72 chars
            })
        
        sections.append({
            "title": "Товары",
            "rows": rows
        })
        
        await whatsapp_client.send_list(
            to=to,
            header=header,
            body=body,
            button_text="Выбрать 🪑",
            sections=sections
        )
        
        logger.info(f"✓ Sent product list to {to}")
    
    except Exception as e:
        logger.error(f"❌ Error sending product list: {e}")
        # Fallback to simple text
        await _send_product_list_text(to, products)


async def send_product_details(
    to: str,
    product: Dict[str, Any]
):
    """
    Send detailed product information with image and buttons.
    """
    try:
        # Format product details
        details = f"""🪑 *{product.get('name', 'Товар')}*

📦 *Артикул:* {product.get('sku', 'N/A')}

📝 *Описание:*
{product.get('description', 'Описание отсутствует')[:500]}

📏 *Характеристики:*
• Материал: {product.get('material', 'не указан')}
• Цвет: {product.get('color', 'не указан')}
• Размеры: {product.get('dimensions', 'не указаны')}

💰 *Цена:* Уточните у менеджера
🚚 *Доставка:* Уточните у менеджера
"""
        
        # Send image if available
        if product.get("image_url"):
            await whatsapp_client.send_image(
                to=to,
                image_url=product["image_url"],
                caption=details
            )
        else:
            await whatsapp_client.send_text(to=to, text=details)
        
        # Send action buttons
        buttons = [
            {"id": f"manager_{product['sku']}", "title": "💬 Менеджер"},
            {"id": f"similar_{product['sku']}", "title": "🔍 Похожие"},
            {"id": f"alert_{product['sku']}", "title": "🔔 Цена ↓"}
        ]
        
        await whatsapp_client.send_buttons(
            to=to,
            text="Что хотите сделать?",
            buttons=buttons
        )
        
        logger.info(f"✓ Sent product details: {product['sku']}")
    
    except Exception as e:
        logger.error(f"❌ Error sending product details: {e}")


async def handle_button_response(message: Dict[str, Any]):
    """
    Handle button click (interactive button reply).
    
    WhatsApp sends button clicks in this format:
    {
        "type": "interactive",
        "interactive": {
            "type": "button_reply",
            "button_reply": {
                "id": "btn_id",
                "title": "Button Text"
            }
        }
    }
    """
    try:
        from_number = message.get("from")
        button_reply = message.get("interactive", {}).get("button_reply", {})
        button_id = button_reply.get("id")
        
        if not button_id:
            return
        
        logger.info(f"📱 Button clicked: {button_id} by {from_number}")
        
        # Parse button ID
        if button_id.startswith("product_"):
            # User selected product from list
            sku = button_id.replace("product_", "")
            product = await product_api.get_product_by_sku(sku)
            
            if product:
                await send_product_details(to=from_number, product=product)
        
        elif button_id.startswith("manager_"):
            # Contact manager
            sku = button_id.replace("manager_", "")
            await _handle_manager_contact(from_number, sku)
        
        elif button_id.startswith("similar_"):
            # Show similar products
            sku = button_id.replace("similar_", "")
            products = await product_api.recommend_products(based_on_sku=sku, limit=5)
            
            if products:
                await send_product_list(
                    to=from_number,
                    products=products,
                    header="Похожие товары 🔍",
                    body="Вот похожие варианты:"
                )
        
        elif button_id.startswith("alert_"):
            # Setup price alert
            sku = button_id.replace("alert_", "")
            from core.alerts import save_price_alert
            await save_price_alert(user_phone=from_number, sku=sku)
            
            await whatsapp_client.send_text(
                to=from_number,
                text="✅ Отлично! Я уведомлю вас, когда цена снизится."
            )
    
    except Exception as e:
        logger.error(f"❌ Error handling button: {e}", exc_info=True)


async def handle_list_response(message: Dict[str, Any]):
    """
    Handle list selection (interactive list reply).
    
    Format:
    {
        "type": "interactive",
        "interactive": {
            "type": "list_reply",
            "list_reply": {
                "id": "row_id",
                "title": "Row Title"
            }
        }
    }
    """
    try:
        from_number = message.get("from")
        list_reply = message.get("interactive", {}).get("list_reply", {})
        row_id = list_reply.get("id")
        
        if not row_id:
            return
        
        logger.info(f"📋 List item selected: {row_id} by {from_number}")
        
        # Handle product selection
        if row_id.startswith("product_"):
            sku = row_id.replace("product_", "")
            product = await product_api.get_product_by_sku(sku)
            
            if product:
                await send_product_details(to=from_number, product=product)
    
    except Exception as e:
        logger.error(f"❌ Error handling list: {e}", exc_info=True)


async def send_welcome_menu(to: str):
    """Send welcome menu with quick actions"""
    try:
        welcome_text = """👋 Добро пожаловать в ZETA Furniture!

Я - умный ассистент, помогу найти идеальную мебель для вашего дома! 🪑

Что вас интересует?"""
        
        buttons = [
            {"id": "browse_catalog", "title": "📖 Каталог"},
            {"id": "search_help", "title": "🔍 Поиск"},
            {"id": "contact_manager", "title": "💬 Менеджер"}
        ]
        
        await whatsapp_client.send_buttons(
            to=to,
            text=welcome_text,
            buttons=buttons
        )
        
        logger.info(f"✓ Sent welcome menu to {to}")
    
    except Exception as e:
        logger.error(f"❌ Error sending welcome: {e}")


async def send_store_location(to: str):
    """Send store location (physical address)"""
    try:
        # ZETA Taldykorgan location (example coordinates)
        await whatsapp_client.send_location(
            to=to,
            latitude=45.0158,
            longitude=78.3737,
            name="ZETA Furniture Талдыкорган",
            address="ул. Примерная, 123, Талдыкорган, Казахстан"
        )
        
        await whatsapp_client.send_text(
            to=to,
            text="📍 Наш адрес!\n\nРабочие часы:\nПн-Сб: 10:00 - 20:00\nВс: 11:00 - 18:00\n\n📞 Телефон: +7 (XXX) XXX-XX-XX"
        )
        
        logger.info(f"✓ Sent location to {to}")
    
    except Exception as e:
        logger.error(f"❌ Error sending location: {e}")


async def _handle_manager_contact(phone: str, sku: str):
    """Handle manager contact request"""
    try:
        # Log escalation to admin platform
        from core.escalation import log_escalation
        await log_escalation(
            user_phone=phone,
            product_sku=sku,
            reason="manager_request"
        )
        
        await whatsapp_client.send_text(
            to=phone,
            text="""✅ Менеджер получил ваш запрос!

Наш менеджер свяжется с вами в ближайшее время (обычно в течение 30 минут).

Вы также можете позвонить:
📞 +7 (XXX) XXX-XX-XX

Или продолжить поиск - я всегда на связи! 😊"""
        )
    
    except Exception as e:
        logger.error(f"❌ Manager contact error: {e}")


async def _send_product_list_text(to: str, products: List[Dict]):
    """Fallback: send product list as simple text"""
    lines = ["🪑 *Вот что нашёл:*\n"]
    
    for i, product in enumerate(products[:5], 1):
        lines.append(f"{i}. {product['name']}")
        lines.append(f"   📦 Артикул: {product['sku']}")
        lines.append(f"   🎨 {product.get('category', '')}")
        lines.append("")
    
    lines.append("Напишите номер товара или артикул для подробностей!")
    
    await whatsapp_client.send_text(to=to, text="\n".join(lines))


__all__ = [
    "send_product_list",
    "send_product_details",
    "handle_button_response",
    "handle_list_response",
    "send_welcome_menu",
    "send_store_location"
]
