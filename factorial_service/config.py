"""
Configuration management for the Factorial Service using environment variables.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Settings:
    """
    Application settings container.
    
    Attributes:
        max_input (int): Maximum allowed integer for factorial computation to prevent CPU exhaustion.
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    max_input: int = int(os.getenv("FACTORIAL_MAX_INPUT", "10000"))
    log_level: str = os.getenv("FACTORIAL_LOG_LEVEL", "INFO").upper()


def get_settings() -> Settings:
    """
    Retrieve default settings instance.

    Returns:
        Settings: Configured application settings.
    """
    return Settings()
