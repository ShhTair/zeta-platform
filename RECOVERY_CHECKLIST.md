# 🚨 ZETA Platform Recovery Checklist

**Status:** Azure VM (20.234.16.216) is **UNREACHABLE**

---

## Step 1: Restore VM Connectivity (CRITICAL)

### A. Check Azure Portal

- [ ] Go to https://portal.azure.com
- [ ] Navigate to: **Virtual Machines**
- [ ] Find: **zeta-vm** (or search for 20.234.16.216)
- [ ] Check status indicator:
  - 🔴 **Stopped** → Click "Start" button
  - 🔴 **Deallocated** → Click "Start" button  
  - 🟢 **Running** → Go to Step B
  - ⚠️ **Other** → Take screenshot, escalate

### B. If VM is Running but Unreachable

- [ ] Check **Network Security Group (NSG)**:
  - Go to VM → Networking → Network Security Group
  - Verify inbound rules allow:
    - [ ] Port 22 (SSH)
    - [ ] Port 80 (HTTP)
    - [ ] Port 443 (HTTPS)
    - [ ] Port 8000 (API)
    - [ ] Port 8443 (Bot webhook)

- [ ] Check **Subscription Status**:
  - Go to Subscriptions → Verify billing is active
  - Check for spending limits

- [ ] **Restart VM**:
  - VM → Overview → Restart
  - Wait 2-3 minutes

### C. Verify Connectivity

```bash
# Run from your machine
ping -c 3 20.234.16.216

# If ping works, try SSH
ssh azureuser@20.234.16.216 "echo 'VM is back!'"
```

- [ ] Ping responds
- [ ] SSH connects

---

## Step 2: Verify Services

### Run Quick Check

```bash
cd /home/tair/.openclaw/workspace/zeta-platform
./verify-quick.sh
```

### Or Manual Checks

```bash
# Database
ssh azureuser@20.234.16.216 "sudo -u postgres psql zeta_platform -c 'SELECT COUNT(*) FROM products;'"

# Redis
ssh azureuser@20.234.16.216 "redis-cli ping"

# API service
ssh azureuser@20.234.16.216 "sudo systemctl status zeta-api"

# API health
curl -s http://20.234.16.216:8000/health | jq

# Bot service
ssh azureuser@20.234.16.216 "sudo systemctl status zeta-bot"
```

**Checklist:**
- [ ] PostgreSQL responding
- [ ] Redis responding
- [ ] zeta-api service running
- [ ] API /health returns success
- [ ] zeta-bot service running

---

## Step 3: Configure Telegram Webhook (CRITICAL)

```bash
curl -X POST "https://api.telegram.org/bot7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM/setWebhook" \
  -d "url=https://20.234.16.216:8443/webhook"
```

### Verify Webhook

```bash
curl -s "https://api.telegram.org/bot7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM/getWebhookInfo" | jq
```

**Checklist:**
- [ ] Webhook URL set to `https://20.234.16.216:8443/webhook`
- [ ] `has_custom_certificate` is false
- [ ] `pending_update_count` is 0 or low
- [ ] No `last_error_message`

---

## Step 4: Test End-to-End

### A. Test API Endpoints

```bash
# Products
curl -s "http://20.234.16.216:8000/products?limit=5" | jq

# Cities
curl -s "http://20.234.16.216:8000/cities" | jq

# Search
curl -s "http://20.234.16.216:8000/products/search?query=chair&limit=3" | jq
```

- [ ] Products endpoint works
- [ ] Cities endpoint works
- [ ] Search endpoint works

### B. Test User Registration

```bash
TEST_EMAIL="verify-$(date +%s)@example.com"

curl -X POST http://20.234.16.216:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"TestPass123!\"}"

# Verify in database
ssh azureuser@20.234.16.216 "sudo -u postgres psql zeta_platform -c \"SELECT email FROM users WHERE email='$TEST_EMAIL';\""
```

- [ ] Registration succeeds
- [ ] User appears in database

### C. Test Telegram Bot

1. Open Telegram
2. Send message to **@zeta_taldykorgan_bot**
3. Type: `/start`

**Expected:** Bot responds

```bash
# Check bot logs
ssh azureuser@20.234.16.216 "sudo journalctl -u zeta-bot -n 20 --no-pager"
```

- [ ] Bot receives message
- [ ] Bot responds
- [ ] No errors in logs

### D. Test Frontend

1. Open: https://web-ten-sigma-30.vercel.app
2. Check browser console (F12)
3. Navigate through pages

**Checklist:**
- [ ] Frontend loads
- [ ] No API errors in console
- [ ] Products display (if applicable)
- [ ] Search works (if applicable)

---

## Step 5: Post-Recovery Actions

### A. Check Logs for Issues

```bash
# API logs (last 100 lines)
ssh azureuser@20.234.16.216 "sudo journalctl -u zeta-api -n 100 --no-pager"

# Bot logs (last 100 lines)
ssh azureuser@20.234.16.216 "sudo journalctl -u zeta-bot -n 100 --no-pager"

# System logs (errors)
ssh azureuser@20.234.16.216 "sudo journalctl -p err -n 50 --no-pager"
```

- [ ] No critical errors
- [ ] Services started cleanly
- [ ] No repeated warnings

### B. Check Disk Space

```bash
ssh azureuser@20.234.16.216 "df -h"
```

- [ ] Root partition < 80% full
- [ ] No partitions at 100%

### C. Check Memory

```bash
ssh azureuser@20.234.16.216 "free -h"
```

- [ ] Available memory > 500MB
- [ ] Swap usage < 50%

---

## Step 6: Set Up Monitoring (Prevent Future Outages)

### A. Azure Monitor Alerts

1. Go to Azure Portal
2. Navigate to: **Monitor** → **Alerts** → **Create alert rule**
3. Create alerts for:
   - [ ] **VM stopped** (ResourceHealth)
   - [ ] **CPU > 90%** for 5 minutes
   - [ ] **Memory > 90%** for 5 minutes
   - [ ] **Disk > 85%**

### B. External Uptime Monitoring

1. Sign up for UptimeRobot (free) or similar
2. Add monitors:
   - [ ] http://20.234.16.216:8000/health (every 5 min)
   - [ ] https://web-ten-sigma-30.vercel.app (every 5 min)
   - [ ] Telegram bot webhook (GET request)

### C. Log Monitoring

```bash
# Set up log rotation
ssh azureuser@20.234.16.216 "sudo systemctl status systemd-journald"

# Check journal size
ssh azureuser@20.234.16.216 "sudo journalctl --disk-usage"
```

- [ ] Log rotation configured
- [ ] Journal size < 1GB

---

## Step 7: Documentation

- [ ] Update `INFRASTRUCTURE_MAP.md` with current status
- [ ] Document what caused the outage (if known)
- [ ] Update runbooks with recovery steps
- [ ] Schedule post-mortem review

---

## Recovery Complete! ✅

When all checks pass, run full verification:

```bash
cd /home/tair/.openclaw/workspace/zeta-platform
./verify-quick.sh > recovery-verification.log 2>&1
cat recovery-verification.log
```

### Success Criteria

- ✅ VM reachable and running
- ✅ All services active (zeta-api, zeta-bot)
- ✅ Database responding with data
- ✅ Redis responding
- ✅ API endpoints working
- ✅ Telegram webhook configured
- ✅ Bot receiving messages
- ✅ Frontend connected to backend
- ✅ End-to-end flows working

---

## Escalation

If recovery takes > 1 hour or issues persist:

1. **Take snapshots:**
   - Azure VM disk snapshot
   - Database backup
   - Configuration files

2. **Gather diagnostics:**
   ```bash
   ssh azureuser@20.234.16.216 "sudo dmesg | tail -100"
   ssh azureuser@20.234.16.216 "sudo systemctl --failed"
   ```

3. **Contact:**
   - Azure Support (if infrastructure issue)
   - Database admin (if data corruption)
   - Review backup/restore procedures

---

**Recovery started:** [Fill in time]  
**Recovery completed:** [Fill in time]  
**Total downtime:** [Calculate]  
**Root cause:** [Document findings]
