"""
Centralised logger configuration.
"""

import logging
import sys
from typing import Final

from .config import get_settings

_LOG_FORMAT: Final = (
    "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
)


def configure_logging() -> None:
    """Configure the root logger based on Settings."""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=_LOG_FORMAT,
        stream=sys.stdout,
    )
    # Reduce noise from third‑party libraries
    for noisy_logger in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


configure_logging()
logger = logging.getLogger(__name__)
