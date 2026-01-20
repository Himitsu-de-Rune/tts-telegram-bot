"""Configuration management."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration."""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # TTS Provider
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "OSS").upper()
    
    # Yandex TTS
    YANDEX_API_KEY: str = os.getenv("YANDEX_API_KEY", "")
    YANDEX_FOLDER_ID: Optional[str] = os.getenv("YANDEX_FOLDER_ID")
    
    # Sber TTS
    SBER_API_KEY: str = os.getenv("SBER_API_KEY", "")
    SBER_CLIENT_ID: Optional[str] = os.getenv("SBER_CLIENT_ID")
    
    # Audio Converter
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    
    # Telegram Webhook (optional)
    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "8443"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        if cls.TTS_PROVIDER == "YANDEX":
            if not cls.YANDEX_API_KEY:
                errors.append("YANDEX_API_KEY is required when TTS_PROVIDER=YANDEX")
            if not cls.YANDEX_FOLDER_ID:
                errors.append("YANDEX_FOLDER_ID is required when TTS_PROVIDER=YANDEX (обязателен для API-ключа)")
        
        if cls.TTS_PROVIDER == "SBER" and not cls.SBER_API_KEY:
            errors.append("SBER_API_KEY is required when TTS_PROVIDER=SBER")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    @classmethod
    def get_tts_provider_config(cls) -> dict:
        """Get TTS provider configuration based on TTS_PROVIDER."""
        if cls.TTS_PROVIDER == "YANDEX":
            return {
                "api_key": cls.YANDEX_API_KEY,
                "folder_id": cls.YANDEX_FOLDER_ID
            }
        elif cls.TTS_PROVIDER == "SBER":
            return {
                "api_key": cls.SBER_API_KEY,
                "client_id": cls.SBER_CLIENT_ID
            }
        elif cls.TTS_PROVIDER == "OSS":
            return {}
        else:
            raise ValueError(f"Unknown TTS_PROVIDER: {cls.TTS_PROVIDER}")
