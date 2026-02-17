# ZETA Platform - Testing Guide

## Testing Checklist

### Bot Testing

#### 1. Local Webhook Test (with ngrok)

```bash
cd apps/bot

# Setup
cp .env.example .env
# Edit .env with your BOT_TOKEN

# Run test script
./test_webhook.sh

# OR manually:
ngrok http 8080
# Copy ngrok URL to .env as WEBHOOK_URL
python3 main.py
```

**Expected behavior:**
- ✅ Bot starts without errors
- ✅ Webhook is set successfully
- ✅ Bot responds to `/start` command
- ✅ Logs show incoming updates

#### 2. Test Conversation Flow

**Step 1: Greeting**
```
User: /start
Bot: 👋 [Dynamic greeting from API]
```

**Step 2: Product Inquiry**
```
User: I need a laptop
Bot: 🔍 Ищу в каталоге...
Bot: 📦 Найденные товары:
     1. Laptop X - 50000 ₽
     [🔗 Laptop X] [📞 Связаться с менеджером] [🎫 Создать заявку]
```

**Step 3: Product Link**
```
User: [clicks "🔗 Laptop X"]
Bot: 🔗 Ссылка на товар: https://shop.zeta.com/product/123
```

**Step 4: Manager Escalation**
```
User: [clicks "📞 Связаться с менеджером"]
Bot: 🔔 Новое обращение!
     👤 Клиент: @username
     🔍 Запрос: I need a laptop
     @manager_username, пожалуйста, помогите клиенту!
Bot: ✅ Менеджер уведомлен!
```

**Step 5: Ticket Creation**
```
User: [clicks "🎫 Создать заявку"]
Bot: ✅ Заявка создана!
     🎫 Номер заявки: 12345
     Наш менеджер свяжется с вами в ближайшее время.
```

#### 3. API Integration Tests

**Config Loading**
```bash
# Start API first
cd apps/api
uvicorn app.main:app --port 8000

# Check bot can fetch config
cd apps/bot
python3 -c "
import asyncio
from services.api_client import APIClient

async def test():
    client = APIClient('http://localhost:8000')
    config = await client.get_city_config('moscow')
    print('✅ Config:', config)
    await client.close()

asyncio.run(test())
"
```

**Product Search**
```bash
python3 -c "
import asyncio
from services.api_client import APIClient

async def test():
    client = APIClient('http://localhost:8000')
    products = await client.search_products('laptop', 'moscow')
    print(f'✅ Found {len(products)} products')
    await client.close()

asyncio.run(test())
"
```

#### 4. Webhook Validation

```bash
# Check webhook is set
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"

# Expected response:
{
  "ok": true,
  "result": {
    "url": "https://your-ngrok-url.ngrok.io/webhook/123456789",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40
  }
}
```

#### 5. Dynamic Prompt Hot-Reload Test

```bash
# 1. Start bot
cd apps/bot
python3 main.py

# 2. Send /start - note the greeting

# 3. Update prompt via API
curl -X PUT http://localhost:8000/api/cities/moscow/prompts \
  -H "Content-Type: application/json" \
  -d '{"greeting": "🎉 NEW GREETING!"}'

# 4. Wait 5 minutes (cache TTL) or restart bot

# 5. Send /start again - should see new greeting
```

---

### API Testing

#### 1. Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "environment": "development"}
```

#### 2. Cities Endpoints

```bash
# Get city config
curl http://localhost:8000/api/cities/moscow/config

# Expected response:
{
  "city_id": "moscow",
  "city_name": "Москва",
  "bot_token": "***",
  "manager_telegram_id": "@manager",
  "prompts": {
    "greeting": "👋 Добро пожаловать!",
    "catalog_search": "🔍 Ищу в каталоге..."
  }
}
```

#### 3. Products Endpoints

```bash
# Search products
curl "http://localhost:8000/api/products/search?q=laptop&city_id=moscow&limit=5"

# Expected: array of products
[
  {
    "id": "123",
    "name": "Laptop X",
    "price": 50000,
    "url": "https://shop.com/product/123"
  }
]
```

#### 4. Bitrix Integration

```bash
# Create deal
curl -X POST http://localhost:8000/api/bitrix/deals \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "customer_telegram": "@johndoe",
    "product_id": "123",
    "message": "Interested in laptop",
    "city_id": "moscow",
    "source": "telegram_bot"
  }'

# Expected:
{
  "success": true,
  "deal_id": "12345",
  "deal_url": "https://bitrix.ru/crm/deal/12345/"
}
```

---

### Integration Testing

#### End-to-End Test Scenario

```python
# test_e2e.py
import asyncio
from aiogram import Bot
from aiogram.types import Update, Message, User, Chat
from services.api_client import APIClient
from services.prompt_manager import PromptManager

async def test_full_flow():
    """Test complete conversation flow"""
    
    # 1. Initialize services
    api_client = APIClient("http://localhost:8000")
    prompt_manager = PromptManager(api_client, "moscow")
    await prompt_manager.load_config()
    
    # 2. Test greeting prompt
    greeting = await prompt_manager.get_prompt("greeting")
    assert greeting, "Greeting prompt should not be empty"
    print(f"✅ Greeting: {greeting[:50]}...")
    
    # 3. Test product search
    products = await api_client.search_products("laptop", "moscow")
    assert len(products) > 0, "Should find products"
    print(f"✅ Found {len(products)} products")
    
    # 4. Test Bitrix deal creation
    result = await api_client.create_bitrix_deal(
        customer_name="Test User",
        customer_telegram="@testuser",
        product_id=products[0]["id"],
        message="Test inquiry",
        city_id="moscow"
    )
    assert result["success"], "Deal creation should succeed"
    print(f"✅ Deal created: {result['deal_id']}")
    
    await api_client.close()
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
```

Run:
```bash
cd apps/bot
python3 test_e2e.py
```

---

### Load Testing

#### Simulate Multiple Users

```bash
# Install locust
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class BotUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def search_product(self):
        self.client.get("/api/products/search", params={
            "q": "laptop",
            "city_id": "moscow",
            "limit": 5
        })
    
    @task(1)
    def get_config(self):
        self.client.get("/api/cities/moscow/config")
EOF

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

Open http://localhost:8089 and configure:
- Number of users: 100
- Spawn rate: 10/sec

---

### Docker Testing

#### Build and Test Containers

```bash
# Build bot image
cd apps/bot
docker build -t zeta-bot-test .

# Run with test env
docker run --rm \
  -e BOT_TOKEN=$TEST_BOT_TOKEN \
  -e CITY_ID=test \
  -e API_URL=http://host.docker.internal:8000 \
  -e WEBHOOK_URL=https://test.ngrok.io \
  -p 8080:8080 \
  zeta-bot-test
```

#### Docker Compose Test

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f bot-moscow

# Test health
curl http://localhost:8000/health

# Stop
docker-compose down
```

---

### Performance Benchmarks

#### Expected Response Times

| Endpoint | Target | Acceptable |
|----------|--------|------------|
| GET /health | <10ms | <50ms |
| GET /api/cities/{id}/config | <100ms | <500ms |
| GET /api/products/search | <200ms | <1s |
| POST /api/bitrix/deals | <500ms | <2s |
| Bot webhook processing | <500ms | <2s |

#### Monitor Response Times

```bash
# API response time
time curl http://localhost:8000/api/cities/moscow/config

# Bot webhook latency - check logs:
# Look for: "Update processing time: 123ms"
```

---

### Security Testing

#### 1. Test Webhook Signature (if implemented)

```bash
# Telegram sends X-Telegram-Bot-Api-Secret-Token header
# Bot should validate it
```

#### 2. Test Rate Limiting

```bash
# Spam requests
for i in {1..100}; do
  curl http://localhost:8000/api/products/search?q=test &
done

# Should return 429 Too Many Requests after threshold
```

#### 3. Test SQL Injection

```bash
# Try malicious input
curl "http://localhost:8000/api/products/search?q='; DROP TABLE products; --"

# Should be safely escaped by SQLAlchemy
```

---

### Monitoring & Debugging

#### Enable Debug Logging

```python
# apps/bot/main.py
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### Test with Telegram Updates

```bash
# Send a test update to webhook
curl -X POST http://localhost:8080/webhook/123456789 \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456,
    "message": {
      "message_id": 1,
      "from": {"id": 123, "first_name": "Test"},
      "chat": {"id": 123, "type": "private"},
      "text": "/start"
    }
  }'
```

---

## Automated Testing (Future)

### Unit Tests

```python
# tests/test_prompt_manager.py
import pytest
from services.prompt_manager import PromptManager

@pytest.mark.asyncio
async def test_prompt_caching():
    # Mock API client
    # Test cache TTL
    # Test hot-reload
    pass
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd apps/bot
          pip install -r requirements.txt
          python -m pytest tests/
```

---

## Common Issues

### Issue: Webhook not receiving updates

**Debug:**
```bash
# 1. Check webhook info
curl https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo

# 2. Check if URL is accessible
curl -I $WEBHOOK_URL/webhook/$(echo $BOT_TOKEN | cut -d: -f1)

# 3. Check bot logs
docker logs zeta-bot-moscow
```

### Issue: Dynamic prompts not loading

**Debug:**
```bash
# 1. Test API connection
curl http://localhost:8000/api/cities/moscow/prompts

# 2. Check bot can reach API
docker exec zeta-bot-moscow curl http://api:8000/health

# 3. Check prompt manager cache
# Add debug logs in prompt_manager.py
```

### Issue: Bitrix deal creation fails

**Debug:**
```bash
# Test Bitrix webhook
curl -X POST $BITRIX_WEBHOOK_URL/crm.deal.add \
  -d "FIELDS[TITLE]=Test"

# Check API logs
docker logs zeta-api | grep bitrix
```

---

## Test Data Setup

```sql
-- Insert test city
INSERT INTO cities (id, name, bot_token, manager_telegram_id) 
VALUES ('test', 'Test City', '123456789:TEST', '@test_manager');

-- Insert test prompts
INSERT INTO prompts (city_id, key, value) VALUES
  ('test', 'greeting', '👋 Test Greeting'),
  ('test', 'catalog_search', '🔍 Searching...');

-- Insert test products
INSERT INTO products (id, name, price, city_id) VALUES
  ('p1', 'Test Laptop', 50000, 'test'),
  ('p2', 'Test Phone', 30000, 'test');
```

---

**Last updated:** 2026-02-17
