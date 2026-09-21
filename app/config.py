"""
Configuration module.

All configuration values are loaded from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Final

# Base directory of the project
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent

# Logging configuration
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO").upper()
