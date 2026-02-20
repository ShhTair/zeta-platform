# ZETA WhatsApp Bot - Quick Start Guide

> **Get up and running in 30 minutes!**

This guide gets you from zero to deployed bot in ~30 minutes for testing, or 4-6 hours for full production.

---

## 🚀 Fast Track (30 Minutes)

### Step 1: Install Dependencies (5 min)

```bash
# Navigate to project
cd /path/to/zeta-platform/apps/whatsapp-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install optional (voice support)
pip install openai-whisper
```

### Step 2: Setup Redis (2 min)

```bash
# Option A: Docker (recommended)
docker run -d --name redis -p 6379:6379 redis:latest

# Option B: Local install
sudo apt-get install redis-server
sudo systemctl start redis
```

### Step 3: Configure Environment (3 min)

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

**Minimum required:**
```env
# Get from Meta Business Manager (see below)
WHATSAPP_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=123456789
WHATSAPP_VERIFY_TOKEN=make_up_a_random_string
WHATSAPP_BUSINESS_ACCOUNT_ID=123456789

# Get from OpenAI
OPENAI_API_KEY=sk-proj-your-key-here

# Local backend (or your production URL)
API_URL=http://localhost:8000
CITY_ID=1

# Redis
REDIS_URL=redis://localhost:6379/0

# Your public HTTPS URL (ngrok for testing)
WEBHOOK_URL=https://your-domain.com
```

### Step 4: Get Meta Credentials (10 min)

1. Go to https://developers.facebook.com/apps/
2. Click **"Create App"** → **"Business"**
3. Add **WhatsApp** product
4. Go to **WhatsApp → Getting Started**
5. Copy these values to `.env`:
   - **Temporary Access Token** → `WHATSAPP_TOKEN`
   - **Phone Number ID** → `WHATSAPP_PHONE_NUMBER_ID`
   - **Business Account ID** → `WHATSAPP_BUSINESS_ACCOUNT_ID`
6. Make up a random string for `WHATSAPP_VERIFY_TOKEN` (e.g., `my_secret_123`)

### Step 5: Setup Webhook (5 min)

```bash
# Option A: ngrok (quick testing)
ngrok http 8000
# Copy the https://xxxx.ngrok.io URL

# Option B: Your server with HTTPS
# Use your actual domain URL
```

Update `.env`:
```env
WEBHOOK_URL=https://xxxx.ngrok.io  # or your domain
```

### Step 6: Start Bot (1 min)

```bash
python main.py
```

You should see:
```
INFO - 🚀 Starting ZETA WhatsApp Bot
INFO - 📱 Phone Number ID: 123456789
INFO - ✅ Redis connected
INFO - ✅ WhatsApp bot ready!
INFO - Uvicorn running on http://0.0.0.0:8000
```

### Step 7: Register Webhook in Meta (3 min)

1. In Meta dashboard: **WhatsApp → Configuration**
2. Click **"Edit"** next to Webhook
3. Enter:
   - **Callback URL:** `https://xxxx.ngrok.io/webhook/whatsapp`
   - **Verify token:** (same as `WHATSAPP_VERIFY_TOKEN` in .env)
4. Click **"Verify and Save"**
5. Subscribe to fields: `messages`, `message_status`

✅ **If successful:** "Webhook verified" ✓

### Step 8: Test! (1 min)

1. Open WhatsApp on your phone
2. Send message to your business number: `Hello`
3. Bot should respond: Welcome menu with buttons

---

## ✅ Success Checklist

- ✅ Dependencies installed
- ✅ Redis running
- ✅ `.env` configured
- ✅ Bot started (no errors in logs)
- ✅ Webhook registered (green checkmark in Meta)
- ✅ Test message received response

**Congratulations! Your bot is running! 🎉**

---

## 🧪 Quick Tests

### Test 1: Text Message

```
You: Привет
Bot: [Welcome menu with 3 buttons]
```

### Test 2: Product Search

```
You: Нужен диван
Bot: С удовольствием помогу! 🛋️ Для какой комнаты ищете?
You: Для гостиной, серый
Bot: [Shows list of gray sofas]
```

### Test 3: Image Search

```
You: [Send product photo]
Bot: 👀 (reaction)
Bot: Нашёл! [product results]
```

### Test 4: Buttons

```
[Tap "Каталог" button]
Bot: [Shows product categories]
```

---

## 🚨 Troubleshooting

### Bot doesn't respond to messages

1. **Check webhook:** Meta dashboard → should see green checkmark
2. **Check logs:** Look for errors in terminal
3. **Test webhook manually:**
```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"entry":[{"changes":[{"value":{"messages":[{"from":"123","type":"text","text":{"body":"test"}}]}}]}]}'
```

### Webhook verification failed

1. **Check verify token:** Must match exactly in `.env` and Meta dashboard
2. **Check URL:** Must be HTTPS (use ngrok for testing)
3. **Check bot is running:** `curl http://localhost:8000/health`

### Redis connection error

```bash
# Check Redis is running
redis-cli ping  # Should respond: PONG

# Check REDIS_URL in .env
REDIS_URL=redis://localhost:6379/0
```

### OpenAI API error

1. **Check API key:** Copy from https://platform.openai.com/api-keys
2. **Check quota:** https://platform.openai.com/usage
3. **Test API:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 🎯 Next Steps

### For Testing
- ✅ Test all message types (text, image, voice)
- ✅ Test interactive buttons
- ✅ Test product search
- ✅ Test manager escalation

### For Production

1. **Get permanent access token:**
   - Meta dashboard → Settings → System Users
   - Create user with WhatsApp permissions
   - Generate token → copy to `.env`

2. **Setup HTTPS properly:**
   - Use Let's Encrypt + Nginx
   - OR use Cloudflare Tunnel
   - Update `WEBHOOK_URL` in `.env`

3. **Submit templates for approval:**
   - Meta dashboard → WhatsApp → Message Templates
   - Create templates from `templates/message_templates.yaml`
   - Wait 1-3 business days for approval

4. **Deploy as systemd service:**
```bash
sudo nano /etc/systemd/system/whatsapp-bot.service
# [See WHATSAPP_SETUP.md for full config]
sudo systemctl enable whatsapp-bot
sudo systemctl start whatsapp-bot
```

5. **Setup monitoring:**
   - Add Prometheus metrics
   - Setup alerting
   - Monitor logs

---

## 📚 Documentation

- **Full Setup:** [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) (step-by-step production guide)
- **Features:** [WHATSAPP_FEATURES.md](WHATSAPP_FEATURES.md) (comparison vs Telegram)
- **Overview:** [README.md](README.md) (project documentation)
- **Completion:** [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md) (what was built)

---

## 💡 Tips

### Development
- Use **ngrok** for quick testing (no need to setup HTTPS)
- Use **Meta test number** (free, 5 recipients max)
- Check **logs** constantly: `tail -f /var/log/whatsapp-bot.log`

### Production
- Use **permanent access token** (not temporary one)
- Setup **systemd service** for auto-restart
- Enable **Redis persistence** (`SAVE` command)
- Setup **backup** for Redis data
- Use **Sentry** for error tracking
- Monitor **API quotas** (Meta + OpenAI)

### Testing
- Use **Meta Business Suite** to see message history
- Check **webhook logs** in Meta dashboard
- Test on **multiple devices** (Android, iOS)
- Test with **real users** before full launch

---

## 🆘 Need Help?

1. **Check logs first:**
```bash
# If running directly
tail -f /var/log/whatsapp-bot.log

# If using systemd
journalctl -u whatsapp-bot -f

# If using Docker
docker logs -f whatsapp-bot
```

2. **Check documentation:**
   - [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md) - Full setup guide
   - [Meta WhatsApp Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)

3. **Common issues:**
   - Webhook not working → Check HTTPS and verify token
   - No messages received → Check webhook subscriptions
   - AI not responding → Check OpenAI API key and quota
   - Redis errors → Check Redis is running

---

## ✅ You're Done!

Your ZETA WhatsApp Bot is now running and ready to help customers! 🎉

**What you have:**
- ✅ AI-powered conversation
- ✅ Product search
- ✅ Image search
- ✅ Interactive buttons & lists
- ✅ Conversation memory
- ✅ Multi-language support

**What's next:**
- 🚀 Deploy to production (see [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md))
- 📊 Monitor metrics
- 🎯 Optimize based on user feedback
- 💰 Watch conversion rates grow!

---

**Happy Building! 🪑💬**
