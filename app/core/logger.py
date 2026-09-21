"""
Centralised logging configuration.
"""

from __future__ import annotations

import logging
import sys
from logging.config import dictConfig
from typing import Final

from .config import settings

_LOG_CONFIG: Final[dict] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": ["default"],
        "level": settings.LOG_LEVEL,
    },
}

def configure_logging() -> None:
    """
    Apply the logging configuration defined in ``_LOG_CONFIG``.
    This should be called once, as early as possible in the program start‑up.
    """
    dictConfig(_LOG_CONFIG)

# Configure logging immediately upon import so that any module importing this
# file has a ready‑to‑use logger.
configure_logging()
logger = logging.getLogger(__name__)
