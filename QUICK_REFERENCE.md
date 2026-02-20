# 🚀 ZETA Bot - Admin Integration Quick Reference

**One-page cheat sheet for developers**

---

## 📦 Installation

```bash
# 1. Apply database migration
cd apps/api
alembic upgrade head

# 2. Start API
uvicorn app.main:app --reload

# 3. Start Bot
cd ../bot
python main.py

# 4. Run tests
cd ../..
python test_admin_integration.py
```

---

## 🔧 Bot Configuration

**Environment (.env):**
```bash
BOT_TOKEN=123456789:ABC...
CITY_ID=1
API_URL=http://localhost:8000
WEBHOOK_URL=https://bot.yourdomain.com
```

**Services in Bot Context:**
```python
config_manager = message.bot.get("config_manager")
escalation_logger = message.bot.get("escalation_logger")
analytics_tracker = message.bot.get("analytics_tracker")
city_id = message.bot.get("city_id")
```

---

## 🌐 API Endpoints

### Public (No Auth)
```
GET  /cities/{id}/bot-config     Bot loads config
POST /escalations                 Bot logs escalation
POST /analytics/events            Bot tracks event
```

### Authenticated (JWT)
```
PUT  /cities/{id}/config          Update config
GET  /cities/{id}/escalations     List escalations
PUT  /escalations/{id}            Update escalation
GET  /cities/{id}/analytics       Get stats
```

---

## 💻 Code Examples

### Get Config
```python
config_manager = message.bot.get("config_manager")
greeting = config_manager.greeting_message
contact = config_manager.manager_contact
prompt = config_manager.system_prompt
action = config_manager.escalation_action  # notify/transfer/log_only
```

### Log Escalation
```python
escalation_logger = message.bot.get("escalation_logger")
city_id = message.bot.get("city_id")

await escalation_logger.log_escalation(
    city_id=city_id,
    user_id=message.from_user.id,
    user_name=message.from_user.full_name,
    product_sku="SKU-123",
    reason="price_question",
    conversation_history=[
        {"role": "user", "text": message.text}
    ]
)
```

### Track Analytics
```python
analytics_tracker = message.bot.get("analytics_tracker")
city_id = message.bot.get("city_id")

# Search
await analytics_tracker.track_search(city_id, query, results_count)

# Product view
await analytics_tracker.track_product_view(city_id, product_sku)

# Escalation
await analytics_tracker.track_escalation(city_id, reason)

# Custom event
await analytics_tracker.track_event(city_id, "custom_event", {"key": "value"})
```

---

## 📊 Database Queries

### View Escalations
```sql
SELECT * FROM escalations 
WHERE city_id = 1 
ORDER BY created_at DESC 
LIMIT 10;
```

### View Analytics
```sql
SELECT event_type, COUNT(*) 
FROM analytics_events 
WHERE city_id = 1 
GROUP BY event_type;
```

### View Bot Config
```sql
SELECT * FROM bot_configs WHERE city_id = 1;
```

---

## 🧪 Testing

**Run all tests:**
```bash
python test_admin_integration.py
```

**Manual tests:**
```bash
# Test config endpoint
curl http://localhost:8000/cities/1/bot-config

# Test escalation creation
curl -X POST http://localhost:8000/escalations \
  -H "Content-Type: application/json" \
  -d '{"city_id":1,"user_telegram_id":123,"user_name":"Test","reason":"test"}'

# Test analytics event
curl -X POST http://localhost:8000/analytics/events \
  -H "Content-Type: application/json" \
  -d '{"city_id":1,"event_type":"test","data":{}}'
```

---

## 🔍 Monitoring

**Bot logs to watch:**
```
✅ Config loaded + auto-reload started (every 300s)
🔄 Config auto-reloaded (every 300s)
✅ Escalation logged: #<id> - User <user_id>, Reason: <reason>
📊 Event tracked: <event_type>
```

**API logs to watch:**
```
POST /escalations → 201 Created
POST /analytics/events → 201 Created
GET /cities/1/bot-config → 200 OK
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Config not loading | Check API is running + CITY_ID is correct |
| Auto-reload not working | Check logs for "🔄 Config auto-reloaded" |
| Escalations not appearing | Check database: `SELECT * FROM escalations;` |
| Analytics missing | Check `analytics_events` table |

---

## 📁 Key Files

```
Backend:
  apps/api/app/models/escalation.py
  apps/api/app/models/analytics_event.py
  apps/api/app/routes/escalations.py
  apps/api/app/routes/analytics.py
  apps/api/alembic/versions/002_add_escalations_analytics.py

Bot:
  apps/bot/core/config_manager.py
  apps/bot/core/escalation_logger.py
  apps/bot/core/analytics_tracker.py
  apps/bot/handlers/admin_integrated.py
  apps/bot/main.py

Tests:
  test_admin_integration.py

Docs:
  ADMIN_INTEGRATION_README.md
  ADMIN_INTEGRATION_GUIDE.md
  VERIFICATION_CHECKLIST.md
  ARCHITECTURE_DIAGRAM.md
```

---

## 🎯 Common Tasks

### Update Bot Greeting
1. Edit config in admin panel (or via API)
2. Wait 5 minutes (or restart bot)
3. Greeting automatically updates

### View Recent Escalations
```sql
SELECT user_name, reason, created_at 
FROM escalations 
WHERE city_id = 1 
  AND created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

### Get Analytics Stats
```bash
curl http://localhost:8000/cities/1/analytics?days=7 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🚢 Deployment

**Production checklist:**
- [ ] Run migration on prod DB
- [ ] Set production env vars
- [ ] Enable HTTPS for API + bot
- [ ] Configure CORS for frontend
- [ ] Monitor logs for errors
- [ ] Set up alerts for escalations

---

## 📚 Full Documentation

- `ADMIN_INTEGRATION_README.md` - Quick start
- `ADMIN_INTEGRATION_GUIDE.md` - Full details
- `ARCHITECTURE_DIAGRAM.md` - Visual architecture
- `VERIFICATION_CHECKLIST.md` - Testing guide

---

## 🆘 Need Help?

1. Check documentation above
2. Review code examples in `apps/bot/handlers/admin_integrated.py`
3. Run `test_admin_integration.py` to verify setup
4. Check logs for errors

---

**Version:** 1.0 | **Last Updated:** 2026-02-19
