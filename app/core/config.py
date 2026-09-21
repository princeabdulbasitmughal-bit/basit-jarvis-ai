"""
Configuration handling for the FastAPI application.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from pydantic import BaseSettings, Field, validator

class Settings(BaseSettings):
    """
    Settings for the application, loaded from environment variables
    or a `.env` file located at the project root.
    """

    APP_NAME: str = Field("Status Ping Service", env="APP_NAME")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    DEBUG: bool = Field(False, env="DEBUG")
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")
    RELOAD: bool = Field(False, env="RELOAD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("LOG_LEVEL")
    def _validate_log_level(cls, v: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
        upper_v = v.upper()
        if upper_v not in allowed:
            raise ValueError(f"Invalid LOG_LEVEL: {v}. Choose from {allowed}")
        return upper_v

# Create a module‑level singleton that can be imported elsewhere.
settings: Final[Settings] = Settings()
