"""
Structured logger setup for Factorial Service.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str = "factorial_service", level: Optional[str] = None) -> logging.Logger:
    """
    Creates and configures a standard logger instance.

    Args:
        name (str): Name of the logger module.
        level (Optional[str]): Logging level name.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    if level:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    else:
        logger.setLevel(logging.INFO)
        
    return logger
