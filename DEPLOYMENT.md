# ZETA Platform - Deployment Guide

## Architecture Overview

```
┌─────────────────┐
│  Telegram User  │
└────────┬────────┘
         │
         │ (webhook)
         ▼
┌─────────────────┐      ┌──────────────┐
│   Bot Instance  │─────▶│  FastAPI     │
│   (Aiogram 3.x) │      │  Backend     │
│                 │◀─────│              │
│  Port: 8080+    │      │  Port: 8000  │
└─────────────────┘      └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  PostgreSQL  │
                         │  Database    │
                         └──────────────┘
```

## Components

### 1. Bot (`apps/bot/`)
- **Framework:** Aiogram 3.x with webhook
- **Port:** 8080 (configurable per city)
- **Features:**
  - Dynamic prompts from API
  - Product catalog search
  - Manager escalation
  - Bitrix CRM integration

### 2. API (`apps/api/`)
- **Framework:** FastAPI
- **Port:** 8000
- **Database:** PostgreSQL
- **Features:**
  - City configuration management
  - Product catalog
  - Dynamic prompts storage
  - Bitrix integration

### 3. Web (`apps/web/`)
- **Framework:** Next.js (status: TODO)
- **Port:** 3000
- **Features:** Admin dashboard

---

## Quick Start (Local Development)

### 1. Start API Backend

```bash
cd apps/api

# Setup environment
cp .env.example .env
# Edit .env with database credentials

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload --port 8000
```

### 2. Start Bot with ngrok

```bash
cd apps/bot

# Setup environment
cp .env.example .env
# Edit .env:
#   BOT_TOKEN=your_bot_token
#   CITY_ID=moscow
#   API_URL=http://localhost:8000

# Install dependencies
pip install -r requirements.txt

# Run test script (includes ngrok)
./test_webhook.sh

# OR manually:
# 1. Start ngrok: ngrok http 8080
# 2. Update WEBHOOK_URL in .env
# 3. Run: python main.py
```

---

## Production Deployment

### Prerequisites

- Docker & Docker Compose
- PostgreSQL database
- Domain with SSL certificate (required by Telegram)
- Nginx as reverse proxy

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb zeta_platform

# Run migrations
cd apps/api
alembic upgrade head
```

### 2. Deploy API Backend

```bash
cd apps/api

# Build Docker image
docker build -t zeta-api .

# Run container
docker run -d \
  --name zeta-api \
  -e DATABASE_URL=postgresql://user:pass@host/zeta_platform \
  -e SECRET_KEY=your_secret_key \
  -p 8000:8000 \
  zeta-api
```

### 3. Deploy Bot Instances (Multi-City)

Each city runs a separate bot instance:

```bash
cd apps/bot

# Build image
docker build -t zeta-bot .

# Moscow bot
docker run -d \
  --name zeta-bot-moscow \
  -e BOT_TOKEN=123456789:ABCdef... \
  -e CITY_ID=moscow \
  -e API_URL=http://zeta-api:8000 \
  -e WEBHOOK_URL=https://bot.zeta.com \
  -p 8080:8080 \
  zeta-bot

# St. Petersburg bot
docker run -d \
  --name zeta-bot-spb \
  -e BOT_TOKEN=987654321:XYZabc... \
  -e CITY_ID=spb \
  -e API_URL=http://zeta-api:8000 \
  -e WEBHOOK_URL=https://bot.zeta.com \
  -p 8081:8080 \
  zeta-bot

# Kazan bot
docker run -d \
  --name zeta-bot-kazan \
  -e BOT_TOKEN=111222333:QWErty... \
  -e CITY_ID=kazan \
  -e API_URL=http://zeta-api:8000 \
  -e WEBHOOK_URL=https://bot.zeta.com \
  -p 8082:8080 \
  zeta-bot
```

### 4. Nginx Configuration

```nginx
# /etc/nginx/sites-available/zeta-bot

upstream api_backend {
    server localhost:8000;
}

server {
    listen 443 ssl http2;
    server_name bot.zeta.com;

    ssl_certificate /etc/letsencrypt/live/bot.zeta.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.zeta.com/privkey.pem;

    # API endpoint
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Moscow bot webhook
    location /webhook/123456789 {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # SPB bot webhook
    location /webhook/987654321 {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Kazan bot webhook
    location /webhook/111222333 {
        proxy_pass http://localhost:8082;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. SSL Setup (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d bot.zeta.com

# Auto-renewal is configured automatically
```

---

## Docker Compose (Recommended)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: zeta
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: zeta_platform
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build: ./apps/api
    environment:
      DATABASE_URL: postgresql://zeta:${DB_PASSWORD}@postgres/zeta_platform
      SECRET_KEY: ${API_SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  bot-moscow:
    build: ./apps/bot
    environment:
      BOT_TOKEN: ${MOSCOW_BOT_TOKEN}
      CITY_ID: moscow
      API_URL: http://api:8000
      WEBHOOK_URL: https://bot.zeta.com
    ports:
      - "8080:8080"
    depends_on:
      - api

  bot-spb:
    build: ./apps/bot
    environment:
      BOT_TOKEN: ${SPB_BOT_TOKEN}
      CITY_ID: spb
      API_URL: http://api:8000
      WEBHOOK_URL: https://bot.zeta.com
    ports:
      - "8081:8080"
    depends_on:
      - api

volumes:
  postgres_data:
```

Start all services:

```bash
docker-compose up -d
```

---

## Environment Variables

### API (`apps/api/.env`)

```env
DATABASE_URL=postgresql://user:password@localhost/zeta_platform
SECRET_KEY=your-secret-key-min-32-chars
BITRIX_WEBHOOK_URL=https://your-bitrix.ru/rest/123/abc/
```

### Bot (`apps/bot/.env`)

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
CITY_ID=moscow
API_URL=http://localhost:8000
WEBHOOK_URL=https://bot.zeta.com
HOST=0.0.0.0
PORT=8080
```

---

## Monitoring & Logs

### View Logs

```bash
# Docker logs
docker logs -f zeta-bot-moscow
docker logs -f zeta-api

# Docker Compose logs
docker-compose logs -f bot-moscow
docker-compose logs -f api
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Bot webhook info
curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
```

---

## Scaling

### Horizontal Scaling (Multiple Cities)

Each city = separate bot instance:
- Unique BOT_TOKEN per city
- Different port per instance
- Nginx routes webhooks by bot token

### Vertical Scaling

- Increase container resources
- Optimize database queries
- Add Redis cache for prompts

---

## Security Checklist

- [ ] Use SSL/TLS for webhook (required by Telegram)
- [ ] Store secrets in environment variables, not code
- [ ] Use Docker secrets in production
- [ ] Restrict database access (firewall)
- [ ] Enable Nginx rate limiting
- [ ] Rotate API keys regularly
- [ ] Monitor failed authentication attempts
- [ ] Keep dependencies updated

---

## Troubleshooting

### Bot not receiving messages

1. Check webhook status:
   ```bash
   curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
   ```

2. Verify SSL certificate is valid
3. Check nginx logs: `tail -f /var/log/nginx/error.log`
4. Verify webhook URL matches nginx config

### Database connection errors

1. Check DATABASE_URL format
2. Verify PostgreSQL is running
3. Test connection: `psql $DATABASE_URL`

### Dynamic prompts not loading

1. Check API is accessible from bot container
2. Verify city_id exists in database
3. Check API logs for errors

---

## Maintenance

### Update Prompts (No Restart!)

```bash
# Via API
curl -X PUT http://localhost:8000/api/cities/moscow/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "greeting": "New greeting message!",
    "catalog_search": "Searching..."
  }'

# Bot will auto-reload after cache TTL (5 minutes)
```

### Database Migrations

```bash
cd apps/api

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Backup Database

```bash
pg_dump -U zeta zeta_platform > backup_$(date +%Y%m%d).sql

# Restore
psql -U zeta zeta_platform < backup_20260217.sql
```

---

## Performance Optimization

1. **Enable Redis caching** for prompts (reduce API calls)
2. **Database indexing** on frequently queried fields
3. **CDN** for product images
4. **Connection pooling** in API
5. **Async/await** throughout (already implemented)

---

## Support

- Bot issues: Check `apps/bot/README.md`
- API issues: Check `apps/api/README.md`
- Telegram Bot API: https://core.telegram.org/bots/api
- Aiogram docs: https://docs.aiogram.dev/

---

**Last updated:** 2026-02-17
