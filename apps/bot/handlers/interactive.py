"""
Interactive UI Handler - Beautiful inline keyboards, photo sharing, links
Makes bot visually engaging and tap-friendly!
"""
import logging
from typing import List, Dict, Any, Optional
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    InputMediaPhoto,
    FSInputFile
)

from handlers.start import ConversationState

logger = logging.getLogger(__name__)

router = Router()

# Configuration
MAX_PRODUCTS_PER_PAGE = 5
MAX_CAROUSEL_PHOTOS = 10
WEBSITE_BASE_URL = "https://zeta.kz"  # Update with actual ZETA website


# ==================== UTILITY FUNCTIONS ====================

def create_product_list_keyboard(
    products: List[Dict[str, Any]], 
    offset: int = 0,
    show_more: bool = False
) -> InlineKeyboardMarkup:
    """
    Create beautiful product list with inline buttons
    Each product gets its own button with emoji and truncated name
    """
    buttons = []
    
    # Product buttons (5 per page)
    for product in products[offset:offset + MAX_PRODUCTS_PER_PAGE]:
        name = product.get("name", "Товар")
        sku = product.get("sku") or product.get("id", "unknown")
        price = product.get("price")
        
        # Format button text with emoji and price
        button_text = f"🪑 {name[:35]}"
        if len(name) > 35:
            button_text += "..."
        if price:
            button_text += f" • {price:,} ₸"
        
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"prod_{sku}"
            )
        ])
    
    # Navigation buttons
    nav_buttons = []
    
    # "Show More" button if there are more products
    if show_more and len(products) > offset + MAX_PRODUCTS_PER_PAGE:
        nav_buttons.append(
            InlineKeyboardButton(
                text="📄 Показать ещё",
                callback_data=f"more_{offset + MAX_PRODUCTS_PER_PAGE}"
            )
        )
    
    # "New Search" button
    nav_buttons.append(
        InlineKeyboardButton(
            text="🔄 Новый поиск",
            callback_data="new_search"
        )
    )
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_product_actions_keyboard(
    sku: str,
    has_photo: bool = False,
    has_website_link: bool = True
) -> InlineKeyboardMarkup:
    """
    Create action buttons for product detail page
    """
    buttons = []
    
    # Row 1: Photo and Website Link
    row1 = []
    if has_photo:
        row1.append(
            InlineKeyboardButton(
                text="📸 Фото",
                callback_data=f"photo_{sku}"
            )
        )
    if has_website_link:
        row1.append(
            InlineKeyboardButton(
                text="🔗 Ссылка на сайт",
                callback_data=f"link_{sku}"
            )
        )
    if row1:
        buttons.append(row1)
    
    # Row 2: Contact Manager
    buttons.append([
        InlineKeyboardButton(
            text="💬 Связаться с менеджером",
            callback_data=f"manager_{sku}"
        )
    ])
    
    # Row 3: Back button
    buttons.append([
        InlineKeyboardButton(
            text="↩️ Назад к списку",
            callback_data="back_list"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_quick_filters_keyboard() -> InlineKeyboardMarkup:
    """
    Create quick filter buttons for vague queries
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Для дома", callback_data="filter_home")],
        [InlineKeyboardButton(text="🏢 Для офиса", callback_data="filter_office")],
        [InlineKeyboardButton(text="🎨 По цвету", callback_data="filter_color")],
        [InlineKeyboardButton(text="💰 По цене", callback_data="filter_price")],
        [InlineKeyboardButton(text="📋 Показать всё", callback_data="filter_all")]
    ])


def create_quick_actions_menu() -> InlineKeyboardMarkup:
    """
    Create main menu with quick actions
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Искать товар", callback_data="action_search")],
        [InlineKeyboardButton(text="📸 Поиск по фото", callback_data="action_photo")],
        [InlineKeyboardButton(text="🏷️ Популярные товары", callback_data="action_popular")],
        [InlineKeyboardButton(text="💬 Связаться", callback_data="action_contact")]
    ])


# ==================== COMMAND HANDLERS ====================

@router.message(F.text == "/menu")
async def show_menu(message: types.Message):
    """Show quick actions menu"""
    await message.answer(
        "🪑 <b>Меню действий</b>\n\nВыберите, что вас интересует:",
        reply_markup=create_quick_actions_menu()
    )


# ==================== CALLBACK HANDLERS ====================

@router.callback_query(F.data.startswith("prod_"))
async def show_product_details(callback: types.CallbackQuery, state: FSMContext):
    """
    Show detailed product information with beautiful action buttons
    """
    api_client = callback.message.bot.get("api_client")
    sku = callback.data.split("_", 1)[1]
    
    # Get product from state cache
    state_data = await state.get_data()
    products = state_data.get("products", [])
    
    product = None
    for p in products:
        if str(p.get("sku", p.get("id"))) == str(sku):
            product = p
            break
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    # Format product details
    name = product.get("name", "Товар")
    sku_display = product.get("sku") or product.get("id", "N/A")
    description = product.get("description", "")
    price = product.get("price")
    stock = product.get("stock", 0)
    material = product.get("material", "")
    color = product.get("color", "")
    dimensions = product.get("dimensions", "")
    
    # Build message
    message_text = f"🪑 <b>{name}</b>\n\n"
    message_text += f"📦 <b>Артикул:</b> <code>{sku_display}</code>\n\n"
    
    if description:
        message_text += f"📝 <b>Описание:</b>\n{description[:300]}\n\n"
    
    # Characteristics
    message_text += "📏 <b>Характеристики:</b>\n"
    if material:
        message_text += f"• Материал: {material}\n"
    if color:
        message_text += f"• Цвет: {color}\n"
    if dimensions:
        message_text += f"• Размеры: {dimensions}\n"
    
    message_text += "\n"
    
    # Price and stock
    if price:
        message_text += f"💰 <b>Цена:</b> {price:,} ₸\n"
    message_text += f"📍 <b>Наличие:</b> {'✅ В наличии' if stock > 0 else '⏳ Под заказ'}\n"
    
    # Check if product has photo
    image_url = product.get("image_url") or product.get("primary_image")
    has_photo = bool(image_url)
    
    # Create action buttons
    keyboard = create_product_actions_keyboard(sku, has_photo=has_photo)
    
    # Send or edit message
    try:
        if image_url:
            # Send photo with caption
            await callback.message.answer_photo(
                photo=image_url,
                caption=message_text,
                reply_markup=keyboard
            )
            # Delete old message
            await callback.message.delete()
        else:
            # Edit existing message
            await callback.message.edit_text(
                message_text,
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Failed to show product details: {e}")
        await callback.message.answer(
            message_text,
            reply_markup=keyboard
        )
    
    # Save current product to state
    await state.update_data(current_product=product)
    await callback.answer()


@router.callback_query(F.data.startswith("photo_"))
async def send_product_photos(callback: types.CallbackQuery, state: FSMContext):
    """
    Send product photos (supports single or multiple)
    """
    sku = callback.data.split("_", 1)[1]
    
    state_data = await state.get_data()
    product = state_data.get("current_product")
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    # Get primary image
    primary_image = product.get("image_url") or product.get("primary_image")
    
    # Get additional images (if available)
    additional_images = product.get("images", [])
    
    if not primary_image and not additional_images:
        await callback.answer("😔 Фото пока нет", show_alert=True)
        return
    
    try:
        # If multiple images, send as media group (carousel)
        if additional_images and len(additional_images) > 1:
            media_group = []
            for idx, img_url in enumerate(additional_images[:MAX_CAROUSEL_PHOTOS]):
                caption = f"🪑 {product['name']}\n📦 Артикул: {sku}" if idx == 0 else None
                media_group.append(
                    InputMediaPhoto(media=img_url, caption=caption)
                )
            
            await callback.message.answer_media_group(media_group)
            await callback.answer("📸 Фото отправлены!")
        
        # Single image
        elif primary_image:
            await callback.message.answer_photo(
                photo=primary_image,
                caption=f"🪑 {product['name']}\n📦 Артикул: {sku}"
            )
            await callback.answer("📸 Фото отправлено!")
        
    except Exception as e:
        logger.error(f"Failed to send photos: {e}")
        await callback.answer("❌ Не удалось загрузить фото", show_alert=True)


@router.callback_query(F.data.startswith("link_"))
async def send_product_link(callback: types.CallbackQuery, state: FSMContext):
    """
    Send website link for the product
    """
    sku = callback.data.split("_", 1)[1]
    
    state_data = await state.get_data()
    product = state_data.get("current_product")
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    # Generate product link
    product_url = product.get("url") or f"{WEBSITE_BASE_URL}/products/{sku}"
    
    # Create inline button with URL
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Открыть на сайте", url=product_url)]
    ])
    
    await callback.message.answer(
        f"🔗 <b>Ссылка на товар:</b>\n\n{product_url}",
        reply_markup=keyboard,
        disable_web_page_preview=False
    )
    
    await callback.answer("🔗 Ссылка отправлена!")


@router.callback_query(F.data.startswith("manager_"))
async def contact_manager(callback: types.CallbackQuery, state: FSMContext):
    """
    Show manager contact information and log escalation
    """
    api_client = callback.message.bot.get("api_client")
    sku = callback.data.split("_", 1)[1]
    
    state_data = await state.get_data()
    product = state_data.get("current_product")
    
    if not product:
        await callback.answer("❌ Товар не найден", show_alert=True)
        return
    
    # Log escalation to Bitrix or database
    user = callback.from_user
    customer_name = user.full_name or user.username or "Клиент"
    customer_telegram = f"@{user.username}" if user.username else f"ID: {user.id}"
    
    message = f"Запрос на консультацию: {product.get('name')} (Артикул: {sku})"
    
    try:
        # Create escalation in CRM
        result = await api_client.create_bitrix_deal(
            customer_name=customer_name,
            customer_telegram=customer_telegram,
            product_id=sku,
            message=message,
            city_id="default"
        )
        
        deal_id = result.get("deal_id", "N/A")
        
        contact_message = f"""
💬 <b>Связь с менеджером</b>

Ваша заявка #{deal_id} создана!

📞 <b>Контакты:</b>
• Телефон: +7 (XXX) XXX-XX-XX
• Email: info@zeta.kz
• Telegram: @zeta_manager

<b>При обращении укажите артикул:</b> <code>{sku}</code>

Наш менеджер свяжется с вами в ближайшее время! ⚡
"""
        
        await callback.message.answer(contact_message)
        await callback.answer("✅ Заявка создана!")
        
        logger.info(f"Manager contact request: user={user.id}, product={sku}, deal={deal_id}")
    
    except Exception as e:
        logger.error(f"Failed to create escalation: {e}")
        
        # Fallback without CRM
        contact_message = f"""
💬 <b>Свяжитесь с менеджером:</b>

📞 Телефон: +7 (XXX) XXX-XX-XX
✉️ Email: info@zeta.kz

<b>Упомяните артикул:</b> <code>{sku}</code>
"""
        await callback.message.answer(contact_message)
        await callback.answer()


@router.callback_query(F.data == "back_list")
async def back_to_product_list(callback: types.CallbackQuery, state: FSMContext):
    """
    Return to product search results
    """
    state_data = await state.get_data()
    products = state_data.get("products", [])
    query = state_data.get("query", "")
    offset = state_data.get("offset", 0)
    
    if not products:
        await callback.message.answer(
            "🔍 <b>Введите новый поисковый запрос</b>",
            reply_markup=create_quick_actions_menu()
        )
        await callback.answer()
        return
    
    # Re-display product list
    count = len(products)
    response = f"📦 <b>Найдено товаров:</b> {count}\n"
    response += f"<b>Запрос:</b> «{query}»\n\n"
    response += "Выберите товар:"
    
    keyboard = create_product_list_keyboard(products, offset=offset, show_more=True)
    
    try:
        await callback.message.edit_text(response, reply_markup=keyboard)
    except:
        await callback.message.answer(response, reply_markup=keyboard)
    
    await callback.answer()


@router.callback_query(F.data.startswith("more_"))
async def show_more_products(callback: types.CallbackQuery, state: FSMContext):
    """
    Pagination: show next batch of products
    """
    new_offset = int(callback.data.split("_", 1)[1])
    
    state_data = await state.get_data()
    products = state_data.get("products", [])
    query = state_data.get("query", "")
    
    if not products or new_offset >= len(products):
        await callback.answer("Больше товаров нет", show_alert=True)
        return
    
    # Update offset in state
    await state.update_data(offset=new_offset)
    
    # Show next page
    response = f"📦 <b>Найдено товаров:</b> {len(products)}\n"
    response += f"<b>Запрос:</b> «{query}»\n\n"
    response += f"Страница {new_offset // MAX_PRODUCTS_PER_PAGE + 1}"
    
    keyboard = create_product_list_keyboard(products, offset=new_offset, show_more=True)
    
    await callback.message.edit_text(response, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "new_search")
async def start_new_search(callback: types.CallbackQuery, state: FSMContext):
    """
    Clear current search and start new one
    """
    # Clear search state
    await state.update_data(products=[], query="", offset=0)
    
    await callback.message.edit_text(
        "🔍 <b>Что вы ищете?</b>\n\nОпишите товар, который вам нужен:",
        reply_markup=create_quick_actions_menu()
    )
    
    await callback.answer("Новый поиск")


# ==================== FILTER HANDLERS ====================

@router.callback_query(F.data.startswith("filter_"))
async def handle_quick_filter(callback: types.CallbackQuery, state: FSMContext):
    """
    Apply quick filter to search
    """
    filter_type = callback.data.split("_", 1)[1]
    
    # Map filter to query modifier
    filters = {
        "home": "для дома",
        "office": "для офиса",
        "color": "по цвету",
        "price": "по цене",
        "all": ""
    }
    
    modifier = filters.get(filter_type, "")
    
    await callback.answer(f"Фильтр: {modifier or 'все'}")
    
    # Show search prompt with applied filter
    await callback.message.edit_text(
        f"🔍 <b>Фильтр:</b> {modifier or 'все товары'}\n\n"
        "Напишите, что именно вы ищете:",
        reply_markup=None
    )
    
    # Save filter to state
    await state.update_data(active_filter=filter_type)


# ==================== QUICK ACTION HANDLERS ====================

@router.callback_query(F.data == "action_search")
async def action_search(callback: types.CallbackQuery, state: FSMContext):
    """Quick action: Search products"""
    await callback.message.edit_text(
        "🔍 <b>Поиск товара</b>\n\nОпишите, что вы ищете:",
        reply_markup=None
    )
    await state.set_state(ConversationState.product_inquiry)
    await callback.answer()


@router.callback_query(F.data == "action_photo")
async def action_photo_search(callback: types.CallbackQuery):
    """Quick action: Photo search"""
    await callback.message.edit_text(
        "📸 <b>Поиск по фото</b>\n\n"
        "Отправьте фото товара или скриншот с артикулом!\n\n"
        "Я использую:\n"
        "• 🔍 OCR для извлечения текста и SKU\n"
        "• 🤖 AI Vision для описания товара\n"
        "• 📦 Поиск по каталогу (37K товаров)\n\n"
        "Просто пришлите фото! 📸"
    )
    await callback.answer()


@router.callback_query(F.data == "action_popular")
async def action_popular_products(callback: types.CallbackQuery, state: FSMContext):
    """Quick action: Show popular products"""
    api_client = callback.message.bot.get("api_client")
    
    await callback.answer("Загружаю популярные товары...")
    
    # Fetch popular/featured products
    try:
        products = await api_client.search_products(
            query="популярные",
            city_id="default",
            limit=10
        )
        
        if products:
            keyboard = create_product_list_keyboard(products, show_more=False)
            await callback.message.edit_text(
                "🏷️ <b>Популярные товары</b>\n\nВыберите товар:",
                reply_markup=keyboard
            )
            await state.update_data(products=products, query="популярные", offset=0)
        else:
            await callback.message.edit_text("❌ Не удалось загрузить товары")
    
    except Exception as e:
        logger.error(f"Failed to load popular products: {e}")
        await callback.message.edit_text("❌ Ошибка при загрузке")


@router.callback_query(F.data == "action_contact")
async def action_contact(callback: types.CallbackQuery):
    """Quick action: Contact support"""
    contact_info = """
💬 <b>Контакты</b>

📞 Телефон: +7 (XXX) XXX-XX-XX
✉️ Email: info@zeta.kz
🌐 Сайт: https://zeta.kz

📍 Адрес:
г. Алматы, ул. Пример, 123

⏰ Режим работы:
Пн-Пт: 09:00 - 18:00
Сб-Вс: выходной
"""
    
    await callback.message.edit_text(
        contact_info,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="↩️ Назад", callback_data="new_search")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "action_about")
async def action_about(callback: types.CallbackQuery):
    """Quick action: About company"""
    about_info = """
ℹ️ <b>О компании ZETA</b>

🏢 ZETA — ведущий поставщик качественной мебели для дома и офиса в Казахстане.

✨ <b>Наши преимущества:</b>
• Широкий ассортимент товаров
• Прямые поставки от производителей
• Конкурентные цены
• Быстрая доставка по всему Казахстану
• Профессиональная сборка и установка

🎯 <b>Миссия:</b>
Делать качественную мебель доступной для каждого!

📦 <b>Каталог:</b>
Более 1000+ товаров на складе
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Наш сайт", url="https://zeta.kz")],
        [InlineKeyboardButton(text="↩️ Назад в меню", callback_data="new_search")]
    ])
    
    await callback.message.edit_text(about_info, reply_markup=keyboard)
    await callback.answer()


# ==================== PRODUCT CAROUSEL ====================

async def send_product_carousel(
    message: types.Message,
    products: List[Dict[str, Any]],
    state: FSMContext
):
    """
    Send products as beautiful photo carousel (media group)
    Up to 10 photos maximum
    """
    media_group = []
    
    for idx, product in enumerate(products[:MAX_CAROUSEL_PHOTOS]):
        image_url = product.get("image_url") or product.get("primary_image")
        
        if not image_url:
            continue
        
        name = product.get("name", "Товар")
        sku = product.get("sku") or product.get("id", "")
        price = product.get("price")
        
        # Caption for first photo
        caption = None
        if idx == 0:
            caption = f"🪑 {name}\n📦 {sku}"
            if price:
                caption += f"\n💰 {price:,} ₸"
        
        media_group.append(
            InputMediaPhoto(media=image_url, caption=caption)
        )
    
    if media_group:
        try:
            await message.answer_media_group(media_group)
            
            # Send buttons after carousel
            keyboard = create_product_list_keyboard(products, show_more=False)
            await message.answer(
                "👆 Выберите товар для подробностей:",
                reply_markup=keyboard
            )
            
            # Save to state
            await state.update_data(products=products, offset=0)
            
        except Exception as e:
            logger.error(f"Failed to send carousel: {e}")
            # Fallback to regular list
            keyboard = create_product_list_keyboard(products, show_more=True)
            await message.answer(
                f"📦 <b>Найдено товаров:</b> {len(products)}\n\nВыберите товар:",
                reply_markup=keyboard
            )
    else:
        # No images available, show text list
        keyboard = create_product_list_keyboard(products, show_more=True)
        await message.answer(
            f"📦 <b>Найдено товаров:</b> {len(products)}\n\nВыберите товар:",
            reply_markup=keyboard
        )
