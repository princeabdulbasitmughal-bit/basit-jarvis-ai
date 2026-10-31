"""Centralised logger configuration."""

import logging
import sys
from typing import Final, Optional

from .config import get_settings

_settings = get_settings()

_LOG_FORMAT: Final = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging() -> None:
    """Configure root logger based on Settings."""
    logging.basicConfig(
        level=_settings.LOG_LEVEL,
        format=_LOG_FORMAT,
        stream=sys.stdout,
    )
    # Reduce noise from third-party libraries
    for lib in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(lib).setLevel(logging.INFO)


configure_logging()
logger = logging.getLogger(__name__)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Optional logger name, defaults to root logger.

    Returns:
        logging.Logger instance.
    """
    return logging.getLogger(name or "jarvis_app")
