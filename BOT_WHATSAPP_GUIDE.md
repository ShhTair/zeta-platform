# 📱 ZETA WhatsApp Bot - Complete Guide

**Platform:** WhatsApp Cloud API (Meta)  
**Mode:** Webhook  
**AI Model:** GPT-4o-mini  
**Location:** `apps/whatsapp-bot/`

---

## 🎯 What It Does

Enhanced AI shopping assistant with WhatsApp-specific features.

**Unique Features vs Telegram:**
- 🎤 Voice messages (Whisper transcription)
- 🔔 Price alerts (scheduled notifications)
- 🧠 Smart recommendations (10-message context)
- 👤 User preferences tracking
- 📋 List messages (better than buttons)
- ⚡ Quick reply buttons (max 3)
- 📝 Template messages (pre-approved)
- 🎯 Better AI (longer context)

---

## 🏗️ Architecture

### File Structure

```
apps/whatsapp-bot/
├── main.py                    # FastAPI webhook server
├── .env                       # Environment variables
├── requirements.txt           # Dependencies
├── Dockerfile                 # Container build
│
├── handlers/                  # Request handlers
│   ├── messages.py            # Text messages
│   ├── media.py               # Images, voice, docs
│   └── interactive.py         # Buttons & lists
│
├── core/                      # Core logic
│   ├── ai_assistant.py        # OpenAI (10-msg context)
│   ├── product_search.py      # Search logic
│   ├── user_context.py        # User preferences
│   ├── alerts.py              # Price alert system
│   ├── escalation.py          # Manager escalation
│   ├── memory.py              # Redis memory
│   └── rate_limiter.py        # Rate limiting
│
├── integrations/              # Future integrations
│   ├── onec.py                # 1C stub
│   └── bitrix24.py            # Bitrix24 stub
│
└── templates/                 # WhatsApp templates
    └── message_templates.yaml # Pre-approved messages
```

---

## 🔄 How It Works

### Request Flow

```
WhatsApp → Webhook → FastAPI → Handler → AI → Format → Send

1. User sends message (text/voice/image)
   ↓
2. WhatsApp forwards to webhook
   ↓
3. FastAPI validates & routes
   ↓
4. Load user context (Redis)
   ↓
5. Process based on type:
   - Text → AI conversation
   - Voice → Whisper transcription → AI
   - Image → Vision API → Search
   - Button → Handle callback
   ↓
6. AI generates response (10-message context)
   ↓
7. Format for WhatsApp:
   - Quick reply buttons (max 3)
   - List messages (if many options)
   - Media messages (images)
   ↓
8. Send via WhatsApp Cloud API
   ↓
9. Update memory & preferences
```

---

## 🧠 AI Prompts & Logic

### System Prompt (Enhanced)

```python
system_prompt = """
Ты - продвинутый AI-ассистент мебельного магазина ZETA.

**Контекст:** У тебя есть история последних 10 сообщений пользователя.

**Твои задачи:**
1. Помогать найти мебель с учётом предпочтений
2. Запоминать стиль, бюджет, цвета пользователя
3. Предлагать похожие товары
4. Уведомлять о скидках (через price alerts)

**User Preferences Tracking:**
- Если пользователь упоминает бюджет → запомни
- Если выбирает цвет → предлагай в том же стиле
- Если смотрит диваны → рекомендуй столики

**Functions:**
- search_products(query, category, filters)
- get_recommendations(user_id, based_on_product)
- set_price_alert(user_id, product_id, target_price)
- track_preference(user_id, key, value)

**Tone:**
- Ещё более дружелюбный
- Персонализированный
- Проактивный (предлагай, не жди вопроса)

**Examples:**
User: "хочу красный диван"
You: "🛋️ Отлично! Вижу вы любите яркие цвета. У нас 5 красных диванов.
Какой бюджет? Или показать все варианты?"

[User views product]
You: "👀 Заметил, вас интересует диван 'Комфорт'. К нему отлично подойдёт 
журнальный столик в том же стиле. Показать?"

[Price drops]
You: "🔔 Цена на диван 'Классика' снизилась! 180000 → 150000 (-17%)"
"""
```

### Context Management (10 messages)

```python
# core/ai_assistant.py
async def get_ai_response(user_id: str, message: str):
    # Load last 10 messages (vs 5 in Telegram)
    history = await memory.get_last_n_messages(user_id, n=10)
    
    # Load user preferences
    prefs = await memory.get_user_preferences(user_id)
    # Example: {"budget": 200000, "preferred_color": "красный", 
    #           "style": "современный", "viewed_categories": ["Диваны"]}
    
    # Inject preferences into system prompt
    system_prompt_with_prefs = system_prompt + f"""
    
**User Preferences:**
- Budget: {prefs.get('budget', 'unknown')}
- Preferred colors: {prefs.get('preferred_color', 'any')}
- Style: {prefs.get('style', 'any')}
- Previously viewed: {prefs.get('viewed_categories', [])}
"""
    
    # Call OpenAI
    response = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt_with_prefs},
            *history,
            {"role": "user", "content": message}
        ],
        functions=[
            search_products_function,
            get_recommendations_function,
            set_price_alert_function,
            track_preference_function
        ]
    )
    
    return response
```

---

## 🎤 Voice Messages (Whisper)

### Implementation

```python
# handlers/media.py
async def handle_voice_message(message):
    # Download voice file from WhatsApp
    media_id = message['audio']['id']
    audio_url = await whatsapp_api.get_media_url(media_id)
    audio_file = await download_file(audio_url)
    
    # Transcribe with Whisper
    transcription = await openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="ru"  # Russian
    )
    
    # Process as text
    text = transcription.text
    response = await ai_assistant.get_response(user_id, text)
    
    # Send text response (don't send voice back)
    await whatsapp_api.send_message(user_id, response)
```

**When to use:**
- User sends voice note → Transcribe → Respond with text
- Don't send voice responses (text is clearer)

---

## 🔔 Price Alerts System

### How It Works

```python
# core/alerts.py
import schedule

# User sets alert
async def set_alert(user_id: str, product_id: str, target_price: int):
    alert = {
        "user_id": user_id,
        "product_id": product_id,
        "current_price": await get_product_price(product_id),
        "target_price": target_price,
        "created_at": datetime.now()
    }
    
    # Store in Redis
    await redis.hset(f"price_alert:{user_id}:{product_id}", mapping=alert)

# Background job (runs every 24 hours)
@schedule.every(24).hours.do
async def check_price_alerts():
    # Get all active alerts
    alerts = await redis.scan_iter("price_alert:*")
    
    for alert_key in alerts:
        alert = await redis.hgetall(alert_key)
        product_id = alert['product_id']
        
        # Check current price
        current_price = await api_client.get_product_price(product_id)
        
        # If price dropped below target
        if current_price <= int(alert['target_price']):
            # Send WhatsApp template message
            await send_price_alert_notification(
                user_id=alert['user_id'],
                product_id=product_id,
                old_price=alert['current_price'],
                new_price=current_price
            )
            
            # Mark alert as triggered
            await redis.delete(alert_key)
```

### WhatsApp Template Message

```yaml
# templates/message_templates.yaml
price_alert:
  name: "price_alert_notification"
  language: "ru"
  template: |
    🔔 *Цена снижена!*
    
    {{product_name}}
    
    Было: {{old_price}} ₸
    Стало: {{new_price}} ₸
    Скидка: {{discount}}%
    
    Успейте купить! 🛒
  
  buttons:
    - type: "quick_reply"
      text: "Подробнее"
    - type: "quick_reply"
      text: "Купить сейчас"
```

---

## 🧠 Smart Recommendations

### Implementation

```python
# core/product_search.py
async def get_smart_recommendations(user_id: str, context: dict):
    # Get user history
    viewed_products = await memory.get_set(f"user:{user_id}:viewed")
    preferences = await memory.get_user_preferences(user_id)
    
    # Analyze patterns
    categories_viewed = [p.category for p in viewed_products]
    most_viewed_category = max(set(categories_viewed), key=categories_viewed.count)
    
    # Build recommendation query
    query = {
        "category": most_viewed_category,
        "price_max": preferences.get('budget', 999999),
        "exclude_ids": [p.id for p in viewed_products],  # Don't repeat
        "limit": 5
    }
    
    # If user prefers certain style
    if preferences.get('style'):
        query['style'] = preferences['style']
    
    # Get recommendations
    products = await api_client.search_products(**query)
    
    # Sort by relevance
    # (products that match multiple preferences score higher)
    scored_products = []
    for product in products:
        score = 0
        if product.color == preferences.get('preferred_color'):
            score += 2
        if product.style == preferences.get('style'):
            score += 3
        if 'sale' in product.tags:
            score += 1
        
        scored_products.append((score, product))
    
    scored_products.sort(reverse=True, key=lambda x: x[0])
    
    return [p for _, p in scored_products[:5]]
```

---

## 👤 User Preferences Tracking

### Auto-Detection

```python
# core/user_context.py
async def extract_preferences(user_id: str, message: str, context: dict):
    # Budget detection
    budget_pattern = r'(\d+)\s*(?:тысяч|тыс|к|000)'
    if match := re.search(budget_pattern, message):
        budget = int(match.group(1)) * 1000
        await save_preference(user_id, 'budget', budget)
    
    # Color preference
    colors = ['красный', 'синий', 'белый', 'черный', 'серый', 'коричневый']
    for color in colors:
        if color in message.lower():
            await save_preference(user_id, 'preferred_color', color)
    
    # Style preference
    styles = ['современный', 'классический', 'минимализм', 'лофт']
    for style in styles:
        if style in message.lower():
            await save_preference(user_id, 'style', style)
    
    # Track viewed products
    if context.get('action') == 'view_product':
        await add_to_viewed(user_id, context['product_id'])
```

---

## 📋 Interactive UI

### List Messages (Better than Buttons)

```python
# When showing 5+ products, use list instead of buttons
async def send_product_list(user_id: str, products: list):
    sections = [{
        "title": "Диваны",
        "rows": [
            {
                "id": p.id,
                "title": p.name,
                "description": f"{p.price:,} ₸"
            }
            for p in products[:10]  # Max 10
        ]
    }]
    
    await whatsapp_api.send_list_message(
        to=user_id,
        header="Найденные товары",
        body="Выберите товар для подробностей:",
        button_text="Показать товары",
        sections=sections
    )
```

### Quick Reply Buttons (Max 3)

```python
# For simple choices, use quick reply buttons
async def send_with_quick_replies(user_id: str, text: str):
    await whatsapp_api.send_message(
        to=user_id,
        type="interactive",
        interactive={
            "type": "button",
            "body": {"text": text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "yes", "title": "Да"}},
                    {"type": "reply", "reply": {"id": "no", "title": "Нет"}},
                    {"type": "reply", "reply": {"id": "more", "title": "Ещё"}},
                ]
            }
        }
    )
```

---

## 🔧 Configuration

### Environment Variables

```bash
# WhatsApp Cloud API
WHATSAPP_TOKEN=EAAJ...                    # Access token
WHATSAPP_PHONE_ID=103876...               # Phone number ID
WHATSAPP_VERIFY_TOKEN=zeta_webhook_2026   # Webhook verify

# Backend & AI
API_URL=https://zeta-api...
OPENAI_API_KEY=sk-proj-...
REDIS_URL=redis://...

# Features
ENABLE_VOICE_TRANSCRIPTION=true
ENABLE_PRICE_ALERTS=true
ENABLE_SMART_RECOMMENDATIONS=true
ALERT_CHECK_INTERVAL=86400  # 24 hours
```

---

## 🚀 How to Improve

### 1. Better Recommendations

**File:** `core/product_search.py`

**Add collaborative filtering:**
```python
async def collaborative_filtering(user_id: str):
    # Find users with similar preferences
    similar_users = await find_similar_users(user_id)
    
    # Get products they viewed but current user hasn't
    recommendations = []
    for similar_user in similar_users[:5]:
        their_products = await get_viewed_products(similar_user)
        my_products = await get_viewed_products(user_id)
        
        new_products = set(their_products) - set(my_products)
        recommendations.extend(new_products)
    
    return recommendations[:10]
```

### 2. Multi-language Voice

**File:** `handlers/media.py`

**Detect language automatically:**
```python
async def transcribe_voice(audio_file):
    # Let Whisper auto-detect language
    transcription = await openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        # Don't specify language - auto-detect
    )
    
    detected_lang = transcription.language  # 'ru', 'kz', 'en'
    text = transcription.text
    
    # Respond in same language
    await ai_assistant.get_response(user_id, text, language=detected_lang)
```

### 3. Proactive Suggestions

**File:** `core/ai_assistant.py`

**Add proactive logic:**
```python
async def check_for_proactive_suggestions(user_id: str):
    last_activity = await redis.get(f"user:{user_id}:last_active")
    
    # If user hasn't interacted in 7 days
    if (datetime.now() - last_activity).days >= 7:
        # Check for new products in their preferred categories
        prefs = await get_user_preferences(user_id)
        new_products = await api_client.get_new_products(
            category=prefs.get('viewed_categories', []),
            since=last_activity
        )
        
        if new_products:
            await send_template_message(
                user_id=user_id,
                template="new_products_notification",
                params={"count": len(new_products)}
            )
```

---

## 🐛 Common Issues & Fixes

### Issue 1: Voice не транскрибируется

**Debug:**
```bash
# Check ffmpeg installed
docker exec <container> ffmpeg -version

# Check audio format
file /tmp/voice.ogg
```

**Fix:**
```python
# Convert to supported format first
import ffmpeg
audio_converted = ffmpeg.input('voice.ogg').output('voice.mp3').run()
```

### Issue 2: Price alerts не срабатывают

**Debug:**
```python
# Check scheduler running
import schedule
print(schedule.jobs)  # Should show check_price_alerts

# Check Redis alerts
redis-cli KEYS "price_alert:*"
```

**Fix:**
```python
# Run scheduler in background thread
import threading
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

thread = threading.Thread(target=run_scheduler, daemon=True)
thread.start()
```

---

## 📊 Analytics

Track:
- Voice message usage
- Price alerts set/triggered
- Recommendation click-through rate
- User preference accuracy

```sql
-- Most popular features
SELECT 
  feature,
  COUNT(*) as usage_count
FROM analytics_events
WHERE platform = 'whatsapp'
GROUP BY feature
ORDER BY usage_count DESC;
```

---

## 🔗 WhatsApp Cloud API Setup

### 1. Create Meta Business Account

1. Go to https://business.facebook.com
2. Create Business Account
3. Add WhatsApp product

### 2. Get Credentials

```
WHATSAPP_TOKEN       - From App Dashboard → WhatsApp → API Setup
WHATSAPP_PHONE_ID    - From Phone Numbers tab
WHATSAPP_VERIFY_TOKEN - Create your own (any string)
```

### 3. Setup Webhook

```bash
# Webhook URL
https://zeta-whatsapp-bot.../webhook

# Verify token
zeta_webhook_verify_2026

# Subscribe to:
- messages
- message_status
```

### 4. Add Template Messages

Templates need pre-approval (1-2 days):

```
Name: price_alert_notification
Category: UTILITY
Language: Russian
Body: 🔔 Цена снижена! {{1}} Было: {{2}} ₸ Стало: {{3}} ₸
```

---

**Last Updated:** 2026-02-20  
**Version:** 1.0  
**Status:** Code Ready (Meta setup needed)
