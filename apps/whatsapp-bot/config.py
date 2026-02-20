"""
Configuration Management for WhatsApp Bot
Loads from .env and provides typed settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # WhatsApp Business API
    whatsapp_token: str
    whatsapp_phone_number_id: str
    whatsapp_verify_token: str
    whatsapp_business_account_id: str
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    
    # API Backend
    api_url: str = "http://localhost:8000"
    city_id: int = 1
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    webhook_url: str
    
    # Rate Limiting
    rate_limit_messages: int = 20
    rate_limit_window_seconds: int = 60
    
    # Features
    enable_voice_transcription: bool = True
    enable_price_alerts: bool = True
    enable_order_tracking: bool = False
    enable_saved_searches: bool = True
    
    # Language
    default_language: str = "ru"
    supported_languages: List[str] = ["ru", "kz"]
    
    # Session Management
    session_timeout_seconds: int = 86400  # 24 hours
    max_conversation_history: int = 20
    
    # Logging
    log_level: str = "INFO"
    sentry_dsn: str = ""
    
    # Admin Integration
    admin_api_url: str = "http://localhost:8000"
    admin_api_key: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()


# Webhook path
WEBHOOK_PATH = f"/webhook/whatsapp"


# WhatsApp Cloud API Endpoints
WHATSAPP_API_BASE = f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}"
WHATSAPP_MESSAGES_ENDPOINT = f"{WHATSAPP_API_BASE}/messages"
WHATSAPP_MEDIA_ENDPOINT = f"{WHATSAPP_API_BASE}/media"


__all__ = ["settings", "WEBHOOK_PATH", "WHATSAPP_MESSAGES_ENDPOINT", "WHATSAPP_MEDIA_ENDPOINT"]
