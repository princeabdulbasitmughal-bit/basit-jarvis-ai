"""Logging configuration module for application-wide structured logging."""

import logging
import sys
from app.config import Settings


def setup_logger(settings: Settings) -> logging.Logger:
    """Configures and initializes the standard application logger.

    Args:
        settings (Settings): Configured settings instance.

    Returns:
        logging.Logger: Configured logger instance.
    """
    numeric_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Avoid duplicate handlers if re-initialized
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)

    # Reduce noisy logs from third-party packages
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)

    logger = logging.getLogger("telegram_ai_bot")
    logger.info("Logger initialized with level: %s", settings.log_level)
    return logger
