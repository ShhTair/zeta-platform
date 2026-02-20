# 📱 ZETA Telegram Bot - Complete Guide

**Bot:** @zeta_taldykorgan_bot  
**Mode:** Webhook (production)  
**AI Model:** GPT-4o-mini  
**Location:** `apps/bot/`

---

## 🎯 What It Does

AI-powered furniture shopping assistant for ZETA stores in Kazakhstan.

**Key Features:**
- 🤖 Natural language conversation
- 🔍 Product search & recommendations
- 📸 Image search (OCR + Vision API)
- ⌨️ Interactive inline keyboards
- 📷 Photo sharing & carousels
- 🌐 Direct website links
- 👤 Manager escalation
- 📊 Pagination (5 products/page)
- 💾 Conversation memory (Redis)
- 🚦 Rate limiting
- 🌍 Multilanguage (Russian/Kazakh)

---

## 🏗️ Architecture

### File Structure

```
apps/bot/
├── main.py                    # Entry point (webhook mode)
├── main_ai.py                 # Legacy (polling mode - not used)
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container build
│
├── handlers/                  # Message handlers
│   ├── conversation.py        # AI conversation logic
│   ├── conversation_interactive.py  # Conversation + UI
│   ├── image_search.py        # OCR + Vision API
│   ├── interactive.py         # Inline keyboards
│   ├── escalation.py          # Manager escalation
│   └── callbacks.py           # Button callbacks
│
├── core/                      # Core logic
│   ├── ai_assistant.py        # OpenAI integration
│   ├── api_client.py          # Backend API client
│   ├── config_manager.py      # Hot-reload config
│   ├── escalation_logger.py   # Log escalations
│   ├── analytics_tracker.py   # Track analytics
│   ├── memory.py              # Redis memory
│   ├── rate_limiter.py        # Rate limiting
│   └── i18n.py                # Multilanguage
│
├── integrations/              # Future integrations
│   ├── manager.py             # Plugin system
│   ├── onec.py                # 1C stub
│   └── bitrix24.py            # Bitrix24 stub
│
├── config/                    # Configuration
│   └── integrations.yaml      # Integration settings
│
└── services/                  # Legacy services
    ├── api_client.py          # Old API client
    └── prompt_manager.py      # Old prompt manager
```

### Key Components

**1. Webhook Handler (`main.py`)**
- Receives messages from Telegram
- Routes to appropriate handler
- Sends responses back

**2. AI Assistant (`core/ai_assistant.py`)**
- OpenAI GPT-4o-mini integration
- Function calling for product search
- Conversation context (last 5 messages)

**3. Image Search (`handlers/image_search.py`)**
- **OCR** (Tesseract): Extracts SKU from screenshots
- **Vision API** (gpt-4o-mini): Describes product photos
- Hybrid: Tries both, returns best match

**4. Interactive UI (`handlers/interactive.py`)**
- Inline keyboards for products
- Photo carousels (up to 10)
- Website links as buttons
- Pagination controls

**5. Hot-Reload Config (`core/config_manager.py`)**
- Polls backend API every 5 minutes
- Updates system prompt without restart
- Logs config changes

**6. Escalation Logger (`core/escalation_logger.py`)**
- Tracks manager escalations
- Sends full conversation history to admin
- Creates CRM deal stub

---

## 🔄 How It Works

### User Flow

```
User sends message
    ↓
Webhook receives
    ↓
Check rate limit ─→ [Exceeded] → "Too many requests"
    ↓ [OK]
Load conversation memory (Redis)
    ↓
Detect intent:
    ├─ Image? → Image Search Handler
    ├─ /start? → Welcome + Quick Actions
    ├─ Button callback? → Callback Handler
    └─ Text → AI Conversation Handler
         ↓
         OpenAI GPT-4o-mini
         ↓
         Function calls:
         ├─ search_products → Backend API
         ├─ get_product_details → Backend API
         └─ escalate_to_manager → Log escalation
              ↓
              Interactive UI
              ├─ Inline keyboards
              ├─ Photo sharing
              ├─ Website links
              └─ Pagination
                   ↓
                   Send response
                   ↓
                   Update memory (Redis)
```

### Message Types

**1. Text Messages**
- Processed by AI
- Function calling for actions
- Responds with product info

**2. Image Messages**
- OCR extracts SKU
- Vision API describes product
- Returns matching products

**3. Button Callbacks**
- Pagination (next/prev page)
- Product selection
- Category filter
- Quick actions

---

## 🧠 AI Prompts & Logic

### System Prompt

Located in: `core/ai_assistant.py`

```python
system_prompt = """
Ты - AI-ассистент мебельного магазина ZETA в {city}.

**Твоя задача:**
- Помогать клиентам найти мебель
- Отвечать на вопросы о товарах, ценах, доставке
- Использовать function calling для поиска продуктов

**Function calling:**
- search_products(query, category, price_min, price_max)
- get_product_details(product_id)
- escalate_to_manager(reason)

**Tone:**
- Дружелюбный, helpful
- Краткие ответы (2-3 предложения)
- Используй эмодзи 🛋️ 🪑 🛏️

**Examples:**
User: "хочу диван"
You: "🛋️ Отлично! У нас большой выбор диванов. Какой стиль вам интересен? Современный, классический или угловой?"

User: "сколько стоит?"
You: [call search_products] "Вот наши диваны в наличии: [показать 3-5 товаров с ценами]"
"""
```

### Function Definitions

**1. search_products**
```python
{
  "name": "search_products",
  "description": "Search furniture products by query, category, and price range",
  "parameters": {
    "query": {
      "type": "string",
      "description": "Search keywords (e.g., 'красный диван')"
    },
    "category": {
      "type": "string",
      "enum": ["Диваны", "Кресла", "Столы", "Кровати", "Шкафы"]
    },
    "price_min": {"type": "integer"},
    "price_max": {"type": "integer"}
  }
}
```

**2. get_product_details**
```python
{
  "name": "get_product_details",
  "description": "Get detailed information about a specific product",
  "parameters": {
    "product_id": {
      "type": "string",
      "description": "Product UUID"
    }
  }
}
```

**3. escalate_to_manager**
```python
{
  "name": "escalate_to_manager",
  "description": "Escalate to human manager when AI can't help",
  "parameters": {
    "reason": {
      "type": "string",
      "description": "Why escalating (e.g., 'custom order', 'complaint')"
    }
  }
}
```

---

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Telegram Bot
BOT_TOKEN=7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM

# Backend API
API_URL=https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Redis (conversation memory)
REDIS_URL=redis://localhost:6379

# Rate Limiting
RATE_LIMIT_PER_USER=10  # messages per minute
RATE_LIMIT_WINDOW=60    # seconds

# Webhook
WEBHOOK_PATH=/webhook
WEBHOOK_PORT=8443
```

### Integrations Config (`config/integrations.yaml`)

```yaml
integrations:
  enabled: true
  
  onec:
    enabled: false
    api_url: ""
    api_key: ""
    
  bitrix24:
    enabled: false
    webhook_url: ""
    
memory:
  enabled: true
  backend: redis
  ttl: 3600  # 1 hour
  
rate_limiting:
  enabled: true
  strategy: user_id
  
multilanguage:
  enabled: true
  default: ru
  supported: [ru, kz]
```

---

## 🚀 How to Improve

### 1. Enhance AI Responses

**File:** `core/ai_assistant.py`

**Current:**
- 5-message context
- Basic function calling

**Improvements:**
- Increase context to 10 messages
- Add user preferences tracking
- Implement follow-up questions
- Add sentiment analysis

**Code location:**
```python
# core/ai_assistant.py, line ~45
conversation_history = memory.get_last_n_messages(user_id, n=5)  # Change to 10
```

### 2. Better Product Recommendations

**File:** `handlers/conversation.py`

**Current:**
- Simple search by keywords
- No personalization

**Improvements:**
- Track user's viewed products
- Recommend similar items
- Implement collaborative filtering
- Add "customers also bought" feature

**Implementation:**
```python
# New function in handlers/conversation.py
async def get_recommendations(user_id: str, product_id: str):
    # Track viewed products
    memory.add_to_set(f"user:{user_id}:viewed", product_id)
    
    # Get similar products
    similar = await api_client.get_similar_products(product_id)
    
    # Get frequently bought together
    bundle = await api_client.get_bundle_products(product_id)
    
    return {"similar": similar, "bundle": bundle}
```

### 3. Improve Image Search

**File:** `handlers/image_search.py`

**Current:**
- OCR for screenshots
- Vision API for photos
- Basic matching

**Improvements:**
- Add image similarity search (embeddings)
- Support multiple images
- Detect furniture type from image
- Add reverse image search

**Code location:**
```python
# handlers/image_search.py, line ~120
async def image_similarity_search(image_url: str):
    # Use CLIP embeddings
    embedding = await openai.embeddings.create(
        model="clip-vit-large-patch14",
        input=image_url
    )
    
    # Search similar products by embedding
    results = await api_client.search_by_embedding(embedding)
    return results
```

### 4. Add Voice Messages Support

**New File:** `handlers/voice.py`

**Implementation:**
```python
from openai import OpenAI

async def handle_voice(message):
    # Download voice file
    voice_file = await bot.download_file(message.voice.file_id)
    
    # Transcribe with Whisper
    transcription = openai.audio.transcriptions.create(
        model="whisper-1",
        file=voice_file
    )
    
    # Process as text message
    return await handle_text_message(transcription.text)
```

### 5. Smart Follow-ups

**File:** `core/ai_assistant.py`

**Add context awareness:**
```python
# Track conversation stage
stages = {
    "greeting": ["привет", "здравствуйте"],
    "browsing": ["показать", "хочу посмотреть"],
    "comparing": ["чем отличается", "какой лучше"],
    "deciding": ["куплю", "заказать"],
}

# Adjust responses based on stage
if stage == "comparing":
    prompt += "\nПомоги сравнить товары по характеристикам."
elif stage == "deciding":
    prompt += "\nПредложи оформить заказ или связаться с менеджером."
```

---

## 🐛 Common Issues & Fixes

### Issue 1: Bot не отвечает

**Symptoms:** Messages sent, no response

**Debug:**
```bash
# Check webhook status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Check Container App logs
az containerapp logs show -n zeta-api -g zeta-platform-prod --follow

# Test backend API
curl https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io/health
```

**Fix:**
1. Webhook not set → Set webhook
2. Backend down → Restart Container App
3. OpenAI key invalid → Update env variable

### Issue 2: Image search не работает

**Symptoms:** Photos sent, no products returned

**Debug:**
```bash
# Check OCR installed
docker exec <container> tesseract --version

# Check OpenAI API key
docker exec <container> python -c "from openai import OpenAI; print(OpenAI().models.list())"
```

**Fix:**
1. Tesseract not installed → Add to Dockerfile
2. Vision API rate limit → Add retry logic
3. No matching products → Improve fuzzy matching

### Issue 3: Rate limit ложно срабатывает

**Symptoms:** "Too many requests" after 2-3 messages

**Debug:**
```python
# Check Redis
redis-cli GET rate_limit:<user_id>
```

**Fix:**
```python
# Increase limits in .env
RATE_LIMIT_PER_USER=20  # was 10
RATE_LIMIT_WINDOW=60
```

---

## 📊 Analytics

Bot tracks:
- Message count
- Search queries
- Product views
- Escalations
- Error rate

**View stats:**
```sql
SELECT 
  event_type,
  COUNT(*) as count,
  AVG(metadata->>'response_time') as avg_response_ms
FROM analytics_events
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY event_type;
```

---

## 🔗 Integration Points

### Backend API Endpoints Used

```
GET  /health                      - Health check
GET  /products/search             - Search products
GET  /products/{id}               - Product details
GET  /cities/{id}/bot-config      - Get bot config
POST /analytics/event             - Log analytics
POST /escalations                 - Create escalation
```

### Redis Keys

```
conversation:{user_id}            - Chat history (LIST)
rate_limit:{user_id}              - Request count (INT, TTL)
user:{user_id}:viewed             - Viewed products (SET)
bot:config:{city_id}              - Bot configuration (HASH)
```

---

## 📝 To-Do List

**High Priority:**
- [ ] Add voice message support
- [ ] Implement recommendations
- [ ] Add order tracking
- [ ] Improve error messages

**Medium Priority:**
- [ ] Add more categories
- [ ] Implement filters (color, size, material)
- [ ] Add favorites/wishlist
- [ ] Implement promo codes

**Low Priority:**
- [ ] Add gift suggestions
- [ ] Implement AR preview
- [ ] Add chat history export
- [ ] Implement referral system

---

**Last Updated:** 2026-02-20  
**Version:** 1.0 (Production)  
**Maintained by:** OpenClaw AI
