"""Application configuration settings managed via Pydantic BaseSettings."""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable fallback and validation."""

    APP_NAME: str = Field(default="FastAPI Telemetry Service", description="Application name")
    ENVIRONMENT: str = Field(default="production", description="Execution environment (development, staging, production)")
    DEBUG: bool = Field(default=False, description="Debug mode state")
    API_V1_STR: str = Field(default="/api/v1", description="API Route prefix")

    # Security / JWT
    SECRET_KEY: str = Field(
        default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        description="JWT Secret key for signing tokens. Override in production!"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT Signing Algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token TTL in minutes")

    # Admin Credentials (In production, replace with DB lookup)
    ADMIN_USERNAME: str = Field(default="admin", description="Admin username for JWT generation")
    ADMIN_PASSWORD_HASH: str = Field(
        default="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # bcrypt for "secret"
        description="Bcrypt hashed password for admin user"
    )

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(default=["*"], description="Allowed CORS origins")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
