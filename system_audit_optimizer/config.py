"""
Application Configuration Module.
Centralized settings management using environment variables and Pydantic Settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """System configuration parameters."""

    ENV: str = Field(default="production", description="Application environment (development/production/testing)")
    DEBUG: bool = Field(default=False, description="Enable debug logging and detailed API errors")
    HOST: str = Field(default="0.0.0.0", description="API server bind host")
    PORT: int = Field(default=8000, description="API server bind port")

    # Worker Pool Settings
    MAX_CONCURRENT_WORKERS: int = Field(default=10, description="Maximum concurrent background workers")
    QUEUE_CAPACITY: int = Field(default=1000, description="Worker pool task queue buffer limit")
    TASK_TIMEOUT_SECONDS: float = Field(default=30.0, description="Task execution timeout limit in seconds")

    # Audit & Metric Thresholds
    CPU_WARNING_THRESHOLD: float = Field(default=85.0, description="CPU usage warning percentage threshold")
    MEMORY_WARNING_THRESHOLD: float = Field(default=85.0, description="RAM usage warning percentage threshold")
    MAX_FILE_SIZE_BYTES: int = Field(default=5_000_000, description="Maximum source file size for AST scanning")

    # Security
    API_KEY_SECRET: Optional[str] = Field(default=None, description="Optional bearer token API key")

    class Config:
        env_prefix = "AUDIT_OPT_"
        case_sensitive = True


def get_settings() -> Settings:
    """Singleton getter for application settings."""
    return Settings()
