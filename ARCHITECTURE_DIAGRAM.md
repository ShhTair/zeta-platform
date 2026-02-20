# 🏗️ ZETA Bot - Admin Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ADMIN WEB PANEL                             │
│                      (Next.js + React + TailwindCSS)                 │
│                                                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │  Bot Config     │  │  Escalations    │  │   Analytics     │   │
│  │  Editor         │  │  Dashboard      │  │   Dashboard     │   │
│  │                 │  │                 │  │                 │   │
│  │ • Edit prompts  │  │ • View list     │  │ • Conversations │   │
│  │ • Set contact   │  │ • Mark resolved │  │ • Unique users  │   │
│  │ • Save config   │  │ • Add notes     │  │ • Escalations   │   │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘   │
│           │                    │                     │              │
└───────────┼────────────────────┼─────────────────────┼──────────────┘
            │                    │                     │
            │ HTTP REST (HTTPS)  │                     │
            │ JWT Auth           │                     │
            ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                              │
│                     (Python 3.9+ + SQLAlchemy)                       │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                       AUTHENTICATED ROUTES                     │ │
│  │                                                                │ │
│  │  PUT  /cities/{id}/config           ← Update bot config       │ │
│  │  GET  /cities/{id}/config           ← Get bot config          │ │
│  │  GET  /cities/{id}/escalations      ← List escalations        │ │
│  │  PUT  /escalations/{id}             ← Update escalation       │ │
│  │  GET  /cities/{id}/analytics        ← Get analytics stats     │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                         PUBLIC ROUTES                          │ │
│  │                     (No Auth - Bot Access)                     │ │
│  │                                                                │ │
│  │  GET  /cities/{id}/bot-config       ← Bot loads config        │ │
│  │  POST /escalations                  ← Bot logs escalation     │ │
│  │  POST /analytics/events             ← Bot tracks events       │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                      DATABASE MODELS                           │ │
│  │                                                                │ │
│  │  • bot_configs         → System prompts, greetings, contacts  │ │
│  │  • escalations         → Customer escalations with history    │ │
│  │  • analytics_events    → Bot usage events (search, view, etc) │ │
│  │  • conversations       → User conversations                   │ │
│  │  • audit_logs          → Change tracking                      │ │
│  └───────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬────────────────────────────────────────┘
                               │
                               │ PostgreSQL
                               ▼
                    ┌─────────────────────┐
                    │   DATABASE          │
                    │   (PostgreSQL)      │
                    │                     │
                    │ • bot_configs       │
                    │ • escalations       │
                    │ • analytics_events  │
                    └─────────────────────┘
                               ▲
                               │
┌──────────────────────────────┴────────────────────────────────────────┐
│                         TELEGRAM BOT                                   │
│                      (aiogram 3.x + aiohttp)                           │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                       CORE SERVICES                               │ │
│  │                                                                   │ │
│  │  ConfigManager:                                                   │ │
│  │    • load_config()          ← Load from API on startup           │ │
│  │    • auto_reload()          ← Background task (every 5 min)      │ │
│  │    • Properties: system_prompt, greeting_message, manager_contact│ │
│  │                                                                   │ │
│  │  EscalationLogger:                                                │ │
│  │    • log_escalation()       ← POST to /escalations               │ │
│  │    • Non-blocking           ← Won't crash bot on failure         │ │
│  │                                                                   │ │
│  │  AnalyticsTracker:                                                │ │
│  │    • track_search()         ← Track product searches             │ │
│  │    • track_product_view()   ← Track product views                │ │
│  │    • track_escalation()     ← Track escalations                  │ │
│  │    • track_event()          ← Generic event tracking             │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                       MESSAGE HANDLERS                            │ │
│  │                                                                   │ │
│  │  /start        → Send greeting from config                       │ │
│  │  /contact      → Send manager contact from config                │ │
│  │  /escalate     → Log escalation + send contact                   │ │
│  │  <search>      → Track search analytics                          │ │
│  │  <product>     → Track product view analytics                    │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               │ Telegram Bot API
                               │ (Webhook or Polling)
                               ▼
                    ┌─────────────────────┐
                    │   TELEGRAM USERS    │
                    │   (End Customers)   │
                    │                     │
                    │ • Ask questions     │
                    │ • Search products   │
                    │ • Request help      │
                    └─────────────────────┘
```

---

## Data Flow: Config Update

```
1. Admin edits config in web panel
   │
   ▼
2. Frontend sends PUT /cities/{id}/config with JWT token
   │
   ▼
3. Backend validates & saves to database
   │
   ▼
4. Backend logs change to audit_logs
   │
   ▼
5. Bot auto-reload task runs (every 5 min)
   │
   ▼
6. Bot calls GET /cities/{id}/bot-config
   │
   ▼
7. Bot updates in-memory config
   │
   ▼
8. Bot uses new config for next messages
```

**Time to apply:** ~5 minutes (no restart needed!)

---

## Data Flow: Escalation

```
1. User sends complex question to bot
   │
   ▼
2. Bot handler detects escalation needed
   │
   ▼
3. Bot calls escalation_logger.log_escalation()
   │
   ▼
4. EscalationLogger sends POST /escalations
   │
   ▼
5. Backend saves to escalations table
   │
   ▼
6. Admin sees escalation in dashboard
   │
   ▼
7. Admin clicks "Mark Resolved"
   │
   ▼
8. Frontend sends PUT /escalations/{id}
   │
   ▼
9. Backend updates status & sets resolved_at
```

**Real-time visibility!**

---

## Data Flow: Analytics

```
1. User searches "керамогранит"
   │
   ▼
2. Bot searches products
   │
   ▼
3. Bot calls analytics_tracker.track_search()
   │
   ▼
4. AnalyticsTracker sends POST /analytics/events
   │
   ▼
5. Backend saves to analytics_events table
   │
   ▼
6. Admin views analytics dashboard
   │
   ▼
7. Frontend calls GET /cities/{id}/analytics?days=7
   │
   ▼
8. Backend aggregates events & returns stats
```

**Track everything!**

---

## Component Interaction Map

```
┌─────────────┐
│ ConfigMgr   │──────► GET /cities/{id}/bot-config
└─────────────┘         (every 5 min)
      │
      ▼
  [In-Memory Config]
      │
      ▼
┌─────────────┐
│ Bot Handler │──────► Uses config
└─────────────┘         (greeting, contact, etc)


┌─────────────┐
│ Bot Handler │──────► Detects escalation needed
└─────────────┘
      │
      ▼
┌─────────────┐
│ EscalLogger │──────► POST /escalations
└─────────────┘         (user_id, reason, conversation)


┌─────────────┐
│ Bot Handler │──────► User action (search, view)
└─────────────┘
      │
      ▼
┌─────────────┐
│ Analytics   │──────► POST /analytics/events
│ Tracker     │         (event_type, data)
└─────────────┘
```

---

## Database Schema

```
bot_configs
├── id (PK)
├── city_id (FK → cities.id)
├── system_prompt (TEXT)
├── greeting_message (TEXT)
├── manager_contact (STRING)
├── escalation_action (ENUM: notify/transfer/log_only)
└── updated_at (TIMESTAMP)

escalations
├── id (PK)
├── city_id (FK → cities.id)
├── user_telegram_id (BIGINT) [INDEXED]
├── user_name (STRING)
├── product_sku (STRING)
├── reason (STRING)
├── conversation (JSON)
├── status (STRING: pending/contacted/resolved)
├── assigned_to (FK → users.id)
├── notes (TEXT)
├── created_at (TIMESTAMP) [INDEXED]
└── resolved_at (TIMESTAMP)

analytics_events
├── id (PK)
├── city_id (FK → cities.id)
├── event_type (STRING) [INDEXED]
├── data (JSON)
└── created_at (TIMESTAMP) [INDEXED]
```

---

## API Authentication

```
Public Endpoints (No Auth):
• GET  /cities/{id}/bot-config
• POST /escalations
• POST /analytics/events

Why? Bot needs to access these without managing JWT tokens.

Authenticated Endpoints (JWT Required):
• PUT  /cities/{id}/config
• GET  /cities/{id}/config
• GET  /cities/{id}/escalations
• PUT  /escalations/{id}
• DELETE /escalations/{id}
• GET  /cities/{id}/analytics

Why? Admin users need authentication & authorization.
```

---

## Auto-Reload Mechanism

```
Bot Startup:
├── Load config from API
├── Start auto-reload background task
└── Set webhook / start polling

Auto-Reload Task (asyncio):
├── Sleep for N seconds (default: 300 = 5 min)
├── Wake up
├── Call GET /cities/{id}/bot-config
├── Update in-memory config
├── Log "Config reloaded"
└── Repeat

Bot Shutdown:
├── Cancel auto-reload task
├── Delete webhook
└── Close sessions
```

**Result:** Config updates apply automatically without restart!

---

## Scalability Considerations

**Single Bot Instance:**
- Auto-reload every 5 minutes
- ~1 API call per 5 minutes
- Minimal overhead

**Multiple Bot Instances (same city):**
- Each instance reloads independently
- ~N API calls per 5 minutes (N = instances)
- Consider caching layer if N > 10

**Multiple Cities:**
- Each bot has own CITY_ID
- Each bot loads own config
- Fully isolated

**High Traffic:**
- Analytics tracking is non-blocking
- Failed tracking won't crash bot
- Consider queuing system for analytics if needed

---

## Error Handling

**Config Load Failure:**
- Bot startup fails (intentional)
- Forces fix before bot runs

**Config Reload Failure:**
- Logged as error
- Bot continues with last known config
- Retries on next interval

**Escalation Log Failure:**
- Logged as error
- User still gets response
- Try manual escalation later

**Analytics Track Failure:**
- Logged as warning (not error)
- Fully non-blocking
- Missing data acceptable

---

## Monitoring Points

**Health Checks:**
- API: `GET /health`
- Bot: Auto-reload logs

**Key Metrics:**
- Config reload success rate
- Escalation creation rate
- Analytics event rate
- API response times

**Alerts:**
- Config reload failed 3 times in a row
- Escalation API down
- Analytics API down (warning, not critical)

---

## Deployment Architecture

```
┌──────────────────────────────────────────┐
│         PRODUCTION DEPLOYMENT             │
├──────────────────────────────────────────┤
│                                           │
│  Frontend (Next.js)                       │
│  ↓ Deployed to Vercel/Netlify            │
│  ↓ Domain: admin.yourdomain.com          │
│                                           │
│  Backend (FastAPI)                        │
│  ↓ Deployed to VPS/Cloud                 │
│  ↓ Domain: api.yourdomain.com            │
│  ↓ HTTPS via Let's Encrypt              │
│                                           │
│  Bot (aiogram)                            │
│  ↓ Deployed to same VPS or separate      │
│  ↓ Webhook: bot.yourdomain.com           │
│  ↓ HTTPS via Let's Encrypt              │
│                                           │
│  Database (PostgreSQL)                    │
│  ↓ Managed service (AWS RDS, etc)        │
│  ↓ Or self-hosted on VPS                 │
│                                           │
└──────────────────────────────────────────┘
```

---

## Summary

**Key Features:**
- ✅ Zero-downtime config updates (5 min auto-reload)
- ✅ Real-time escalation tracking
- ✅ Comprehensive analytics
- ✅ Secure API with JWT auth
- ✅ Public endpoints for bot
- ✅ Non-blocking event tracking

**Architecture Highlights:**
- Clean separation of concerns
- RESTful API design
- Async/await throughout
- Background tasks for hot-reload
- Scalable and maintainable

**Ready for production!** 🚀
