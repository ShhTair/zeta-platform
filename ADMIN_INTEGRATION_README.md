# 🤖 ZETA Bot - Admin Platform Integration

## Overview

The ZETA Telegram bot is now fully integrated with the admin platform, enabling:
- **Dynamic configuration** - Edit prompts, contacts, and settings without restarting the bot
- **Escalation management** - Track and manage customer escalations from admin panel
- **Analytics tracking** - Monitor bot usage, searches, and user behavior
- **Hot-reload** - Configuration updates apply automatically every 5 minutes

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Admin Web Panel                         │
│                   (Next.js + React)                          │
│                                                              │
│  • Edit bot prompts & settings                              │
│  • View escalations & mark resolved                         │
│  • View analytics dashboard                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │ REST API (HTTPS)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│                                                              │
│  Endpoints:                                                  │
│  • GET  /cities/{id}/bot-config  (public for bot)          │
│  • PUT  /cities/{id}/config      (authenticated)            │
│  • POST /escalations             (public for bot)           │
│  • GET  /cities/{id}/escalations (authenticated)            │
│  • POST /analytics/events        (public for bot)           │
│  • GET  /cities/{id}/analytics   (authenticated)            │
└──────────────────┬──────────────────────────────────────────┘
                   │ REST API (HTTP/HTTPS)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Bot                              │
│                    (aiogram)                                 │
│                                                              │
│  Services:                                                   │
│  • ConfigManager       - Load & hot-reload config (5 min)   │
│  • EscalationLogger    - Log escalations to admin           │
│  • AnalyticsTracker    - Track events for dashboard         │
└──────────────────┬──────────────────────────────────────────┘
                   │ Telegram Bot API
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                         Users                                │
│                   (Telegram Clients)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 What's Included

### Backend Components

**New Database Models:**
- `Escalation` - Customer escalations with conversation history
- `AnalyticsEvent` - Bot usage events

**New API Routes:**
- `/cities/{id}/bot-config` - Bot configuration (public)
- `/escalations` - Escalation CRUD
- `/analytics/events` - Event tracking
- `/cities/{id}/analytics` - Analytics stats

**Database Migration:**
- `002_add_escalations_analytics.py`

### Bot Components

**Core Services:**
- `ConfigManager` - Dynamic config with auto-reload
- `EscalationLogger` - Log escalations to API
- `AnalyticsTracker` - Track events to API

**Example Handlers:**
- `/contact` - Show manager contact
- `/escalate` - Create escalation
- `/config` - Show current config (debug)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL database
- Telegram bot token
- Domain with HTTPS (for webhook)

### 1. Database Migration

```bash
cd apps/api
alembic upgrade head
```

This creates the `escalations` and `analytics_events` tables.

### 2. Configure Bot

Edit `apps/bot/.env`:

```bash
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
CITY_ID=1
API_URL=http://localhost:8000
WEBHOOK_URL=https://your-domain.com
PORT=8080
```

### 3. Start Services

**Terminal 1: API**
```bash
cd apps/api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Bot**
```bash
cd apps/bot
python main.py
```

**Terminal 3: Frontend (optional)**
```bash
cd apps/web
npm run dev
```

### 4. Create Initial Config

Use the admin panel or API to create bot config for your city:

```bash
curl -X PUT http://localhost:8000/cities/1/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "system_prompt": "You are a helpful shopping assistant.",
    "greeting_message": "Добро пожаловать! Чем могу помочь?",
    "manager_contact": "+7 XXX XXX-XX-XX",
    "escalation_action": "notify"
  }'
```

---

## 🧪 Testing

Run the integration test suite:

```bash
python test_admin_integration.py
```

This tests:
- Bot config loading (public endpoint)
- Escalation creation
- Analytics event tracking
- ConfigManager class
- EscalationLogger class
- AnalyticsTracker class

Expected output:
```
✅ PASS - Bot Config (Public)
✅ PASS - Create Escalation
✅ PASS - Create Analytics Event
✅ PASS - ConfigManager Class
✅ PASS - EscalationLogger Class
✅ PASS - AnalyticsTracker Class

Results: 6/6 tests passed
```

---

## 💻 Usage Examples

### Dynamic Configuration

**In your bot handlers:**

```python
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    config_manager = message.bot.get("config_manager")
    
    # Get greeting from admin config
    greeting = config_manager.greeting_message
    
    await message.answer(greeting)
```

**Config auto-reloads every 5 minutes!** No bot restart needed.

### Escalation Logging

**When a user needs human help:**

```python
@router.message(F.text.contains("помощь менеджера"))
async def escalate_handler(message: types.Message):
    escalation_logger = message.bot.get("escalation_logger")
    config_manager = message.bot.get("config_manager")
    city_id = message.bot.get("city_id")
    
    # Log escalation to admin platform
    await escalation_logger.log_escalation(
        city_id=city_id,
        user_id=message.from_user.id,
        user_name=message.from_user.full_name,
        product_sku=None,  # Or specific product SKU
        reason="manager_requested",
        conversation_history=[
            {"role": "user", "text": message.text}
        ]
    )
    
    # Send manager contact
    manager_contact = config_manager.manager_contact
    await message.answer(
        f"💬 Свяжитесь с менеджером:\n"
        f"📞 {manager_contact}"
    )
```

### Analytics Tracking

**Track user actions:**

```python
@router.message(F.text)
async def search_handler(message: types.Message):
    analytics_tracker = message.bot.get("analytics_tracker")
    city_id = message.bot.get("city_id")
    
    query = message.text
    
    # Your search logic
    results = await search_products(query)
    
    # Track the search
    await analytics_tracker.track_search(
        city_id=city_id,
        query=query,
        results_count=len(results)
    )
    
    # Show results...
```

**Common event types:**
- `search` - Product searches
- `product_view` - Product detail views
- `escalation` - User escalations
- `conversation_start` - New conversations
- Custom events - Add your own!

---

## 🎨 Admin Panel Integration

### 1. Bot Config Editor

**Location:** `apps/web/app/(dashboard)/cities/[id]/bot-config/page.tsx`

Features:
- Edit system prompt (AI instructions)
- Edit greeting message
- Edit manager contact
- Set escalation action (notify/transfer/log_only)
- Live preview
- Save button

**API Calls:**
- `GET /cities/{id}/config` - Load config
- `PUT /cities/{id}/config` - Save config

### 2. Escalations Dashboard

**Location:** `apps/web/app/(dashboard)/cities/[id]/escalations/page.tsx`

Features:
- Table of all escalations
- Filter by status (pending/contacted/resolved)
- View conversation history
- Assign to team member
- Mark as resolved
- Add notes

**API Calls:**
- `GET /cities/{id}/escalations?status=pending` - List
- `PUT /escalations/{id}` - Update
- `DELETE /escalations/{id}` - Delete

### 3. Analytics Dashboard

**Location:** `apps/web/app/(dashboard)/cities/[id]/analytics/page.tsx`

Metrics:
- Total conversations (last N days)
- Unique users
- Total messages
- Average messages per conversation
- Event counts by type (searches, views)
- Total escalations
- Pending escalations

**API Calls:**
- `GET /cities/{id}/analytics?days=7` - Get stats

---

## 🔧 Configuration Reference

### Environment Variables (Bot)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | ✅ Yes | - | Telegram bot token |
| `CITY_ID` | ✅ Yes | - | City ID (integer) |
| `API_URL` | ✅ Yes | - | Admin API URL |
| `WEBHOOK_URL` | ✅ Yes | - | Public webhook URL |
| `PORT` | No | 8080 | Bot webhook port |
| `HOST` | No | 0.0.0.0 | Bot webhook host |

### Bot Config Fields (Admin)

| Field | Type | Description |
|-------|------|-------------|
| `system_prompt` | Text | AI system prompt |
| `greeting_message` | Text | Welcome message |
| `manager_contact` | String | Phone/Telegram handle |
| `escalation_action` | Enum | notify/transfer/log_only |

**Escalation Actions:**
- `notify` - Show manager contact + log
- `transfer` - Indicate transfer + log
- `log_only` - Silent logging

---

## 📊 Database Schema

### `escalations` Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| city_id | Integer | City FK |
| user_telegram_id | BigInteger | User's Telegram ID |
| user_name | String | User's display name |
| product_sku | String | Product SKU (optional) |
| reason | String | Escalation reason |
| conversation | JSON | Message history |
| status | String | pending/contacted/resolved |
| assigned_to | Integer | User FK (optional) |
| notes | Text | Admin notes |
| created_at | Timestamp | Creation time |
| resolved_at | Timestamp | Resolution time |

### `analytics_events` Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| city_id | Integer | City FK |
| event_type | String | Event type |
| data | JSON | Event-specific data |
| created_at | Timestamp | Event time |

---

## 🔍 Monitoring

### Bot Logs

**Successful config load:**
```
✅ Config loaded for city 1
🚀 Started auto-reload task (interval: 300s)
```

**Auto-reload working:**
```
🔄 Config auto-reloaded (every 300s)
```

**Escalation logged:**
```
✅ Escalation logged: #42 - User 123456789, Reason: price_question
```

**Analytics tracked:**
```
📊 Event tracked: search
📊 Event tracked: product_view
```

### API Logs

```
INFO: POST /escalations - 201 Created
INFO: POST /analytics/events - 201 Created
INFO: GET /cities/1/bot-config - 200 OK
```

---

## 🐛 Troubleshooting

### Config not loading

**Symptom:** Bot starts but config is empty

**Fix:**
1. Check API is running: `curl http://localhost:8000/`
2. Check config exists: `curl http://localhost:8000/cities/1/bot-config`
3. Verify `CITY_ID` and `API_URL` in bot `.env`

### Auto-reload not working

**Symptom:** No "🔄 Config auto-reloaded" logs

**Fix:**
1. Check `config_manager.start_auto_reload()` is called in `on_startup()`
2. Verify bot didn't crash (check logs)
3. Try manual reload: restart bot

### Escalations not appearing

**Symptom:** Bot logs escalation but admin doesn't show it

**Fix:**
1. Check database: `SELECT * FROM escalations;`
2. Verify API endpoint: `curl http://localhost:8000/escalations`
3. Check city_id matches

### Analytics events missing

**Symptom:** Events tracked but not in analytics

**Fix:**
1. Check database: `SELECT * FROM analytics_events;`
2. Verify time range in analytics query
3. Analytics tracking is non-blocking - failures won't crash bot

---

## 📚 Documentation

- **Integration Guide:** `ADMIN_INTEGRATION_GUIDE.md` - Full implementation details
- **Completion Report:** `INTEGRATION_COMPLETE.md` - What was built
- **API Documentation:** Visit `/docs` on running API (Swagger UI)

---

## 🎯 Success Checklist

- [ ] Database migration applied
- [ ] Bot config created in admin
- [ ] Bot starts and loads config
- [ ] Auto-reload logs appear every 5 min
- [ ] Escalations logged to database
- [ ] Analytics events tracked
- [ ] Admin can view escalations
- [ ] Admin can edit config
- [ ] Config changes apply to bot (within 5 min)

---

## 🚢 Deployment

### Production Recommendations

1. **Use HTTPS** for API and webhook
2. **Set reload interval** to 300s (5 min) or longer
3. **Enable auth** on admin endpoints (already implemented)
4. **Monitor logs** for errors
5. **Set up alerts** for escalations
6. **Regular backups** of escalations/analytics

### Environment Variables (Production)

```bash
# Bot
BOT_TOKEN=your_real_token
CITY_ID=1
API_URL=https://api.yourdomain.com
WEBHOOK_URL=https://bot.yourdomain.com

# API
DATABASE_URL=postgresql://user:pass@host:5432/zeta
JWT_SECRET=your_secret_key
CORS_ORIGINS=https://admin.yourdomain.com
```

---

## 📞 Support

**Questions?** Check the documentation:
- `ADMIN_INTEGRATION_GUIDE.md` - Implementation details
- `test_admin_integration.py` - Example usage
- `apps/bot/handlers/admin_integrated.py` - Example handlers

**Issues?** Common problems:
1. API not running → Start with `uvicorn app.main:app`
2. Config not found → Create in admin panel
3. Auth errors → Use JWT token for authenticated endpoints

---

## 🎉 That's It!

Your ZETA bot now has full admin integration:
- ✅ Dynamic prompts
- ✅ Escalation management
- ✅ Analytics tracking
- ✅ Zero-downtime updates

Happy building! 🚀
