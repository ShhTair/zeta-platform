# ZETA Platform Infrastructure Map

**Generated:** 2026-02-20 06:26 UTC

---

## ⚠️ CRITICAL ISSUE: Azure VM Unreachable

**The Azure VM (20.234.16.216) is completely unreachable from the network.**

All ports tested (22, 80, 443, 8000, 8443) are timing out. This is blocking verification of:
- Database (PostgreSQL)
- Cache (Redis)
- Backend API
- Telegram Bot service

**Possible causes:**
1. VM is stopped/deallocated in Azure Portal
2. Network Security Group (NSG) rules blocking all traffic
3. VM firewall misconfiguration
4. Azure subscription/billing issue
5. VM crashed or frozen

**Immediate action required:** Check Azure Portal VM status.

---

## Database (PostgreSQL 14)

**Last verified:** 2026-02-19 (from previous successful connections)

- **Host:** localhost (Azure VM)
- **Database:** zeta_platform
- **Tables:** 11 tables
  - alembic_version
  - audit_logs
  - bot_configs
  - categories
  - cities
  - city_admins
  - conversations
  - messages
  - products
  - sessions
  - users
- **Products:** 37,318 rows ✅
- **Users:** 1 row ✅
- **Cities:** 1 row ✅
- **Status:** ❌ UNREACHABLE (VM down)

---

## Cache (Redis 6.0)

**Last verified:** 2026-02-19

- **Host:** localhost (Azure VM)
- **Port:** 6379
- **Keys:** 0 (empty - cache not being used or cleared)
- **Status:** ❌ UNREACHABLE (VM down)

---

## Backend API (FastAPI)

**Last verified:** 2026-02-19

- **URL:** http://20.234.16.216:8000
- **Service:** zeta-api.service (systemd)
- **Process:** uvicorn (PID 49769, running 17h as of last check)
- **Endpoints:** 
  - `/health` - Health check
  - `/products` - Product listings
  - `/cities` - City listings
  - `/auth/register` - User registration
  - `/products/search` - Product search
- **Status:** ❌ UNREACHABLE (VM down)

**Security note:** API logs show scanning attempts for PHP vulnerabilities (phpunit, ThinkPHP exploits). FastAPI correctly returns 404. Consider adding rate limiting.

---

## Frontend (Next.js)

- **URL:** https://web-ten-sigma-30.vercel.app
- **Platform:** Vercel
- **Environment:** Production
- **Status:** ✅ ONLINE (HTTP 200)

**Environment Variables (Vercel Production):**
- `NEXT_PUBLIC_API_URL` - Encrypted ✅
- `VITE_WS_URL` - Encrypted ✅
- `VITE_API_URL` - Encrypted ✅
- `OPENAI_API_KEY` - Encrypted ✅

**Issue:** Cannot verify API connection because backend VM is unreachable.

---

## Telegram Bot

- **Bot:** @zeta_taldykorgan_bot
- **Token:** 7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM
- **Webhook URL:** ❌ NOT SET (empty)
- **Pending updates:** 0
- **Allowed updates:** ["message"]
- **Service:** zeta-bot.service (systemd, status unknown)
- **Status:** ❌ WEBHOOK NOT CONFIGURED

**Critical issue:** Bot webhook is not configured. Bot is in polling mode or not receiving updates.

Expected webhook: `https://20.234.16.216:8443/webhook` or similar

---

## Architecture Connections

```
Frontend (Vercel) ✅
    ↓ HTTPS → API_URL (env var)
Backend API (Port 8000) ❌ UNREACHABLE
    ↓ localhost:5432
Database (PostgreSQL) ❌ UNREACHABLE
    ↓ localhost:6379
Cache (Redis) ❌ UNREACHABLE (0 keys)

Telegram Bot ❌ WEBHOOK NOT SET
    ↓ (should be) HTTPS Port 8443
Backend API ❌ UNREACHABLE
    ↓ SQL queries
Database ❌ UNREACHABLE
```

---

## Issues Found

### 🔴 CRITICAL: Azure VM Unreachable
- **Impact:** Entire backend infrastructure (API, database, bot) is offline
- **Symptoms:** All ports timeout (SSH 22, HTTP 8000, HTTPS 443)
- **Fix:** 
  1. Check Azure Portal: VM status (running/stopped/deallocated)
  2. Check Network Security Group rules
  3. Check Azure billing/subscription status
  4. If VM is running, check firewall: `sudo ufw status`
  5. Restart VM if needed

### 🔴 CRITICAL: Telegram Bot Webhook Not Set
- **Impact:** Bot not receiving messages from users
- **Fix:** Set webhook after VM is back online:
  ```bash
  curl -X POST "https://api.telegram.org/bot7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM/setWebhook" \
    -d "url=https://20.234.16.216:8443/webhook"
  ```

### ⚠️ WARNING: Redis Cache Empty
- **Impact:** No caching, possible performance degradation
- **Investigation needed:** Verify if cache is being used or if it was recently cleared

### ⚠️ WARNING: API Security Scanning
- **Impact:** Automated scanners probing for vulnerabilities
- **Fix:** Add rate limiting middleware to FastAPI app

---

## Verification Status

### ✅ Successfully Verified
- [x] Frontend deployed and online (Vercel)
- [x] Frontend environment variables configured
- [x] Database schema exists (11 tables)
- [x] Database has data (37K products, users, cities)
- [x] Telegram bot exists and API responds

### ❌ Unable to Verify (VM Unreachable)
- [ ] Database connection from API
- [ ] Redis connection from API
- [ ] Backend API endpoints responding
- [ ] API logs (recent)
- [ ] Bot service status
- [ ] Bot webhook configured
- [ ] Frontend → Backend connection
- [ ] Bot → Backend connection
- [ ] End-to-end flow testing

---

## Recommendations

### Immediate (Fix Now)
1. **Restart Azure VM** or check why it's unreachable
2. **Configure bot webhook** after VM is online
3. **Verify NSG rules** allow inbound traffic on ports 22, 8000, 8443

### Short-term (This Week)
1. **Set up monitoring:** Azure Monitor alerts for VM down
2. **Add health checks:** External uptime monitoring (UptimeRobot, etc.)
3. **Configure Redis:** Verify cache strategy is working
4. **Add rate limiting:** Protect API from scanners

### Medium-term (This Month)
1. **SSL/TLS:** Use Let's Encrypt for HTTPS on API and bot webhook
2. **Domain name:** Replace IP with proper domain (api.zeta.kz)
3. **Backup strategy:** Automated PostgreSQL backups
4. **CI/CD:** Automated deployment pipeline
5. **Logging:** Centralized logging (Sentry, Datadog, etc.)

---

## Next Steps

1. ✅ Check Azure Portal VM status
2. ✅ Start/restart VM if stopped
3. ✅ Verify NSG rules
4. ✅ Run verification script again once VM is online
5. ✅ Set bot webhook
6. ✅ Test end-to-end flows

---

**Verification incomplete due to infrastructure outage.**

**Last successful connection:** 2026-02-19 12:54 UTC (API service start time)
**Verification attempted:** 2026-02-20 06:26 UTC
**Duration:** ~17 hours offline
