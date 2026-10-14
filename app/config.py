"""
Configuration handling using Pydantic BaseSettings.
All secrets are loaded from environment variables.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Core FastAPI settings
    APP_NAME: str = "Telemetry Service"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # JWT settings
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Misc
    ALLOWED_USERS: dict[str, str] = Field(
        default_factory=lambda: {"admin": "admin123"},
        description="Mapping of username -> password for demo purposes.",
    )

    @validator("LOG_LEVEL")
    def _validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cache settings instance for the lifetime of the process."""
    return Settings()
