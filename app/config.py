"""Application configuration using Pydantic BaseSettings."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Settings are loaded from environment variables or a `.env` file."""

    APP_NAME: str = Field("Telemetry Service", env="APP_NAME")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        "INFO", env="LOG_LEVEL"
    )
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    # Add any other settings (e.g., DB URLs) here.

    @validator("JWT_SECRET_KEY")
    def secret_key_must_not_be_empty(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("JWT secret key must be provided and non‑empty")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cache settings instance for the lifetime of the process."""
    return Settings()
