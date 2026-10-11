"""
Configuration module using Pydantic BaseSettings.
Loads environment variables and provides type‑safe settings.
"""

import os
from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """
    Application settings.
    """

    # FastAPI settings
    APP_NAME: str = "Telemetry Microservice"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # JWT settings
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("LOG_LEVEL")
    def _validate_log_level(cls, v: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
        if v.upper() not in allowed:
            raise ValueError(f"Invalid LOG_LEVEL: {v}")
        return v.upper()


def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    # Pydantic caches the instance after first call
    return Settings()
