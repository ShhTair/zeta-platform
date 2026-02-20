# WhatsApp Bot Setup Guide

Complete guide to setting up ZETA WhatsApp Bot with Meta Business Cloud API.

---

## Prerequisites

1. **Meta Business Account** (https://business.facebook.com)
2. **WhatsApp Business Account**
3. **Phone number** (not currently used on WhatsApp)
4. **Server** with public HTTPS endpoint
5. **Redis** instance

---

## Part 1: Meta Business Setup

### 1.1 Create Meta Business App

1. Go to https://developers.facebook.com/apps/
2. Click **"Create App"**
3. Select **"Business"** type
4. App name: `ZETA Furniture Bot`
5. Contact email: your email
6. Click **Create App**

### 1.2 Add WhatsApp Product

1. In app dashboard, find **WhatsApp** in products list
2. Click **"Set up"**
3. Choose **"Business"** account type
4. Create or select existing **Business Portfolio**

### 1.3 Configure WhatsApp Business Profile

1. Go to **WhatsApp → Getting Started**
2. Fill business profile:
   - **Business Name:** ZETA Furniture
   - **Category:** Home & Garden → Furniture
   - **Description:** Мебельный магазин в Талдыкоргане
   - **Address:** ул. Примерная, 123, Талдыкорган
   - **Website:** https://zeta-furniture.kz
   - **Hours:** Пн-Сб 10:00-20:00

### 1.4 Get Phone Number

**Option A: Use Test Number (Development)**
- Meta provides test number for free
- Can send messages to up to 5 numbers
- Good for testing

**Option B: Register Your Number (Production)**
1. Go to **Phone Numbers → Add Phone Number**
2. Enter your business phone number
3. Verify via SMS or call
4. Pay fee (~$0/month for light usage)

### 1.5 Get API Credentials

1. Go to **WhatsApp → API Setup**
2. Copy these values:

```env
WHATSAPP_TOKEN=<Temporary access token - valid 24h>
WHATSAPP_PHONE_NUMBER_ID=<Phone number ID>
WHATSAPP_BUSINESS_ACCOUNT_ID=<Business account ID>
```

3. Generate **permanent access token**:
   - Go to **Settings → System Users**
   - Create system user: `ZETA Bot`
   - Add permissions: `whatsapp_business_messaging`, `whatsapp_business_management`
   - Generate token → copy to `.env`

---

## Part 2: Server Setup

### 2.1 Install Dependencies

```bash
cd /path/to/zeta-platform/apps/whatsapp-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Whisper (optional, for voice messages)
pip install openai-whisper

# Install Tesseract (for OCR)
sudo apt-get install tesseract-ocr tesseract-ocr-rus tesseract-ocr-kaz
```

### 2.2 Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env
nano .env
```

Fill in values:

```env
# WhatsApp (from Meta Business Manager)
WHATSAPP_TOKEN=your_permanent_token_here
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=your_random_secret_here  # Make up a random string
WHATSAPP_BUSINESS_ACCOUNT_ID=123456789012345

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here

# Backend API
API_URL=http://localhost:8000
CITY_ID=1

# Redis
REDIS_URL=redis://localhost:6379/0

# Server
HOST=0.0.0.0
PORT=8000
WEBHOOK_URL=https://your-domain.com  # Your public HTTPS URL

# Admin Integration
ADMIN_API_URL=http://localhost:8000
ADMIN_API_KEY=your_admin_key_here
```

### 2.3 Start Redis

```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:latest

# OR install locally
sudo apt-get install redis-server
sudo systemctl start redis
```

### 2.4 Setup HTTPS (Required!)

WhatsApp only accepts HTTPS webhooks. Options:

**Option A: Nginx + Let's Encrypt**

```nginx
# /etc/nginx/sites-available/whatsapp-bot
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Option B: Cloudflare Tunnel**

```bash
cloudflared tunnel --url http://localhost:8000
# Use the https://*.trycloudflare.com URL as WEBHOOK_URL
```

**Option C: ngrok (Development Only)**

```bash
ngrok http 8000
# Use the https://*.ngrok.io URL
```

---

## Part 3: Webhook Registration

### 3.1 Start Bot

```bash
cd /path/to/zeta-platform/apps/whatsapp-bot
source venv/bin/activate
python main.py
```

Check logs:
```
INFO - 🚀 Starting ZETA WhatsApp Bot
INFO - 📱 Phone Number ID: 123456789012345
INFO - ✅ Redis connected
INFO - ✅ WhatsApp bot ready!
INFO - Uvicorn running on http://0.0.0.0:8000
```

### 3.2 Register Webhook in Meta

1. Go to **WhatsApp → Configuration**
2. Click **"Edit"** next to Webhook
3. Fill in:
   - **Callback URL:** `https://your-domain.com/webhook/whatsapp`
   - **Verify token:** (same as `WHATSAPP_VERIFY_TOKEN` in .env)
4. Click **"Verify and Save"**

If successful, you'll see: ✅ **Webhook verified**

### 3.3 Subscribe to Webhook Fields

1. In **Webhook** section, click **"Manage"**
2. Subscribe to:
   - ✅ `messages` (incoming messages)
   - ✅ `message_status` (delivery receipts)
3. Click **"Save"**

---

## Part 4: Template Approval

WhatsApp requires pre-approved templates for messages sent OUTSIDE 24-hour conversation window.

### 4.1 Create Templates

1. Go to **WhatsApp → Message Templates**
2. Click **"Create Template"**
3. Fill in details from `templates/message_templates.yaml`

Example: Price Alert Template

```
Template Name: price_alert
Category: UTILITY
Language: Russian

Header: 🔔 Цена снизилась!

Body:
Отличные новости! Цена на товар {{1}} (арт. {{2}}) снизилась с {{3}} ₸ до {{4}} ₸!

Экономия: {{5}} ₸ ({{6}}%)

Товар доступен на сайте. Успейте оформить заказ!

Buttons:
- URL: Посмотреть товар → https://zeta-furniture.kz/products/{{1}}
- Phone: Позвонить менеджеру → +77001234567

Example:
{{1}} = Диван угловой серый
{{2}} = SOFA-123
{{3}} = 120000
{{4}} = 95000
{{5}} = 25000
{{6}} = 20
```

4. Click **"Submit"**
5. Wait for approval (usually 1-3 business days)

### 4.2 Required Templates

Create these templates (see `templates/message_templates.yaml`):

1. ✅ `price_alert` - Price drop notifications
2. ✅ `new_products_notification` - New products matching saved searches
3. ✅ `order_confirmation` - Order confirmation
4. ✅ `order_status_update` - Order status updates
5. ✅ `manager_response` - Manager replies after 24h window

**Kazakh versions:**
6. ✅ `price_alert_kz`
7. ✅ `new_products_notification_kz`

---

## Part 5: Testing

### 5.1 Send Test Message

1. Open WhatsApp on your phone
2. Add your business number to contacts
3. Send message: `Привет`

Expected response:
```
👋 Добро пожаловать в ZETA Furniture!

Я - умный ассистент, помогу найти идеальную мебель для вашего дома! 🪑

Что вас интересует?

[📖 Каталог] [🔍 Поиск] [💬 Менеджер]
```

### 5.2 Test Features

**1. Text Search:**
```
User: Нужен диван
Bot: С удовольствием помогу! 🛋️ Для какой комнаты ищете?
User: Для гостиной, серый
Bot: [Shows product list with 5 gray sofas]
```

**2. Image Search:**
- Send product photo
- Bot: 👀 (reaction)
- Bot: Нашёл! [product list]

**3. Voice Message** (if enabled):
- Send voice: "Нужен диван для гостиной"
- Bot: 🎤 Вы сказали: "Нужен диван для гостиной"
- Bot: [Processes as text message]

**4. Interactive Buttons:**
- Click product from list
- Bot sends: Image + details + [💬 Менеджер] [🔍 Похожие] [🔔 Цена ↓]

### 5.3 Check Logs

```bash
tail -f /var/log/whatsapp-bot.log
```

Look for:
- ✅ Message received
- ✅ AI response generated
- ✅ Product search completed
- ✅ Message sent

---

## Part 6: Production Deployment

### 6.1 Create Systemd Service

```bash
sudo nano /etc/systemd/system/whatsapp-bot.service
```

```ini
[Unit]
Description=ZETA WhatsApp Bot
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/zeta-platform/apps/whatsapp-bot
Environment="PATH=/opt/zeta-platform/apps/whatsapp-bot/venv/bin"
ExecStart=/opt/zeta-platform/apps/whatsapp-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-bot
sudo systemctl start whatsapp-bot
sudo systemctl status whatsapp-bot
```

### 6.2 Setup Monitoring

**Option A: Prometheus + Grafana**

```python
# Add to main.py
from prometheus_client import Counter, Histogram, make_asgi_app

messages_received = Counter('whatsapp_messages_received_total', 'Total messages received')
response_time = Histogram('whatsapp_response_time_seconds', 'Response time')

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Option B: Sentry (Error Tracking)**

```python
import sentry_sdk
sentry_sdk.init(dsn=settings.sentry_dsn)
```

### 6.3 Setup Backup

```bash
# Redis backup
redis-cli BGSAVE

# Automated daily backup
0 2 * * * /usr/bin/redis-cli BGSAVE && cp /var/lib/redis/dump.rdb /backup/redis-$(date +\%Y\%m\%d).rdb
```

---

## Part 7: Background Workers

### 7.1 Price Alert Worker

```bash
cd /path/to/zeta-platform/apps/whatsapp-bot
python workers/price_alert_worker.py
```

This worker:
- Runs daily
- Checks all saved price alerts
- Sends template message when price drops

### 7.2 New Products Worker

```bash
python workers/new_products_worker.py
```

This worker:
- Runs when new products added
- Matches against saved searches
- Notifies users via template

---

## Troubleshooting

### Webhook Verification Failed

**Problem:** Webhook verification returns 403

**Solutions:**
1. Check `WHATSAPP_VERIFY_TOKEN` matches in `.env` and Meta dashboard
2. Ensure bot is running: `curl http://localhost:8000/health`
3. Check HTTPS is working: `curl https://your-domain.com/`
4. Check logs: `journalctl -u whatsapp-bot -f`

### Messages Not Arriving

**Problem:** No messages received

**Solutions:**
1. Check webhook subscriptions: `messages` field enabled?
2. Check phone number status: Active? Verified?
3. Test with curl:
```bash
curl -X POST https://your-domain.com/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"entry":[{"changes":[{"value":{"messages":[{"from":"123","type":"text","text":{"body":"test"}}]}}]}]}'
```

### Rate Limiting

**Problem:** "Rate limit exceeded" error

**Solutions:**
1. Meta has limits: 1000 messages/day (free tier)
2. Upgrade to paid tier for higher limits
3. Implement user-side rate limiting (already in code)

### Redis Connection Failed

**Problem:** Bot works but no conversation memory

**Solutions:**
1. Check Redis is running: `redis-cli ping` → `PONG`
2. Check `REDIS_URL` in `.env`
3. Check firewall: `sudo ufw allow 6379`

---

## Next Steps

1. ✅ Test all features thoroughly
2. ✅ Get templates approved
3. ✅ Setup monitoring
4. ✅ Configure backup workers
5. ✅ Train staff on escalation handling
6. 🚀 Launch to customers!

---

## Support

- **Meta WhatsApp Support:** https://developers.facebook.com/support/
- **Bot Logs:** `/var/log/whatsapp-bot.log`
- **Redis Monitoring:** `redis-cli MONITOR`

---

**Setup complete! Your WhatsApp bot is ready to serve customers! 🎉**
