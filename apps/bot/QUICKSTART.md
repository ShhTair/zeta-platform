# ZETA Bot - Quick Start Guide

Get the bot running in **5 minutes**! 🚀

## Prerequisites

- Python 3.11+
- Telegram bot token (get from [@BotFather](https://t.me/BotFather))
- ngrok (for local webhook testing)

## Step 1: Install Dependencies

```bash
cd apps/bot
pip install -r requirements.txt
```

## Step 2: Setup Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
BOT_TOKEN=your_bot_token_here
CITY_ID=moscow
API_URL=http://localhost:8000
WEBHOOK_URL=https://your-ngrok-url.ngrok.io  # Will update in next step
```

## Step 3: Run with Test Script

The easy way:

```bash
./test_webhook.sh
```

This script:
1. ✅ Starts ngrok automatically
2. ✅ Updates WEBHOOK_URL
3. ✅ Starts the bot
4. ✅ Sets the webhook

## Step 4: Test the Bot

Open Telegram and message your bot:

```
You: /start
Bot: 👋 Добро пожаловать! Я помогу вам найти нужный товар.

You: I need a laptop
Bot: 🔍 Ищу в каталоге...
Bot: 📦 Найденные товары: [results]
```

---

## Alternative: Manual Setup

If you prefer step-by-step:

### 1. Start ngrok

```bash
ngrok http 8080
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

### 2. Update .env

```env
WEBHOOK_URL=https://abc123.ngrok-free.app
```

### 3. Start Bot

```bash
python3 main.py
```

You should see:
```
INFO:__main__:🚀 Starting ZETA bot for city: moscow
INFO:__main__:✅ Loaded config for city: moscow
INFO:__main__:✅ Webhook set: https://abc123.ngrok-free.app/webhook/123456789
```

---

## Troubleshooting

### Bot token invalid

```bash
# Test your token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

Should return bot info.

### Webhook not set

```bash
# Check webhook status
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

Look for `"url": "your-webhook-url"`.

### API not responding

Make sure the API is running:
```bash
cd ../api
uvicorn app.main:app --port 8000
```

### ngrok URL expired

Free ngrok URLs change every time you restart. Update `.env` and restart the bot.

---

## Next Steps

- ✅ Test product search
- ✅ Test manager escalation
- ✅ Test Bitrix ticket creation
- 📖 Read [TESTING.md](../../TESTING.md) for comprehensive tests
- 🚀 Deploy to production: [DEPLOYMENT.md](../../DEPLOYMENT.md)

---

## Quick Reference

**Start bot:**
```bash
./test_webhook.sh
```

**Check webhook:**
```bash
curl https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo
```

**View logs:**
```bash
# Live output in terminal
# OR if running in Docker:
docker logs -f zeta-bot-moscow
```

**Stop bot:**
```
Ctrl+C
```

---

**Need help?** Check the main [README.md](README.md) or [TESTING.md](../../TESTING.md).
