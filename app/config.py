"""Application configuration using Pydantic BaseSettings."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseSettings
    SettingsConfigDict = None

from pydantic import Field

try:
    from pydantic import field_validator
    def custom_validator(field_name):
        return field_validator(field_name, mode="before")
except ImportError:
    from pydantic import validator as custom_validator


class Settings(BaseSettings):
    """Settings are loaded from environment variables or a `.env` file."""

    APP_NAME: str = Field("Telemetry Service")
    DEBUG: bool = Field(False)
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO")
    JWT_SECRET_KEY: str = Field("basit-quantum-jwt-secret-key-institutional-2026-matrix")
    JWT_ALGORITHM: str = Field("HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60)

    @custom_validator("JWT_SECRET_KEY")
    def secret_key_must_not_be_empty(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("JWT secret key must be provided and non-empty")
        return v

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )
    else:
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cache settings instance for the lifetime of the process."""
    return Settings()
