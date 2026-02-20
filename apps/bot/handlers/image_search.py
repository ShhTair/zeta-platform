"""
Image search handler - OCR + Vision API + reverse product search
Multi-method approach: OCR → Vision API → fallback clarification
"""
import logging
import os
import re
import tempfile
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image
import pytesseract
from openai import AsyncOpenAI

from handlers.start import ConversationState

logger = logging.getLogger(__name__)

router = Router()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# SKU pattern for Russian product codes
# Example: КР-СТ-12345, ДИВ-КЛА-001
SKU_PATTERN = r'[А-ЯA-Z]{2,5}-[А-ЯA-Z]{2,5}-\d{2,6}'

# Common product name patterns for OCR extraction
PRODUCT_PATTERNS = [
    r'(?:артикул|арт\.?|SKU|код)\s*[:=#]?\s*([А-ЯA-Z0-9\-]+)',
    r'([А-Я][а-я]+(?:\s+[А-Я][а-я]+){1,4})',  # Capitalized product names
]


async def download_photo(bot, photo: types.PhotoSize) -> str:
    """
    Download photo from Telegram to temp file
    
    Returns:
        Path to downloaded file
    """
    file = await bot.get_file(photo.file_id)
    temp_dir = Path(tempfile.gettempdir())
    temp_path = temp_dir / f"{photo.file_id}.jpg"
    
    await bot.download_file(file.file_path, temp_path)
    logger.info(f"Downloaded photo to {temp_path}")
    
    return str(temp_path)


async def extract_text_with_ocr(image_path: str) -> str:
    """
    Extract text from image using Tesseract OCR
    Supports Russian and English
    
    Returns:
        Extracted text
    """
    try:
        image = Image.open(image_path)
        
        # Use both Russian and English for better recognition
        text = pytesseract.image_to_string(
            image,
            lang='rus+eng',
            config='--psm 6'  # Assume uniform block of text
        )
        
        logger.info(f"OCR extracted {len(text)} characters")
        return text.strip()
    
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""


def extract_sku_from_text(text: str) -> Optional[str]:
    """
    Extract product SKU from OCR text
    
    Returns:
        First found SKU or None
    """
    # Try exact SKU pattern
    skus = re.findall(SKU_PATTERN, text, re.IGNORECASE)
    if skus:
        return skus[0].upper()
    
    # Try product code patterns
    for pattern in PRODUCT_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            candidate = matches[0].strip()
            # Validate it looks like a SKU (has dashes and numbers)
            if '-' in candidate or re.search(r'\d', candidate):
                return candidate.upper()
    
    return None


async def analyze_image_with_vision(image_path: str) -> Optional[str]:
    """
    Analyze product image with OpenAI Vision API
    
    Returns:
        Product description or None if API unavailable
    """
    if not openai_client:
        logger.warning("OpenAI client not configured")
        return None
    
    try:
        # Read image as base64
        import base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        image_url = f"data:image/jpeg;base64,{image_data}"
        
        # Call Vision API
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective vision model
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Опишите этот товар мебели КРАТКО (1-2 предложения):\n"
                            "- Тип товара (стул, стол, диван и т.д.)\n"
                            "- Цвет и материал\n"
                            "- Стиль (современный, классический и т.д.)\n"
                            "- Ключевые особенности\n\n"
                            "Если это НЕ мебель - скажите что за товар."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }],
            max_tokens=200
        )
        
        description = response.choices[0].message.content.strip()
        logger.info(f"Vision API: {description}")
        
        return description
    
    except Exception as e:
        logger.error(f"Vision API failed: {e}")
        return None


async def search_by_sku(api_client, sku: str, city_id: str) -> List[Dict]:
    """
    Search products by exact SKU match
    
    Returns:
        List of matching products
    """
    try:
        # Try exact SKU search
        products = await api_client.search_products(
            query=sku,
            city_id=city_id,
            limit=3
        )
        
        # Filter to exact SKU matches
        exact_matches = [
            p for p in products 
            if p.get('sku', '').upper() == sku.upper()
        ]
        
        return exact_matches if exact_matches else products[:1]
    
    except Exception as e:
        logger.error(f"SKU search failed: {e}")
        return []


async def search_by_description(api_client, description: str, city_id: str) -> List[Dict]:
    """
    Search products by Vision API description
    
    Returns:
        List of matching products
    """
    try:
        products = await api_client.search_products(
            query=description,
            city_id=city_id,
            limit=7
        )
        
        return products
    
    except Exception as e:
        logger.error(f"Description search failed: {e}")
        return []


def format_products_message(products: List[Dict], method: str) -> str:
    """
    Format product list message
    
    Args:
        products: List of product dicts
        method: Search method used (for logging)
    
    Returns:
        Formatted message
    """
    if not products:
        return ""
    
    message = f"📦 <b>Нашёл по фото:</b>\n\n"
    
    if len(products) == 1:
        p = products[0]
        message += f"🪑 <b>{p.get('name', 'Товар')}</b>\n"
        message += f"💰 Цена: {p.get('price', 'уточняйте')} ₽\n"
        if p.get('sku'):
            message += f"📋 Артикул: {p['sku']}\n"
    else:
        message += f"Найдено похожих товаров: {len(products)}\n"
        message += "Выберите подходящий из списка ниже 👇"
    
    return message


def create_product_keyboard(products: List[Dict]) -> InlineKeyboardMarkup:
    """
    Create inline keyboard with product buttons
    
    Args:
        products: List of product dicts
    
    Returns:
        Inline keyboard markup
    """
    buttons = []
    
    for product in products[:7]:  # Limit to 7 to avoid UI overflow
        name = product.get("name", "Товар")
        price = product.get("price", 0)
        sku = product.get("sku") or product.get("id")
        
        # Truncate long names
        button_text = f"🪑 {name[:35]}" + ("..." if len(name) > 35 else "")
        if price:
            button_text += f" • {price} ₽"
        
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"product_{sku}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.photo)
async def handle_product_photo(message: types.Message, state: FSMContext):
    """
    Handle photo message with hybrid search approach:
    1. Try OCR to extract SKU
    2. If no SKU, use Vision API to describe product
    3. Search catalog by SKU or description
    4. If nothing found, offer manual search
    """
    api_client = message.bot.get("api_client")
    city_id = "default"  # TODO: Get from user context
    
    # Send "searching" status
    status_msg = await message.answer("🔍 Ищу товар по фото...")
    
    try:
        # Step 1: Download photo
        photo = message.photo[-1]  # Get highest resolution
        photo_path = await download_photo(message.bot, photo)
        
        products = []
        search_method = None
        
        # Step 2: Try OCR first (fast, works for screenshots with SKU)
        ocr_text = await extract_text_with_ocr(photo_path)
        
        if ocr_text:
            logger.info(f"OCR text: {ocr_text[:100]}")
            
            # Look for SKU in OCR text
            sku = extract_sku_from_text(ocr_text)
            
            if sku:
                logger.info(f"Found SKU via OCR: {sku}")
                products = await search_by_sku(api_client, sku, city_id)
                search_method = "OCR → SKU"
        
        # Step 3: If OCR didn't find anything, use Vision API
        if not products and openai_client:
            description = await analyze_image_with_vision(photo_path)
            
            if description:
                logger.info(f"Vision API description: {description}")
                products = await search_by_description(api_client, description, city_id)
                search_method = "Vision API"
        
        # Clean up temp file
        try:
            os.unlink(photo_path)
        except:
            pass
        
        # Step 4: Display results
        await status_msg.delete()
        
        if products:
            # Success - found products
            message_text = format_products_message(products, search_method)
            keyboard = create_product_keyboard(products)
            
            await message.answer(message_text, reply_markup=keyboard)
            await state.update_data(
                last_search_method="image",
                products=products
            )
            
            logger.info(
                f"User {message.from_user.id} found {len(products)} products "
                f"via {search_method}"
            )
        
        else:
            # No results - offer alternatives
            no_results = (
                "😔 Не смог найти товар по фото.\n\n"
                "Попробуйте:\n"
                "• Описать товар словами\n"
                "• Прислать фото с другого ракурса\n"
                "• Указать артикул, если он есть\n"
                "• Связаться с менеджером"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="📝 Описать словами",
                    callback_data="describe_product"
                )],
                [InlineKeyboardButton(
                    text="📞 Связаться с менеджером",
                    callback_data="escalate:manager"
                )]
            ])
            
            await message.answer(no_results, reply_markup=keyboard)
            await state.set_state(ConversationState.product_inquiry)
            
            logger.info(
                f"User {message.from_user.id} - no products found via image search"
            )
    
    except Exception as e:
        logger.error(f"Image search error: {e}", exc_info=True)
        
        await status_msg.delete()
        await message.answer(
            "❌ Произошла ошибка при обработке фото.\n"
            "Попробуйте описать товар текстом или свяжитесь с менеджером."
        )


@router.callback_query(F.data == "describe_product")
async def callback_describe_product(callback: types.CallbackQuery, state: FSMContext):
    """
    Handle "describe with words" callback after failed image search
    """
    await callback.message.answer(
        "💬 Опишите товар словами:\n"
        "Например: \"Деревянный стул со спинкой\" или \"Современный угловой диван\""
    )
    
    await state.set_state(ConversationState.product_inquiry)
    await callback.answer()
