"""
Centralised logging configuration.

The logger is configured at import time, making it instantly available
throughout the project via `logging.getLogger(__name__)`.
"""

import logging
import sys
from logging.config import dictConfig

from .config import get_settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": sys.stdout,
        },
    },
    "root": {"handlers": ["default"], "level": "INFO"},
}


def configure_logging() -> None:
    """Apply the logging configuration."""
    dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.debug("Logging configured")


# Configure logging as soon as the module is imported
configure_logging()
logger = logging.getLogger("telemetry")
