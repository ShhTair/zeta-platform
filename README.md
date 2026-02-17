# ZETA Platform

Multi-city e-commerce platform with Telegram bot, API backend, and web frontend.

## Project Structure

```
zeta-platform/
├── apps/
│   ├── bot/          # Telegram bot (Aiogram 3.x + webhook)
│   ├── api/          # FastAPI backend (TODO)
│   └── web/          # Next.js frontend (TODO)
├── packages/
│   └── shared/       # Shared types and utilities (TODO)
└── README.md
```

## Components

### 1. Telegram Bot (`apps/bot/`)

Multi-city Telegram bot with:
- Webhook mode (production-ready)
- Dynamic prompts from database
- Product catalog search
- Manager escalation (Telegram tag + Bitrix CRM)
- Docker deployment

**Status:** ✅ Complete

See [apps/bot/README.md](apps/bot/README.md) for details.

### 2. API Backend (`apps/api/`)

FastAPI backend providing:
- City configuration management
- Product catalog API
- Dynamic prompts storage
- Bitrix CRM integration

**Status:** 🚧 TODO

### 3. Web Frontend (`apps/web/`)

Next.js admin panel for:
- City management
- Product catalog CRUD
- Prompt editor
- Analytics dashboard

**Status:** 🚧 TODO

## Quick Start

### Bot Development

```bash
cd apps/bot

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your bot token

# Run with ngrok for local testing
ngrok http 8080
# Update WEBHOOK_URL in .env

# Start bot
python main.py
```

### Docker Deployment

```bash
cd apps/bot

# Build
docker build -t zeta-bot .

# Run
docker run -d \
  --name zeta-bot-moscow \
  --env-file .env \
  -p 8080:8080 \
  zeta-bot
```

## Environment Variables

### Bot (`apps/bot/.env`)

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
CITY_ID=moscow
API_URL=http://localhost:8000
WEBHOOK_URL=https://your-domain.com
HOST=0.0.0.0
PORT=8080
```

## Multi-City Architecture

Each city has:
- Separate bot instance (unique BOT_TOKEN)
- Own configuration (manager, prompts, catalog)
- Independent deployment

Example: Moscow + SPB:
```bash
# Moscow bot on port 8080
docker run -d -p 8080:8080 -e CITY_ID=moscow zeta-bot

# SPB bot on port 8081
docker run -d -p 8081:8080 -e CITY_ID=spb zeta-bot
```

## API Design (TODO)

```
GET  /api/cities                      # List cities
GET  /api/cities/{id}/config          # Get city config
POST /api/cities                      # Create city
PUT  /api/cities/{id}/config          # Update config

GET  /api/cities/{id}/prompts         # Get prompts (hot-reload)
PUT  /api/cities/{id}/prompts         # Update prompts

GET  /api/products/search             # Search products
GET  /api/products/{id}               # Get product
POST /api/products                    # Create product

POST /api/bitrix/deals                # Create Bitrix CRM deal
```

## Roadmap

- [x] Telegram bot with webhook
- [x] Dynamic prompt loading
- [x] Product search
- [x] Manager escalation
- [x] Bitrix integration
- [x] Docker deployment
- [ ] FastAPI backend
- [ ] Database schema (PostgreSQL)
- [ ] Admin web panel
- [ ] Analytics dashboard
- [ ] Multi-language support

## Tech Stack

- **Bot:** Python 3.11, Aiogram 3.x, aiohttp
- **API:** FastAPI, SQLAlchemy, PostgreSQL (planned)
- **Web:** Next.js, React, TailwindCSS (planned)
- **Deployment:** Docker, Nginx, SSL

## License

Proprietary - ZETA Platform
