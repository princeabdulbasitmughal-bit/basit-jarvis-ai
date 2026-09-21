"""
Configuration management using Pydantic Settings.
"""

from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings(BaseSettings):
    """Application settings and environment configuration."""

    model_config = SettingsConfigDict(
        env_prefix="FIB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Fibonacci Enterprise Service"
    ENVIRONMENT: str = "production"
    LOG_LEVEL: LogLevel = LogLevel.INFO
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    MAX_N: int = 1_000_000
    DEFAULT_ALGORITHM: str = "FAST_DOUBLING"
    ENABLE_STRING_CONVERSION_LIMIT_INCREASE: bool = True
    MAX_STR_DIGITS: int = 1_000_000


settings = Settings()
