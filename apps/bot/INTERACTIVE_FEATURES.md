# 🎨 Interactive UI Features - Implementation Guide

## ✅ Completed Features

### 1. **Inline Keyboards Everywhere** 🎯

#### Product Selection
- Beautiful product list with emoji icons
- Each product shows: 🪑 Name (truncated) • Price
- Max 5 products per page
- Automatic pagination with "📄 Показать ещё" button
- "🔄 Новый поиск" button for starting fresh

**Implementation:** `handlers/interactive.py` → `create_product_list_keyboard()`

#### Quick Filters
When user enters vague queries (e.g., "стул", "диван"), bot shows:
- 🏠 Для дома
- 🏢 Для офиса
- 🎨 По цвету (asks user to specify)
- 💰 По цене (shows price ranges)
- 📋 Показать всё

**Implementation:** `handlers/interactive.py` → `create_quick_filters_keyboard()`

#### Product Actions
On product detail page, each product has:
- 📸 Фото - View product photos
- 🔗 Ссылка на сайт - Direct website link
- 💬 Связаться с менеджером - Contact support (creates CRM deal)
- ↩️ Назад к списку - Return to search results

**Implementation:** `handlers/interactive.py` → `create_product_actions_keyboard()`

---

### 2. **Photo Sharing** 📸

#### Single Photo Mode
```python
@router.callback_query(F.data.startswith("photo_"))
async def send_product_photos(callback: CallbackQuery, state: FSMContext):
    # Sends product photo with caption
    # Falls back gracefully if no photo available
```

#### Photo Carousel (Media Group)
```python
async def send_product_carousel(message, products, state):
    # Sends up to 10 product photos as album
    # First photo has caption with name, SKU, price
    # After carousel, shows interactive button list
```

**Usage:**
- User clicks "📸 Фото" button → sends photo
- Search results can show as carousel if enabled
- Supports multiple images per product

---

### 3. **Website Links** 🔗

```python
@router.callback_query(F.data.startswith("link_"))
async def send_product_link(callback: CallbackQuery):
    # Generates link: https://zeta.kz/products/{sku}
    # Shows inline button "🌐 Открыть на сайте"
```

**Features:**
- Direct links to product pages
- Inline URL button for one-tap opening
- Preview disabled for clean look

---

### 4. **Manager Contact** 💬

```python
@router.callback_query(F.data.startswith("manager_"))
async def contact_manager(callback: CallbackQuery, state: FSMContext):
    # Creates Bitrix CRM deal
    # Shows contact info (phone, email, telegram)
    # Logs escalation with user context
```

**Features:**
- Automatic CRM deal creation
- Deal ID returned to user
- Context preserved (user info, product SKU)
- Fallback if CRM fails

---

### 5. **Pagination** 📄

```python
@router.callback_query(F.data.startswith("more_"))
async def show_more_products(callback: CallbackQuery, state: FSMContext):
    # Offset stored in state
    # Shows next 5 products
    # Updates page indicator
```

**Features:**
- Fetches up to 20 products initially
- Shows 5 per page
- "Показать ещё" button appears if more results
- State-based offset tracking

---

### 6. **Quick Actions Menu** 🎮

```python
@router.message(F.text == "/menu")
async def show_menu(message: types.Message):
    # Shows beautiful action menu
```

**Menu Options:**
- 🔍 Искать товар
- 📸 Поиск по фото (placeholder for future)
- 🏷️ Популярные товары
- 💬 Связаться

**Also shown:**
- On `/start` command
- After "🔄 Новый поиск"
- When no results found

---

### 7. **Product Carousel** 🎠

```python
async def send_product_carousel(message, products, state):
    media_group = []
    for product in products[:10]:
        if product.get('image_url'):
            media_group.append(InputMediaPhoto(...))
    
    await message.answer_media_group(media_group)
```

**Features:**
- Up to 10 photos at once
- First photo has full caption
- Interactive buttons shown after carousel
- Graceful fallback to button list if no images

---

## 🏗️ Architecture

### File Structure

```
handlers/
├── interactive.py              # ⭐ NEW: All inline keyboard logic
├── conversation_interactive.py # ⭐ NEW: Enhanced conversation with buttons
├── start.py                    # Updated: Shows menu on /start
├── callbacks.py                # Legacy: Backward compatibility
├── conversation.py             # Legacy: Old text-based flow
└── product_inquiry.py          # Legacy: Old product search
```

### Handler Priority (Order in main.py)

```python
1. start.router                      # /start command
2. interactive.router                # ⭐ NEW: Inline keyboards
3. conversation_interactive.router   # ⭐ NEW: Enhanced search
4. callbacks.router                  # Legacy callbacks
5. product_inquiry.router            # Legacy product search
6. escalation.router                 # Escalation handlers
```

---

## 🎯 User Flow Examples

### Example 1: Simple Search

```
User: "стул"
Bot: 🤔 Уточните, пожалуйста
     Какой именно стул вас интересует?
     [🏠 Для дома] [🏢 Для офиса] [🎨 По цвету] [💰 По цене]

User: *clicks "🏠 Для дома"*
Bot: 🔍 Ищу в каталоге...
     📦 Нашёл 15 товаров!
     [🪑 Стул деревянный "Классик" • 45,000 ₸]
     [🪑 Кресло офисное "Комфорт" • 67,500 ₸]
     ...
     [📄 Показать ещё] [🔄 Новый поиск]

User: *clicks product*
Bot: 🪑 Стул деревянный "Классик"
     📦 Артикул: SK-12345
     📝 Описание: ...
     💰 Цена: 45,000 ₸
     [📸 Фото] [🔗 Ссылка на сайт]
     [💬 Связаться с менеджером]
     [↩️ Назад к списку]

User: *clicks "📸 Фото"*
Bot: *sends photo(s)*
```

### Example 2: Quick Menu

```
User: /menu
Bot: 🪑 Меню действий
     Выберите, что вас интересует:
     [🔍 Искать товар]
     [📸 Поиск по фото]
     [🏷️ Популярные товары]
     [💬 Связаться]

User: *clicks "🏷️ Популярные товары"*
Bot: 🏷️ Популярные товары
     *shows carousel of 10 photos*
     [Product buttons...]
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file
WEBSITE_BASE_URL=https://zeta.kz  # Product page base URL
MAX_PRODUCTS_PER_PAGE=5           # Pagination size
MAX_CAROUSEL_PHOTOS=10            # Max photos in carousel
```

### Customization Points

#### `handlers/interactive.py`

```python
# Line 15-17: Configuration constants
MAX_PRODUCTS_PER_PAGE = 5
MAX_CAROUSEL_PHOTOS = 10
WEBSITE_BASE_URL = "https://zeta.kz"
```

#### Contact Information

```python
# handlers/interactive.py → action_contact()
contact_info = """
📞 Телефон: +7 (XXX) XXX-XX-XX  # ← Update this
✉️ Email: info@zeta.kz           # ← Update this
🌐 Сайт: https://zeta.kz         # ← Update this
"""
```

---

## 🧪 Testing Checklist

### ✅ Inline Keyboards
- [ ] Product list shows with buttons
- [ ] Pagination works ("Показать ещё")
- [ ] "Новый поиск" resets search
- [ ] Quick filters appear for vague queries
- [ ] Product detail buttons all work

### ✅ Photo Sharing
- [ ] Single photo sends correctly
- [ ] Carousel sends multiple photos
- [ ] Fallback works when no photo
- [ ] Caption shows product info

### ✅ Website Links
- [ ] Link button opens correct URL
- [ ] URL format is valid
- [ ] Preview displays correctly

### ✅ Manager Contact
- [ ] CRM deal creates successfully
- [ ] Deal ID returns to user
- [ ] Contact info displays
- [ ] Fallback works if CRM fails

### ✅ Pagination
- [ ] Shows 5 products per page
- [ ] "Показать ещё" loads next page
- [ ] Page indicator updates
- [ ] State persists across pages

### ✅ Menu Navigation
- [ ] /menu shows action buttons
- [ ] /start shows welcome menu
- [ ] All menu actions work
- [ ] Back buttons return correctly

---

## 🚀 Deployment

### 1. Backup Old Handlers (Optional)

```bash
cd /home/tair/.openclaw/workspace/zeta-platform/apps/bot/handlers
cp conversation.py conversation_legacy.py
cp callbacks.py callbacks_legacy.py
```

### 2. Restart Bot

```bash
# If using systemd
sudo systemctl restart zeta-bot

# If using Docker
docker-compose restart bot

# If using PM2
pm2 restart zeta-bot
```

### 3. Test Interactive Features

Send these commands to bot:
```
/start          # Should show beautiful menu
стул            # Should show filters
/menu           # Should show quick actions
```

---

## 📊 Success Metrics

### Before (Text-only):
- ❌ Users had to type everything
- ❌ No visual feedback
- ❌ Hard to browse products
- ❌ High drop-off rate

### After (Interactive UI):
- ✅ Tap buttons instead of typing
- ✅ Visual product browsing
- ✅ Quick filters for refinement
- ✅ Photos and links one tap away
- ✅ Professional, modern UX
- ✅ Lower friction → higher engagement

---

## 🎉 Next Steps

### Enhancements (Future)
1. **Photo Search** - Upload photo → find similar products
2. **Favorites** - Save products with ⭐ button
3. **Cart System** - Add to cart, checkout flow
4. **Voice Messages** - Record voice query
5. **Location-Based** - Show nearest showroom
6. **Comparison** - Compare 2-3 products side-by-side

### Integration Ideas
1. **Analytics** - Track button click rates
2. **A/B Testing** - Test different button texts
3. **Personalization** - Remember user preferences
4. **Notifications** - Price drop alerts
5. **Reviews** - Show product ratings

---

## 📚 Resources

- **Aiogram Docs**: https://docs.aiogram.dev/
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Inline Keyboards**: https://core.telegram.org/bots/features#inline-keyboards

---

## 🎨 Design Philosophy

### Principles
1. **Tap > Type** - Every action should be a button tap
2. **Visual First** - Show photos whenever possible
3. **Clear Hierarchy** - Most important actions on top
4. **Progressive Disclosure** - Start simple, reveal details
5. **Instant Feedback** - Always acknowledge user actions
6. **Graceful Degradation** - Fallback for missing data

### Button Text Guidelines
- Use emoji for recognition 🎯
- Keep text short (< 40 chars)
- Action-oriented ("Искать", not "Поиск")
- Consistent style across UI

---

**Built with ❤️ for ZETA Platform**
