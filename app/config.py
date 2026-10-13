"""
Configuration module using Pydantic BaseSettings.
All secrets are loaded from environment variables.
"""

import os
from functools import lru_cache
from datetime import timedelta
try:
    from pydantic.v1 import BaseSettings, Field, SecretStr, validator
except ImportError:
    from pydantic import BaseSettings, Field, SecretStr, validator


class Settings(BaseSettings):
    """Application settings."""
    jwt_secret_key: SecretStr = Field(
        SecretStr(os.getenv("JWT_SECRET_KEY", "dev_jwt_secret_key_basit_2026_super_safe_32ch")),
        env="JWT_SECRET_KEY",
        description="Secret key used to sign JWT tokens."
    )
    jwt_algorithm: str = Field(
        "HS256",
        env="JWT_ALGORITHM",
        description="Algorithm used for JWT encoding."
    )
    access_token_expire_minutes: int = Field(
        30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Access token lifetime in minutes."
    )

    # FastAPI configuration
    app_name: str = Field(
        "Telemetry Service",
        env="APP_NAME",
        description="Human readable application name."
    )
    APP_NAME: str = Field(
        "Telemetry Service",
        env="APP_NAME",
        description="Human readable application name."
    )
    DEBUG: bool = Field(
        False,
        env="DEBUG",
        description="FastAPI debug flag."
    )
    log_level: str = Field(
        "INFO",
        env="LOG_LEVEL",
        description="Logging level."
    )

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cache the settings instance."""
    return Settings()
