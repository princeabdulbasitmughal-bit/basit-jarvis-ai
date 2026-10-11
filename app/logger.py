"""
Centralised logging configuration.
"""

import logging
import sys
from logging.config import dictConfig

from .config import get_settings


def configure_logging() -> None:
    """
    Configures the root logger using dictConfig.
    """
    settings = get_settings()
    log_level = settings.LOG_LEVEL

    logging_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": sys.stdout,
                "level": log_level,
            },
        },
        "root": {"handlers": ["console"], "level": log_level},
    }

    dictConfig(logging_config)


configure_logging()
logger = logging.getLogger(__name__)
