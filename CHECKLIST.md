# ZETA Bot - Deployment Checklist

Use this checklist to deploy the ZETA bot from scratch.

---

## 📋 Pre-Deployment

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] Docker installed (optional, for production)
- [ ] PostgreSQL database (for API)
- [ ] Domain with SSL certificate (for production webhook)
- [ ] Telegram bot token from [@BotFather](https://t.me/BotFather)

### Bot Token Setup
- [ ] Create bot with @BotFather
- [ ] Save bot token securely
- [ ] Set bot name and description
- [ ] Upload bot profile picture (optional)

---

## 🧪 Local Testing

### 1. Setup Environment
```bash
cd apps/bot
cp .env.example .env
```

- [ ] Edit `.env` with `BOT_TOKEN`
- [ ] Set `CITY_ID` (e.g., "moscow")
- [ ] Set `API_URL` (e.g., "http://localhost:8000")
- [ ] Install dependencies: `pip install -r requirements.txt`

### 2. Test with ngrok
```bash
./test_webhook.sh
```

- [ ] ngrok starts successfully
- [ ] Bot connects to Telegram
- [ ] Webhook is set (check logs: "✅ Webhook set")
- [ ] Bot responds to `/start`

### 3. Test Conversation Flow
- [ ] `/start` shows greeting
- [ ] Search query returns results
- [ ] Inline buttons appear
- [ ] Product link button works
- [ ] Manager escalation works (tag appears)
- [ ] Ticket creation works (if Bitrix is configured)

### 4. Test Dynamic Prompts
```bash
# Update prompt via API
curl -X PUT http://localhost:8000/api/cities/moscow/prompts \
  -H "Content-Type: application/json" \
  -d '{"greeting": "🎉 TEST GREETING"}'
```

- [ ] Wait 5 minutes (or restart bot)
- [ ] Send `/start` again
- [ ] New greeting appears

---

## 🚀 Production Deployment

### 1. Server Setup
- [ ] Linux server (Ubuntu 20.04+ recommended)
- [ ] Docker installed
- [ ] Domain configured (e.g., bot.zeta.com)
- [ ] SSL certificate (Let's Encrypt)
- [ ] Firewall configured (ports 80, 443)

### 2. Database Setup
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb zeta_platform

# Create user
sudo -u postgres createuser zeta
```

- [ ] Database created
- [ ] User created with password
- [ ] Migrations run: `alembic upgrade head`

### 3. API Deployment
```bash
cd apps/api

# Build Docker image
docker build -t zeta-api .

# Run container
docker run -d \
  --name zeta-api \
  -e DATABASE_URL=postgresql://zeta:pass@host/zeta_platform \
  -e SECRET_KEY=your-secret-key \
  -p 8000:8000 \
  zeta-api
```

- [ ] API container running
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] API accessible

### 4. Bot Deployment (Per City)

**Moscow Bot:**
```bash
cd apps/bot
docker build -t zeta-bot .

docker run -d \
  --name zeta-bot-moscow \
  -e BOT_TOKEN=$MOSCOW_BOT_TOKEN \
  -e CITY_ID=moscow \
  -e API_URL=http://zeta-api:8000 \
  -e WEBHOOK_URL=https://bot.zeta.com \
  -p 8080:8080 \
  zeta-bot
```

- [ ] Bot container running
- [ ] Logs show "✅ Webhook set"
- [ ] Bot responds to messages

**Repeat for each city:**
- [ ] SPB (port 8081)
- [ ] Kazan (port 8082)
- [ ] etc.

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/zeta-bot`:

```nginx
upstream api_backend {
    server localhost:8000;
}

server {
    listen 443 ssl http2;
    server_name bot.zeta.com;

    ssl_certificate /etc/letsencrypt/live/bot.zeta.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.zeta.com/privkey.pem;

    # API
    location /api/ {
        proxy_pass http://api_backend;
    }

    # Moscow bot webhook
    location /webhook/123456789 {
        proxy_pass http://localhost:8080;
    }

    # Add more cities...
}
```

- [ ] Nginx config created
- [ ] SSL certificate obtained
- [ ] Config tested: `sudo nginx -t`
- [ ] Nginx restarted: `sudo systemctl restart nginx`

### 6. Verify Webhooks
```bash
# For each bot, check webhook status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

- [ ] Each bot shows correct webhook URL
- [ ] `pending_update_count` is 0
- [ ] No errors in response

---

## 🔐 Security Checklist

- [ ] Environment variables not committed to git
- [ ] SSL/TLS enabled for webhooks
- [ ] Database password is strong
- [ ] API secret key is random (32+ chars)
- [ ] Firewall rules configured
- [ ] Only necessary ports open (80, 443)
- [ ] Docker containers run as non-root (optional)
- [ ] Nginx rate limiting enabled (optional)

---

## 📊 Monitoring Setup

### Logging
- [ ] Docker logs accessible: `docker logs zeta-bot-moscow`
- [ ] Log rotation configured (optional)
- [ ] Error monitoring setup (Sentry, optional)

### Health Checks
```bash
# API health
curl https://bot.zeta.com/api/health

# Webhook status for each bot
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

- [ ] Health check endpoint works
- [ ] Webhook status looks good
- [ ] Logs show no errors

### Alerts (Optional)
- [ ] Uptime monitoring (UptimeRobot, etc.)
- [ ] Error rate alerts
- [ ] Disk space monitoring

---

## 🧪 Post-Deployment Testing

### Functional Tests
- [ ] Send `/start` to each city bot
- [ ] Test product search
- [ ] Test manager escalation
- [ ] Test ticket creation
- [ ] Test dynamic prompt update

### Load Test (Optional)
```bash
# Install locust
pip install locust

# Run load test
locust -f locustfile.py --host=https://bot.zeta.com
```

- [ ] Bot handles 100 concurrent users
- [ ] Response times acceptable (<2s)
- [ ] No errors under load

### Multi-City Test
- [ ] Each city bot responds independently
- [ ] Correct city config loaded per bot
- [ ] Manager tags are city-specific
- [ ] Products are city-specific

---

## 📝 Documentation

- [ ] Internal docs updated with production URLs
- [ ] Team trained on deployment process
- [ ] Runbook created for common issues
- [ ] Access credentials documented securely

---

## 🔄 Maintenance Plan

### Daily
- [ ] Check logs for errors
- [ ] Monitor webhook status
- [ ] Check pending_update_count

### Weekly
- [ ] Review error logs
- [ ] Check disk space
- [ ] Test bot functionality
- [ ] Update prompts if needed

### Monthly
- [ ] Security updates
- [ ] Dependency updates
- [ ] Backup database
- [ ] Review analytics

---

## 🐛 Troubleshooting

### Bot not receiving messages
1. Check webhook: `getWebhookInfo`
2. Check SSL certificate validity
3. Check nginx logs: `tail -f /var/log/nginx/error.log`
4. Verify bot token is correct

### Dynamic prompts not updating
1. Check API is accessible
2. Verify cache TTL (default 5 min)
3. Check API logs for errors
4. Test API endpoint directly

### Database connection errors
1. Check DATABASE_URL format
2. Verify PostgreSQL is running
3. Test connection: `psql $DATABASE_URL`
4. Check firewall rules

---

## ✅ Go-Live Checklist

### Final Checks
- [ ] All tests pass
- [ ] Documentation complete
- [ ] Team trained
- [ ] Rollback plan ready
- [ ] Monitoring configured
- [ ] Backups configured

### Launch
- [ ] Switch DNS (if needed)
- [ ] Update webhook URLs
- [ ] Announce to users
- [ ] Monitor closely for 24h

### Post-Launch
- [ ] Monitor error rates
- [ ] Collect user feedback
- [ ] Fix critical issues ASAP
- [ ] Schedule retrospective

---

## 📞 Support Contacts

**Technical Issues:**
- Check logs first
- Review documentation
- Contact: [your-email]

**Telegram API Issues:**
- https://core.telegram.org/bots/api
- https://t.me/BotSupport

**Aiogram Issues:**
- https://docs.aiogram.dev/
- https://github.com/aiogram/aiogram

---

## 🎉 Success Criteria

Your deployment is successful if:
- ✅ All city bots respond to `/start`
- ✅ Product search works
- ✅ Manager escalation works
- ✅ Ticket creation works
- ✅ No errors in logs
- ✅ Webhook status is healthy
- ✅ Dynamic prompts update correctly

---

**Ready to deploy?** Start from the top and check off each item!

**Last updated:** 2026-02-17
