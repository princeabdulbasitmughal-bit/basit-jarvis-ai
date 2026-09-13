"""Configuration management module using Pydantic Settings."""

import logging
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    telegram_bot_token: str = Field(..., description="Telegram Bot API Token")
    openai_api_key: str = Field(..., description="OpenAI API Key")
    openai_base_url: Optional[str] = Field("https://api.openai.com/v1", description="OpenAI Base URL")
    ai_model: str = Field("gpt-4o-mini", description="AI model to use for completion")
    system_prompt: str = Field(
        "You are a helpful, concise, and friendly Telegram AI assistant.",
        description="Default system prompt for the AI assistant"
    )
    max_history_messages: int = Field(20, description="Max message history length per chat")
    log_level: str = Field("INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)")


def get_settings() -> Settings:
    """Load and return application configuration settings.

    Returns:
        Settings: Validated application configuration.
    """
    try:
        return Settings()
    except Exception as err:
        logging.critical("Failed to load environment configuration: %s", err)
        raise err
