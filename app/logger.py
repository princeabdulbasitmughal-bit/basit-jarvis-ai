"""
Centralised logger configuration.

The logger is configured once and imported wherever logging is required.
"""

import logging
from .config import LOG_LEVEL

_logger = logging.getLogger("hello_app")
if not _logger.handlers:
    # Configure only once (idempotent)
    _logger.setLevel(LOG_LEVEL)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.propagate = False

def get_logger() -> logging.Logger:
    """Return the configured application logger."""
    return _logger
