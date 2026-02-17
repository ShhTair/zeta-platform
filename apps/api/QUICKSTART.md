# ZETA Platform API - Quick Start Guide

Get the API running in 5 minutes!

## Prerequisites

- Python 3.11 or 3.12
- PostgreSQL (already running on your system)

## Step 1: Setup Environment

```bash
cd /home/tair/.openclaw/workspace/zeta-platform/apps/api

# Virtual environment already created with Python 3.12
source venv/bin/activate
```

## Step 2: Configure Database

Your `.env` file is already configured to use the system PostgreSQL:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/zeta_platform
```

**Create the database:**

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Inside psql:
CREATE DATABASE zeta_platform;
\q
```

Or if you have a postgres user password set:

```bash
psql -U postgres -c "CREATE DATABASE zeta_platform;"
```

## Step 3: Run Migrations

```bash
# Apply database schema
alembic upgrade head
```

## Step 4: Create Super Admin

```bash
# Run initialization script
python init_db.py

# Use defaults:
# Email: admin@zeta.local
# Password: admin123
```

## Step 5: Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 6: Test It!

Open your browser:

- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

Or use the test script:

```bash
# In another terminal
python test_api.py
```

## Using the API

### 1. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@zeta.local", "password": "admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 2. Create a City

```bash
TOKEN="your_token_here"

curl -X POST http://localhost:8000/cities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tel Aviv",
    "slug": "tel-aviv",
    "is_active": true
  }'
```

### 3. Configure Bot

```bash
curl -X PUT http://localhost:8000/cities/1/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt": "You are a helpful shopping assistant",
    "greeting_message": "Welcome! How can I help you today?",
    "manager_contact": "@admin",
    "escalation_action": "notify"
  }'
```

### 4. Add Products

```bash
curl -X POST http://localhost:8000/cities/1/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pizza Margherita",
    "description": "Classic Italian pizza with tomato and mozzarella",
    "price": 45.00,
    "stock": 100,
    "sku": "PIZZA-001"
  }'
```

### 5. View Analytics

```bash
curl -X GET "http://localhost:8000/cities/1/analytics?days=7" \
  -H "Authorization: Bearer $TOKEN"
```

## Using Swagger UI

The easiest way to test the API:

1. Go to http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Login to get token: `/auth/login` → Execute
4. Copy the `access_token` from response
5. Paste into "Value" field in Authorize dialog: `Bearer YOUR_TOKEN`
6. Click "Authorize" then "Close"
7. Now you can test all endpoints with the 🔓 icon

## Troubleshooting

### Database Error

```
FATAL: database "zeta_platform" does not exist
```

**Fix:** Create the database (see Step 2)

### Port Already in Use

```
Address already in use: 0.0.0.0:8000
```

**Fix:** Change port or kill existing process:

```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or kill existing
lsof -ti:8000 | xargs kill -9
```

### Import Errors

```
ModuleNotFoundError: No module named 'app'
```

**Fix:** Make sure virtual environment is activated:

```bash
source venv/bin/activate
```

### Migration Error

```
Can't locate revision identified by '001'
```

**Fix:** Mark current version:

```bash
alembic stamp head
```

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture overview
- Explore the API at http://localhost:8000/docs
- Create additional cities, products, and bot configs
- Integrate with your Telegram bot frontend

## Using Make Commands

If you prefer shortcuts:

```bash
make install    # Install dependencies
make setup      # Full setup (creates DB, runs migrations, creates admin)
make dev        # Run development server
make test       # Run tests
make clean      # Clean temporary files
```

---

**You're all set! 🚀**

The ZETA Platform API is now running and ready for integration.
