# ✅ ZETA Admin Integration - Verification Checklist

Use this checklist to verify the integration is working correctly.

---

## 🗄️ Database Setup

- [ ] Migration files exist in `apps/api/alembic/versions/`
  - [ ] `001_initial_migration.py`
  - [ ] `002_add_escalations_analytics.py`

- [ ] Run migration: `cd apps/api && alembic upgrade head`
  
- [ ] Verify tables created:
  ```sql
  SELECT table_name FROM information_schema.tables 
  WHERE table_schema='public' 
  AND table_name IN ('escalations', 'analytics_events');
  ```
  
- [ ] Check table structure:
  ```sql
  \d escalations
  \d analytics_events
  ```

---

## 🔌 Backend API

### File Structure

- [ ] New models exist:
  - [ ] `apps/api/app/models/escalation.py`
  - [ ] `apps/api/app/models/analytics_event.py`

- [ ] Models registered in `apps/api/app/models/__init__.py`

- [ ] New routes exist:
  - [ ] `apps/api/app/routes/escalations.py`
  
- [ ] Analytics routes updated:
  - [ ] `apps/api/app/routes/analytics.py` includes event tracking

- [ ] Schemas created:
  - [ ] `apps/api/app/schemas/escalation.py`
  - [ ] `apps/api/app/schemas/analytics.py`

- [ ] Routes registered in `apps/api/app/main.py`

### API Endpoints

- [ ] Start API: `cd apps/api && uvicorn app.main:app --reload`

- [ ] API is running: `curl http://localhost:8000/`

- [ ] Public bot config endpoint works (no auth):
  ```bash
  curl http://localhost:8000/cities/1/bot-config
  ```

- [ ] Create test escalation:
  ```bash
  curl -X POST http://localhost:8000/escalations \
    -H "Content-Type: application/json" \
    -d '{
      "city_id": 1,
      "user_telegram_id": 123456789,
      "user_name": "Test User",
      "product_sku": "TEST-001",
      "reason": "test",
      "conversation": [{"role": "user", "text": "Test"}]
    }'
  ```

- [ ] Create test analytics event:
  ```bash
  curl -X POST http://localhost:8000/analytics/events \
    -H "Content-Type: application/json" \
    -d '{
      "city_id": 1,
      "event_type": "test_event",
      "data": {"test": true}
    }'
  ```

- [ ] Verify in database:
  ```sql
  SELECT * FROM escalations ORDER BY created_at DESC LIMIT 1;
  SELECT * FROM analytics_events ORDER BY created_at DESC LIMIT 1;
  ```

---

## 🤖 Bot Integration

### File Structure

- [ ] Core services exist:
  - [ ] `apps/bot/core/config_manager.py`
  - [ ] `apps/bot/core/escalation_logger.py`
  - [ ] `apps/bot/core/analytics_tracker.py`

- [ ] Example handlers exist:
  - [ ] `apps/bot/handlers/admin_integrated.py`

- [ ] Main file updated:
  - [ ] `apps/bot/main.py` imports new services
  - [ ] Services initialized in `create_app()`
  - [ ] Services attached to bot context
  - [ ] Auto-reload starts in `on_startup()`
  - [ ] Auto-reload stops in `on_shutdown()`

### Configuration

- [ ] Bot `.env` file exists with:
  - [ ] `BOT_TOKEN=...`
  - [ ] `CITY_ID=1` (integer)
  - [ ] `API_URL=http://localhost:8000`
  - [ ] `WEBHOOK_URL=https://...`

- [ ] Bot config exists in database:
  ```sql
  SELECT * FROM bot_configs WHERE city_id = 1;
  ```

- [ ] If not, create via API:
  ```bash
  # (requires JWT token - use admin panel or API)
  ```

### Bot Runtime

- [ ] Start bot: `cd apps/bot && python main.py`

- [ ] Bot logs show config loaded:
  ```
  ✅ Loaded legacy config for city: 1
  ✅ Config loaded + auto-reload started (every 300s)
  ```

- [ ] Auto-reload task started:
  ```
  🚀 Started auto-reload task (interval: 300s)
  ```

- [ ] Wait 5 minutes, check for reload log:
  ```
  🔄 Config auto-reloaded (every 300s)
  ```

---

## 🧪 Integration Testing

### Run Test Suite

- [ ] Run test script: `python test_admin_integration.py`

- [ ] All tests pass (6/6):
  - [ ] ✅ Bot Config (Public)
  - [ ] ✅ Create Escalation
  - [ ] ✅ Create Analytics Event
  - [ ] ✅ ConfigManager Class
  - [ ] ✅ EscalationLogger Class
  - [ ] ✅ AnalyticsTracker Class

### Manual Bot Testing

- [ ] Send `/config` to bot → Shows current configuration

- [ ] Send `/contact` to bot → Shows manager contact from config

- [ ] Send `/escalate test_reason` to bot → Creates escalation

- [ ] Check escalation in database:
  ```sql
  SELECT * FROM escalations ORDER BY created_at DESC LIMIT 1;
  ```

- [ ] Use bot normally → Check analytics events:
  ```sql
  SELECT event_type, COUNT(*) FROM analytics_events 
  GROUP BY event_type;
  ```

---

## 📊 Analytics Verification

- [ ] Query analytics endpoint:
  ```bash
  # (requires JWT token)
  curl http://localhost:8000/cities/1/analytics?days=7 \
    -H "Authorization: Bearer YOUR_JWT_TOKEN"
  ```

- [ ] Response includes:
  - [ ] `total_conversations`
  - [ ] `unique_users`
  - [ ] `total_messages`
  - [ ] `event_counts` (object)
  - [ ] `total_escalations`
  - [ ] `pending_escalations`

---

## 🔄 Hot-Reload Testing

- [ ] Update bot config via API (or admin panel):
  - Change `greeting_message` to something unique

- [ ] Wait 5 minutes (or restart bot)

- [ ] Send `/config` to bot

- [ ] Verify greeting message updated

- [ ] Bot DID NOT restart (check uptime in logs)

---

## 📱 Frontend Integration (Manual)

### Escalations API

- [ ] Can list escalations (with auth):
  ```bash
  curl http://localhost:8000/cities/1/escalations \
    -H "Authorization: Bearer YOUR_JWT_TOKEN"
  ```

- [ ] Can update escalation status:
  ```bash
  curl -X PUT http://localhost:8000/escalations/1 \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"status": "resolved"}'
  ```

- [ ] Escalation shows `resolved_at` timestamp after update

### Bot Config API

- [ ] Can get config (with auth):
  ```bash
  curl http://localhost:8000/cities/1/config \
    -H "Authorization: Bearer YOUR_JWT_TOKEN"
  ```

- [ ] Can update config:
  ```bash
  curl -X PUT http://localhost:8000/cities/1/config \
    -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "greeting_message": "Updated greeting!",
      "manager_contact": "+7 999 999-99-99"
    }'
  ```

- [ ] Update logged in `audit_logs` table:
  ```sql
  SELECT * FROM audit_logs 
  WHERE table_name = 'bot_configs' 
  ORDER BY created_at DESC LIMIT 1;
  ```

---

## 🎨 Frontend Pages (TODO)

- [ ] Escalations page exists: `apps/web/app/(dashboard)/cities/[id]/escalations/page.tsx`

- [ ] Bot config page exists: `apps/web/app/(dashboard)/cities/[id]/bot-config/page.tsx`

- [ ] Analytics integrated in dashboard: `apps/web/app/(dashboard)/cities/[id]/page.tsx`

- [ ] Pages use provided templates from `ADMIN_INTEGRATION_GUIDE.md`

---

## 🚀 Production Readiness

### Security

- [ ] Public endpoints (`/bot-config`, `/escalations`, `/analytics/events`) work without auth

- [ ] Admin endpoints require JWT token

- [ ] CORS configured for frontend domain

- [ ] API uses HTTPS in production

- [ ] Bot webhook uses HTTPS

### Performance

- [ ] Auto-reload interval set appropriately (300s = 5 min)

- [ ] Database has indexes on:
  - [ ] `escalations.user_telegram_id`
  - [ ] `escalations.created_at`
  - [ ] `analytics_events.event_type`
  - [ ] `analytics_events.created_at`

- [ ] Analytics queries use date filters

### Monitoring

- [ ] Bot logs auto-reload every 5 minutes

- [ ] API logs escalation creations

- [ ] API logs analytics events

- [ ] Error logs captured and monitored

---

## 📋 Final Checks

- [ ] All files committed to git

- [ ] Documentation complete:
  - [ ] `ADMIN_INTEGRATION_README.md`
  - [ ] `ADMIN_INTEGRATION_GUIDE.md`
  - [ ] `INTEGRATION_COMPLETE.md`
  - [ ] `INTEGRATION_SUMMARY.md`
  - [ ] `VERIFICATION_CHECKLIST.md` (this file)

- [ ] Test script provided: `test_admin_integration.py`

- [ ] Example handlers provided: `apps/bot/handlers/admin_integrated.py`

- [ ] Frontend templates provided in documentation

- [ ] Migration tested on clean database

- [ ] Bot tested end-to-end

- [ ] API tested with curl/Postman

---

## ✅ Sign-Off

**Backend Developer:**
- [ ] All models and routes implemented
- [ ] Tests passing
- [ ] Documentation complete

**Bot Developer:**
- [ ] Services integrated
- [ ] Auto-reload working
- [ ] Example handlers provided

**Frontend Developer:**
- [ ] API contracts understood
- [ ] Templates received
- [ ] Ready to build pages

**QA:**
- [ ] Integration tests pass
- [ ] Manual testing complete
- [ ] No critical issues

**Product Owner:**
- [ ] All features implemented
- [ ] Success criteria met
- [ ] Approved for deployment

---

## 🎉 Integration Status

**Once all boxes are checked, the integration is complete and ready for production!**

---

**Last Updated:** 2026-02-19  
**Version:** 1.0  
**Status:** 🟢 Ready
