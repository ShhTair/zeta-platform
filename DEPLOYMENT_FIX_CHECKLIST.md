# ZETA Platform - Emergency Deployment Fix Checklist

**Status:** 🔴 CRITICAL - Services Down  
**Date:** 2026-02-20  
**Priority:** P0 - Production Blocker

---

## Critical Issues Summary

❌ **Backend API:** Not responding (timeout on all endpoints)  
❌ **Telegram Bot:** Webhook not set (bot not receiving messages)  
❌ **Admin Panel:** Cannot login (HTTPS/HTTP mixed content error)  
❌ **SSH Access:** Blocked (cannot reach Azure VM)

---

## Emergency Fix Steps

### Phase 1: Restore VM Access (30 min)

**Option A: Azure Portal Console**
```bash
# 1. Login to Azure Portal
https://portal.azure.com

# 2. Navigate to Virtual Machine
Resource: openclaw-prod-01 or similar (20.234.16.216)

# 3. Connect via Serial Console or Bastion
```

**Option B: Fix Network Security Group**
```bash
# 1. Go to VM → Networking → Network Security Group
# 2. Add Inbound Rule:
#    - Source: Your IP or "Any"
#    - Port: 22 (SSH)
#    - Priority: 100
#    - Name: Allow-SSH

# 3. Test SSH connection
ssh azureuser@20.234.16.216
```

### Phase 2: Check VM Status (10 min)

```bash
# Once SSH works:

# 1. Check VM is running
uptime

# 2. Check disk space
df -h

# 3. Check memory
free -h

# 4. Check running services
sudo systemctl status zeta-backend
sudo systemctl status zeta-bot

# 5. Check recent logs
sudo journalctl -n 100 --no-pager
```

### Phase 3: Restart Backend API (15 min)

```bash
# 1. Check service status
sudo systemctl status zeta-backend

# 2. If not running, check why
sudo journalctl -u zeta-backend -n 50

# 3. Check backend directory
cd /home/azureuser/zeta-platform/apps/backend
ls -la

# 4. Check .env file
cat .env | grep -v PASSWORD

# 5. Try starting manually (debug mode)
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 6. If successful, stop and use systemd
# Ctrl+C
sudo systemctl restart zeta-backend

# 7. Verify it's running
curl -s http://localhost:8000/health | jq

# 8. Check from outside
curl -s http://20.234.16.216:8000/health | jq
```

**If service doesn't exist:**
```bash
# Create systemd service file
sudo nano /etc/systemd/system/zeta-backend.service

# Paste:
[Unit]
Description=ZETA Backend API
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/home/azureuser/zeta-platform/apps/backend
Environment="PATH=/home/azureuser/zeta-platform/apps/backend/venv/bin"
ExecStart=/home/azureuser/zeta-platform/apps/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Save and enable
sudo systemctl daemon-reload
sudo systemctl enable zeta-backend
sudo systemctl start zeta-backend
sudo systemctl status zeta-backend
```

### Phase 4: Restart Telegram Bot (15 min)

```bash
# 1. Check bot service
sudo systemctl status zeta-bot

# 2. Check bot logs
sudo journalctl -u zeta-bot -n 50

# 3. Check bot directory
cd /home/azureuser/zeta-platform/apps/bot
ls -la

# 4. Check .env
cat .env | grep BOT_TOKEN

# 5. Check webhook certificate
ls -la webhook_cert.pem 2>/dev/null || echo "Certificate missing!"

# 6. If certificate missing, generate it:
openssl req -x509 -newkey rsa:2048 -keyout webhook_key.pem -out webhook_cert.pem -days 365 -nodes -subj "/CN=20.234.16.216"

# 7. Try starting manually (debug)
source venv/bin/activate
python bot.py

# 8. Check logs for webhook status
# Look for: "✅ Webhook set" or errors

# 9. If successful, stop and use systemd
# Ctrl+C
sudo systemctl restart zeta-bot

# 10. Verify webhook is set
BOT_TOKEN="7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM"
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo" | jq '.result.url'
# Should show: "https://20.234.16.216:8443/webhook"
```

**If service doesn't exist:**
```bash
# Create systemd service
sudo nano /etc/systemd/system/zeta-bot.service

# Paste:
[Unit]
Description=ZETA Telegram Bot
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/home/azureuser/zeta-platform/apps/bot
Environment="PATH=/home/azureuser/zeta-platform/apps/bot/venv/bin"
ExecStart=/home/azureuser/zeta-platform/apps/bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Save and enable
sudo systemctl daemon-reload
sudo systemctl enable zeta-bot
sudo systemctl start zeta-bot
sudo systemctl status zeta-bot
```

### Phase 5: Setup HTTPS for Backend (60-90 min)

**This fixes the mixed content error blocking admin panel login.**

```bash
# 1. Install nginx and certbot
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

# 2. Create nginx config
sudo nano /etc/nginx/sites-available/zeta-backend

# Paste:
server {
    listen 80;
    server_name 20.234.16.216;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# 3. Enable site
sudo ln -s /etc/nginx/sites-available/zeta-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 4. Test HTTP proxy works
curl -s http://20.234.16.216/health | jq

# 5. Get SSL certificate (if you have domain)
# If using IP address, you'll need to:
#   - Get a domain name (e.g., zeta-api.example.com)
#   - Point it to 20.234.16.216
#   - Then run:
sudo certbot --nginx -d zeta-api.example.com

# 6. For IP-only (self-signed certificate):
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt \
  -subj "/CN=20.234.16.216"

# Update nginx config:
sudo nano /etc/nginx/sites-available/zeta-backend

# Replace with:
server {
    listen 443 ssl;
    server_name 20.234.16.216;

    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name 20.234.16.216;
    return 301 https://$server_name$request_uri;
}

# Restart nginx
sudo systemctl restart nginx

# 7. Update admin panel environment variable
# In Vercel dashboard, update:
NEXT_PUBLIC_API_URL=https://20.234.16.216
# (Instead of http://20.234.16.216:8000)

# 8. Test HTTPS endpoint
curl -k -s https://20.234.16.216/health | jq
```

### Phase 6: Open Firewall Ports (10 min)

```bash
# Azure Portal:
# 1. Go to VM → Networking → Add inbound port rule

# Add these rules:
# - Port 22 (SSH) - Priority 100
# - Port 80 (HTTP) - Priority 110
# - Port 443 (HTTPS) - Priority 120
# - Port 8000 (Backend direct) - Priority 130
# - Port 8443 (Bot webhook) - Priority 140

# OR via Azure CLI:
az network nsg rule create \
  --resource-group <resource-group> \
  --nsg-name <nsg-name> \
  --name Allow-HTTP \
  --priority 110 \
  --source-address-prefixes '*' \
  --destination-port-ranges 80 \
  --access Allow \
  --protocol Tcp

az network nsg rule create \
  --resource-group <resource-group> \
  --nsg-name <nsg-name> \
  --name Allow-HTTPS \
  --priority 120 \
  --source-address-prefixes '*' \
  --destination-port-ranges 443 \
  --access Allow \
  --protocol Tcp

az network nsg rule create \
  --resource-group <resource-group> \
  --nsg-name <nsg-name> \
  --name Allow-Bot-Webhook \
  --priority 140 \
  --source-address-prefixes '*' \
  --destination-port-ranges 8443 \
  --access Allow \
  --protocol Tcp
```

### Phase 7: Verify Everything Works (15 min)

```bash
# 1. Backend API health
curl -s http://20.234.16.216:8000/health | jq
curl -k -s https://20.234.16.216/health | jq

# 2. Backend API search
curl -s "http://20.234.16.216:8000/products/search?query=стул&limit=5" | jq '.[:2]'

# 3. Backend API auth
TOKEN=$(curl -s -X POST http://20.234.16.216:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@zeta.local","password":"admin123"}' \
  | jq -r '.access_token')
echo "Token: $TOKEN"

# 4. Bot webhook status
BOT_TOKEN="7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM"
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo" | jq '.result | {url, has_custom_certificate, pending_update_count}'

# 5. Test bot (send message)
# Open Telegram, search: @zeta_taldykorgan_bot
# Send: /start
# Expected: Welcome message with buttons

# 6. Test admin panel
# Open: https://web-ten-sigma-30.vercel.app
# Login: admin@zeta.local / admin123
# Expected: Dashboard loads

# 7. Check service status
sudo systemctl status zeta-backend
sudo systemctl status zeta-bot

# 8. Check recent logs
sudo journalctl -u zeta-backend -n 20 --no-pager
sudo journalctl -u zeta-bot -n 20 --no-pager
```

---

## Optional: Install Redis (30 min)

**This enables conversation memory and rate limiting.**

```bash
# 1. Install Redis
sudo apt update
sudo apt install -y redis-server

# 2. Configure Redis
sudo nano /etc/redis/redis.conf
# Change: supervised no → supervised systemd

# 3. Start Redis
sudo systemctl restart redis
sudo systemctl enable redis

# 4. Test Redis
redis-cli ping
# Expected: PONG

# 5. Update bot .env
cd /home/azureuser/zeta-platform/apps/bot
nano .env
# Add:
REDIS_URL=redis://localhost:6379/0

# 6. Update integrations config
nano config/integrations.yaml
# Change:
# advanced:
#   memory:
#     enabled: true  # Change from false
#   rate_limit:
#     enabled: true  # Change from false

# 7. Restart bot
sudo systemctl restart zeta-bot

# 8. Test memory
# Send to bot: "привет, меня зовут Иван"
# Then: "как меня зовут?"
# Expected: Bot remembers "Иван"
```

---

## Verification Checklist

### ✅ Services Running
- [ ] Backend API responding on http://20.234.16.216:8000/health
- [ ] Backend API responding on https://20.234.16.216/health (if HTTPS setup)
- [ ] Telegram bot webhook set: https://20.234.16.216:8443/webhook
- [ ] Bot responds to /start command
- [ ] Admin panel can login

### ✅ Functionality Working
- [ ] Bot AI conversation works (send: "хочу стул")
- [ ] Bot shows product suggestions with buttons
- [ ] Bot image search works (send photo)
- [ ] Admin panel dashboard loads
- [ ] Admin panel shows products
- [ ] Can edit bot config in admin panel
- [ ] Backend API /products/search works
- [ ] Backend API /auth/login works

### ✅ Optional Features
- [ ] Redis installed and running
- [ ] Conversation memory enabled
- [ ] Rate limiting enabled
- [ ] Bot remembers context across messages

### ✅ Monitoring Setup (Future)
- [ ] Health check monitoring configured
- [ ] Email alerts for downtime
- [ ] Log aggregation setup
- [ ] Dashboard for metrics

---

## Common Issues & Solutions

### Issue: "Connection refused" on port 8000
**Solution:**
```bash
# Check if service is running
sudo systemctl status zeta-backend

# Check if port is open
sudo netstat -tlnp | grep 8000

# Check logs
sudo journalctl -u zeta-backend -n 50

# Restart service
sudo systemctl restart zeta-backend
```

### Issue: Bot webhook returns "Wrong response from the webhook"
**Solution:**
```bash
# Check certificate is valid
openssl x509 -in webhook_cert.pem -noout -dates

# Regenerate certificate if expired
openssl req -x509 -newkey rsa:2048 -keyout webhook_key.pem -out webhook_cert.pem -days 365 -nodes -subj "/CN=20.234.16.216"

# Set webhook with new certificate
curl -F "url=https://20.234.16.216:8443/webhook" \
     -F "certificate=@webhook_cert.pem" \
     https://api.telegram.org/bot7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM/setWebhook
```

### Issue: Admin panel "Mixed Content" error
**Solution:**
```bash
# Either:
# 1. Setup HTTPS on backend (see Phase 5)
# OR
# 2. Update admin panel to use HTTP URL (not recommended for production)
# In Vercel environment variables:
NEXT_PUBLIC_API_URL=http://20.234.16.216:8000
```

### Issue: Database connection error
**Solution:**
```bash
# Check database is running
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep zeta

# Check connection settings in backend .env
cd /home/azureuser/zeta-platform/apps/backend
cat .env | grep DATABASE_URL

# Test connection
sudo -u postgres psql -d zeta_db -c "SELECT COUNT(*) FROM products;"
```

### Issue: "Module not found" errors
**Solution:**
```bash
# Reinstall dependencies
cd /home/azureuser/zeta-platform/apps/bot
source venv/bin/activate
pip install -r requirements.txt -r requirements-integrations.txt

cd /home/azureuser/zeta-platform/apps/backend
source venv/bin/activate
pip install -r requirements.txt
```

---

## Post-Fix Testing Script

Save this as `verify_deployment.sh` and run after fixes:

```bash
#!/bin/bash
echo "=== ZETA Platform Deployment Verification ==="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

BOT_TOKEN="7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM"
API_URL="http://20.234.16.216:8000"

# Test 1: Backend Health
echo -n "1. Backend Health Check... "
response=$(curl -s -w "%{http_code}" -o /dev/null "$API_URL/health")
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL (HTTP $response)${NC}"
fi

# Test 2: Backend Products
echo -n "2. Backend Products Search... "
response=$(curl -s -w "%{http_code}" -o /dev/null "$API_URL/products/search?query=стул&limit=1")
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL (HTTP $response)${NC}"
fi

# Test 3: Backend Auth
echo -n "3. Backend Authentication... "
response=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@zeta.local","password":"admin123"}')
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL (HTTP $response)${NC}"
fi

# Test 4: Bot Info
echo -n "4. Bot API Connection... "
bot_info=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getMe")
if echo "$bot_info" | grep -q "zeta_taldykorgan_bot"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Test 5: Bot Webhook
echo -n "5. Bot Webhook Status... "
webhook_info=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo")
webhook_url=$(echo "$webhook_info" | jq -r '.result.url')
if [ "$webhook_url" = "https://20.234.16.216:8443/webhook" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL (URL: $webhook_url)${NC}"
fi

# Test 6: Admin Panel
echo -n "6. Admin Panel Loads... "
response=$(curl -s -w "%{http_code}" -o /dev/null "https://web-ten-sigma-30.vercel.app")
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL (HTTP $response)${NC}"
fi

echo ""
echo "=== Verification Complete ==="
```

---

## Emergency Contacts

**Azure Portal:** https://portal.azure.com  
**Vercel Dashboard:** https://vercel.com/dashboard  
**Telegram Bot API Docs:** https://core.telegram.org/bots/api  

**Bot Token:** 7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM  
**Admin Credentials:** admin@zeta.local / admin123  
**Azure VM IP:** 20.234.16.216

---

**Created:** 2026-02-20 06:40 UTC  
**Last Updated:** 2026-02-20 06:40 UTC  
**Next Review:** After fixes applied
