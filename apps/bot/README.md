# ZETA Telegram Bot

Multi-city Telegram bot with webhook support and dynamic prompts from database.

## Features

- ✅ **Webhook mode** (no polling) for production deployment
- ✅ **Multi-city support** - each city has its own bot token and config
- ✅ **Dynamic prompts** - hot-reloadable from API/database
- ✅ **Product catalog search** via API
- ✅ **Manager escalation** - tag Telegram manager or create Bitrix CRM ticket
- ✅ **Dockerized** and ready for deployment

## Architecture

```
bot/
├── main.py              # Entry point, webhook setup
├── handlers/
│   ├── start.py         # /start command, greeting
│   ├── product_inquiry.py  # Product search and display
│   └── escalation.py    # Manager tagging and ticket creation
├── services/
│   ├── api_client.py    # API client for config/catalog/Bitrix
│   └── prompt_manager.py  # Dynamic prompt loading with cache
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Conversation Flow

1. **Greeting** - User starts with `/start`, receives dynamic greeting
2. **Product Inquiry** - User asks about products, bot searches catalog
3. **Product Display** - Show results with inline buttons
4. **Escalation Options**:
   - 🔗 Send product link
   - 📞 Tag manager in Telegram
   - 🎫 Create Bitrix CRM ticket

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
CITY_ID=moscow
API_URL=http://localhost:8000
WEBHOOK_URL=https://your-domain.com
HOST=0.0.0.0
PORT=8080
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Local Testing with ngrok

```bash
# Start ngrok
ngrok http 8080

# Update .env with ngrok URL
WEBHOOK_URL=https://abc123.ngrok-free.app

# Run bot
python main.py
```

### 4. Docker Deployment

```bash
# Build image
docker build -t zeta-bot .

# Run container
docker run -d \
  --name zeta-bot-moscow \
  --env-file .env \
  -p 8080:8080 \
  zeta-bot
```

## API Endpoints

The bot expects the following API endpoints:

### Get City Config
```
GET /api/cities/{city_id}/config

Response:
{
  "city_id": "moscow",
  "city_name": "Москва",
  "bot_token": "...",
  "manager_telegram_id": "@manager_username",
  "prompts": {
    "greeting": "👋 Добро пожаловать...",
    "product_inquiry": "Что вас интересует?",
    "catalog_search": "🔍 Ищу в каталоге...",
    "no_results": "😔 Ничего не найдено..."
  },
  "bitrix_endpoint": "https://your-bitrix.ru/rest/..."
}
```

### Search Products
```
GET /api/products/search?q=query&city_id=moscow&limit=5

Response:
[
  {
    "id": "123",
    "name": "Product Name",
    "description": "...",
    "price": 1000,
    "url": "https://shop.com/product/123"
  }
]
```

### Get Dynamic Prompts (Hot Reload)
```
GET /api/cities/{city_id}/prompts

Response:
{
  "greeting": "Updated greeting...",
  "catalog_search": "Searching..."
}
```

### Create Bitrix Deal
```
POST /api/bitrix/deals

Body:
{
  "customer_name": "John Doe",
  "customer_telegram": "@johndoe",
  "product_id": "123",
  "message": "Customer inquiry...",
  "city_id": "moscow",
  "source": "telegram_bot"
}

Response:
{
  "success": true,
  "deal_id": "12345",
  "deal_url": "https://bitrix.ru/crm/deal/12345/"
}
```

## Multi-City Deployment

Each city runs as a separate bot instance with its own token:

```bash
# Moscow
docker run -d --name zeta-bot-moscow \
  -e BOT_TOKEN=$MOSCOW_BOT_TOKEN \
  -e CITY_ID=moscow \
  -e WEBHOOK_URL=https://bot.zeta.com \
  -p 8080:8080 zeta-bot

# St. Petersburg
docker run -d --name zeta-bot-spb \
  -e BOT_TOKEN=$SPB_BOT_TOKEN \
  -e CITY_ID=spb \
  -e WEBHOOK_URL=https://bot.zeta.com \
  -p 8081:8080 zeta-bot
```

## Dynamic Prompts

Prompts are cached for 5 minutes (configurable in `prompt_manager.py`).
To update prompts:

1. Change prompts in database
2. Bot will automatically reload on next request (after cache TTL)
3. No bot restart required! 🔥

## Logging

All events are logged:
- User interactions (start, search, escalation)
- API calls (config, catalog, Bitrix)
- Errors and warnings

Check logs:
```bash
docker logs -f zeta-bot-moscow
```

## Testing Checklist

- [ ] `/start` command shows greeting
- [ ] Product search returns results
- [ ] Inline buttons work (product links)
- [ ] Manager tagging works (correct username)
- [ ] Bitrix ticket creation succeeds
- [ ] Webhook receives messages
- [ ] Dynamic prompts reload after TTL
- [ ] Multi-city config loads correctly

## Production Deployment

1. Set up reverse proxy (Nginx) to forward `/webhook/*` to bot instances
2. Configure SSL certificate (required by Telegram)
3. Set environment variables securely (Docker secrets, Kubernetes ConfigMap)
4. Monitor logs and errors
5. Scale horizontally if needed (one instance per city)

## License

Proprietary - ZETA Platform
