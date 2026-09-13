"""
Configuration management using Pydantic Settings.
Loads configuration from environment variables or .env file.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings definition."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Telegram Bot Settings
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram Bot API Token")
    ALLOWED_USER_IDS: List[int] = Field(
        default_factory=list,
        description="List of Telegram User IDs allowed to access Jarvis"
    )

    # OpenAI Settings
    OPENAI_API_KEY: str = Field(..., description="OpenAI API Key")
    OPENAI_MODEL: str = Field(default="gpt-4o", description="OpenAI LLM Model name")
    OPENAI_STT_MODEL: str = Field(default="whisper-1", description="OpenAI Audio Transcription Model")
    OPENAI_TTS_MODEL: str = Field(default="tts-1", description="OpenAI Text-to-Speech Model")
    OPENAI_TTS_VOICE: str = Field(default="alloy", description="OpenAI TTS Voice persona")

    # Jarvis System Configuration
    SYSTEM_PROMPT: str = Field(
        default=(
            "You are Jarvis, a highly intelligent, efficient, and sophisticated personal AI assistant. "
            "You provide clear, concise, accurate, and helpful responses. Maintain a professional, polite, "
            "and slightly refined tone."
        ),
        description="System prompt for Jarvis"
    )
    MAX_CONTEXT_MESSAGES: int = Field(default=20, description="Max conversation history depth per user")
    RATE_LIMIT_PER_MINUTE: int = Field(default=15, description="Max messages per minute per user")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging output level")

    @field_validator("ALLOWED_USER_IDS", mode="before")
    @classmethod
    def parse_allowed_user_ids(cls, value: object) -> List[int]:
        """Parses comma-separated string or list of integers for allowed user IDs."""
        if isinstance(value, str):
            if not value.strip():
                return []
            return [int(uid.strip()) for uid in value.split(",") if uid.strip()]
        if isinstance(value, list):
            return [int(uid) for uid in value]
        return []


settings = Settings()
