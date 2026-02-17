# ZETA Platform API

Multi-tenant bot management platform with authentication, role-based access control, and analytics.

## Features

- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access Control** - Super Admin, City Admin, and Viewer roles
- **Multi-Tenancy** - Isolated data per city
- **Bot Configuration** - Manage bot settings per city
- **Product Management** - CRUD operations for products and categories
- **Analytics** - Conversation and message analytics
- **Audit Logging** - Track all changes to critical data
- **Health Check** - Monitor API and database status

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **JWT** - Token-based authentication
- **Bcrypt** - Password hashing
- **Redis** - (Optional) Caching

## Project Structure

```
api/
├── app/
│   ├── core/           # Configuration, database, security
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routes/         # API endpoints
│   ├── dependencies/   # Auth & access control
│   ├── middleware/     # Audit logging
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
│   └── versions/       # Migration files
├── tests/              # Test files
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
└── README.md           # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11 or 3.12
- PostgreSQL 12+
- Redis (optional, for caching)

### 2. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS (Homebrew):**
```bash
brew install postgresql@16
brew services start postgresql@16
```

### 3. Create Database

```bash
# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE zeta_platform;
CREATE USER zeta_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE zeta_platform TO zeta_user;
\q
```

### 4. Setup Python Environment

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 5. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

Update these values in `.env`:
```env
DATABASE_URL=postgresql://zeta_user:your_secure_password@localhost:5432/zeta_platform
SECRET_KEY=generate-a-secure-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

To generate a secure SECRET_KEY:
```bash
openssl rand -hex 32
```

### 6. Run Database Migrations

```bash
# Apply migrations
alembic upgrade head
```

### 7. Create Initial Super Admin User

```bash
# Start Python REPL
python3

# Run this code:
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email="admin@zeta.local",
    password_hash=get_password_hash("admin123"),
    role=UserRole.SUPER_ADMIN
)
db.add(admin)
db.commit()
print(f"Created admin user: {admin.email}")
db.close()
exit()
```

### 8. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

### 9. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/logout` - Logout
- `GET /auth/me` - Get current user info

### Cities (Super Admin)

- `GET /cities` - List all cities
- `POST /cities` - Create new city
- `GET /cities/{id}` - Get city by ID
- `PUT /cities/{id}` - Update city
- `DELETE /cities/{id}` - Delete city

### Bot Configuration

- `GET /cities/{id}/config` - Get bot config
- `PUT /cities/{id}/config` - Update bot config

### Products

- `GET /cities/{id}/products` - List products
- `POST /cities/{id}/products` - Create product
- `GET /cities/{id}/products/{product_id}` - Get product
- `PUT /cities/{id}/products/{product_id}` - Update product
- `DELETE /cities/{id}/products/{product_id}` - Delete product

### Analytics

- `GET /cities/{id}/analytics` - Get city analytics

### Audit Logs

- `GET /cities/{id}/audit-logs` - Get audit logs

### Health Check

- `GET /health` - API and database health status

## Testing the API

### 1. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@zeta.local",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 2. Create a City (Super Admin)

```bash
curl -X POST http://localhost:8000/cities \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Tel Aviv",
    "slug": "tel-aviv",
    "is_active": true
  }'
```

### 3. Get Bot Configuration

```bash
curl -X GET http://localhost:8000/cities/1/config \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Create a Product

```bash
curl -X POST http://localhost:8000/cities/1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Pizza Margherita",
    "description": "Classic Italian pizza",
    "price": 45.00,
    "stock": 100,
    "sku": "PIZZA-001"
  }'
```

## Database Schema

### Tables

- **users** - User accounts with roles
- **sessions** - JWT session tracking (optional)
- **cities** - Multi-tenant cities
- **city_admins** - City admin assignments
- **bot_configs** - Bot configuration per city
- **categories** - Product categories (hierarchical)
- **products** - Products per city
- **conversations** - Chat conversations
- **messages** - Chat messages
- **audit_logs** - Change tracking

### Roles

- **SUPER_ADMIN** - Full access to all cities and system
- **CITY_ADMIN** - Manage specific cities
- **VIEWER** - Read-only access

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Creating New Migrations

```bash
# Generate migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Style

```bash
# Install formatters
pip install black isort

# Format code
black app/
isort app/
```

## Production Deployment

### Environment Variables

Set these in production:

- Use a strong, random `SECRET_KEY`
- Set `DATABASE_URL` to production database
- Configure `CORS_ORIGINS` for your frontend domains
- Use Redis for caching in production

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.zeta.local;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use strong SECRET_KEY** - Generate with `openssl rand -hex 32`
3. **Enable HTTPS in production** - Use Let's Encrypt
4. **Rotate JWT secrets regularly**
5. **Use environment variables** - Never hardcode credentials
6. **Enable rate limiting** - Protect against brute force
7. **Regular database backups**
8. **Monitor audit logs** - Track suspicious activity

## Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: connection failed
```

**Solution:** Check PostgreSQL is running and DATABASE_URL is correct.

```bash
sudo systemctl status postgresql
```

### Migration Error

```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxx'
```

**Solution:** Reset migrations or check alembic_version table.

```bash
alembic stamp head
```

### Import Errors

```
ModuleNotFoundError: No module named 'app'
```

**Solution:** Ensure you're in the correct directory and virtual environment is activated.

```bash
cd /path/to/api
source venv/bin/activate
```

## License

MIT

## Support

For issues and questions, please open an issue on GitHub or contact the development team.
