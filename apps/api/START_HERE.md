# 🚀 ZETA Platform API - START HERE

Welcome to the ZETA Platform FastAPI backend!

## ✅ What's Built

A complete multi-tenant bot management API with:
- JWT Authentication
- Role-Based Access Control
- Multi-Tenancy (City-based)
- Bot Configuration Management
- Product Catalog
- Analytics & Reporting
- Audit Logging
- 24 API Endpoints

## 📚 Documentation Guide

Read these files in order:

### 1. **QUICKSTART.md** ⚡
**Read this first!** Get up and running in 5 minutes.
- Setup instructions
- Database creation
- First admin user
- Testing the API

### 2. **README.md** 📖
**Complete reference** for everything:
- Full API documentation
- All endpoints explained
- Security best practices
- Deployment guide
- Troubleshooting

### 3. **PROJECT_SUMMARY.md** 🏗️
**Architecture overview**:
- Project structure
- Database schema
- Tech stack
- Design decisions

### 4. **COMPLETION_REPORT.md** ✨
**What was built**:
- Full feature list
- Statistics
- Next steps
- Enhancement ideas

## 🎯 Quick Commands

```bash
# Activate environment
source venv/bin/activate

# Create database
sudo -u postgres psql -c "CREATE DATABASE zeta_platform;"

# Run migrations
alembic upgrade head

# Create admin user
python init_db.py

# Start server
uvicorn app.main:app --reload

# Test API
python test_api.py

# Or use Swagger UI
open http://localhost:8000/docs
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application entry point |
| `.env` | Environment configuration |
| `requirements.txt` | Python dependencies |
| `alembic/versions/001_*.py` | Database migration |
| `init_db.py` | Database setup script |
| `test_api.py` | API test script |
| `Makefile` | Common commands |

## 🏃 Fastest Way to Start

### Option A: Using Makefile
```bash
make setup    # Creates DB, runs migrations, creates admin
make dev      # Starts server
```

### Option B: Manual Steps
```bash
# 1. Setup
source venv/bin/activate

# 2. Database
sudo -u postgres psql -c "CREATE DATABASE zeta_platform;"
alembic upgrade head

# 3. Admin user
python init_db.py
# Email: admin@zeta.local
# Password: admin123

# 4. Run
uvicorn app.main:app --reload
```

### Option C: Docker (PostgreSQL only)
```bash
docker compose up -d     # Start PostgreSQL & Redis
alembic upgrade head     # Run migrations
python init_db.py        # Create admin
uvicorn app.main:app --reload
```

## 🌐 Access Points

Once running:

- **API Server:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 🔑 Default Credentials

**Super Admin:**
- Email: `admin@zeta.local`
- Password: `admin123`

⚠️ **Change these in production!**

## 📦 Project Structure

```
api/
├── app/                    # Application code
│   ├── core/              # Config, database, security
│   ├── models/            # SQLAlchemy models (10 tables)
│   ├── schemas/           # Pydantic schemas
│   ├── routes/            # API endpoints (24 endpoints)
│   ├── dependencies/      # Auth dependencies
│   ├── middleware/        # Audit logging
│   └── main.py           # FastAPI app
├── alembic/               # Database migrations
├── venv/                  # Virtual environment (Python 3.12)
├── .env                   # Environment config
├── requirements.txt       # Dependencies
├── init_db.py            # DB setup script
├── test_api.py           # Test script
├── Makefile              # Common commands
├── docker-compose.yml    # Docker setup
└── *.md                  # Documentation
```

## 🎓 Learning Path

1. **Understand the Basics**
   - Read QUICKSTART.md
   - Run the setup commands
   - Test with Swagger UI

2. **Explore the Code**
   - Check `app/main.py` for routing
   - Look at `app/routes/auth.py` for auth flow
   - Review `app/models/` for database schema

3. **Test the API**
   - Use Swagger UI at `/docs`
   - Try example curl commands from README
   - Run `test_api.py` script

4. **Customize**
   - Modify bot configurations
   - Add new endpoints
   - Extend database models

## 🔧 Common Tasks

### Add a New City
```bash
# Via Swagger UI at /docs:
# 1. Login with admin credentials
# 2. POST /cities with {"name": "City Name", "slug": "city-slug"}
```

### Add Products
```bash
# POST /cities/{id}/products
# Requires city admin access
```

### View Analytics
```bash
# GET /cities/{id}/analytics?days=7
# Shows conversation stats
```

### Check Audit Logs
```bash
# GET /cities/{id}/audit-logs
# Track all changes
```

## 🐛 Troubleshooting

### Can't Connect to Database?
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify database exists
psql -U postgres -l | grep zeta_platform
```

### Import Errors?
```bash
# Make sure venv is activated
source venv/bin/activate

# Check you're in correct directory
pwd
# Should show: .../zeta-platform/apps/api
```

### Port 8000 Already in Use?
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

## 💡 Tips

- **Use Swagger UI** (`/docs`) for testing - it's the easiest way
- **Check logs** - Uvicorn shows all requests and errors
- **Read error messages** - They're usually very helpful
- **Start simple** - Test auth → cities → products in that order
- **Use the Makefile** - It has shortcuts for common tasks

## 🎯 Next Steps After Setup

1. **Test the Default Endpoints**
   - Login with admin account
   - Create a test city
   - Add some products
   - Check analytics

2. **Customize for Your Needs**
   - Update bot configurations
   - Add more product fields
   - Customize escalation logic

3. **Integrate with Frontend**
   - Use the JWT token from `/auth/login`
   - Call API endpoints from your bot
   - Handle errors appropriately

4. **Deploy to Production**
   - Update `.env` with production settings
   - Use strong SECRET_KEY
   - Set up HTTPS
   - Enable monitoring

## 📞 Getting Help

1. **Check Documentation**
   - README.md has detailed info
   - Swagger UI shows all endpoints
   - Code has comments

2. **Common Issues**
   - Database connection → Check PostgreSQL
   - Import errors → Activate venv
   - Auth failures → Check token expiration

3. **Debug Mode**
   ```bash
   # Run with debug output
   uvicorn app.main:app --reload --log-level debug
   ```

## ✨ Features at a Glance

- ✅ JWT Authentication
- ✅ Multi-Tenant (Cities)
- ✅ Bot Configuration
- ✅ Product Management
- ✅ Analytics Dashboard
- ✅ Audit Logging
- ✅ Health Monitoring
- ✅ OpenAPI Docs
- ✅ CORS Support
- ✅ Role-Based Access

## 🎉 You're Ready!

Everything is set up and ready to go. Choose your starting point:

- **Quick Test?** → Run `make setup && make dev`
- **Learn First?** → Read QUICKSTART.md
- **Deep Dive?** → Read README.md
- **Just Try It?** → Visit http://localhost:8000/docs

**Happy coding! 🚀**
