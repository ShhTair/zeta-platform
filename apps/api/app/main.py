from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import auth, cities, bot_config, products, analytics, audit_logs, health, escalations

app = FastAPI(
    title="ZETA Platform API",
    description="Multi-tenant bot management platform with authentication and analytics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(cities.router)
app.include_router(bot_config.router)
app.include_router(products.router)
app.include_router(analytics.router)
app.include_router(escalations.router)
app.include_router(audit_logs.router)


@app.get("/")
def root():
    return {
        "message": "ZETA Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }
