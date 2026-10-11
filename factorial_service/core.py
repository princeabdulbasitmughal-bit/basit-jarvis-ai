"""
Core execution engine for computing factorials synchronously and asynchronously.
"""

import asyncio
import math
from functools import lru_cache
from typing import Union

from factorial_service.config import get_settings
from factorial_service.exceptions import ExceedsMaximumInputError, InvalidInputError
from factorial_service.logger import get_logger

logger = get_logger(__name__)


def validate_input(n: Union[int, float]) -> int:
    """
    Validates that the input integer meets mathematical and safety requirements.

    Args:
        n (Union[int, float]): Input value to validate.

    Returns:
        int: Standardized positive integer or zero.

    Raises:
        InvalidInputError: If input is not an integer or is negative.
        ExceedsMaximumInputError: If input exceeds configured maximum limits.
    """
    settings = get_settings()

    if isinstance(n, bool):
        logger.error("Boolean value supplied instead of integer: %s", n)
        raise InvalidInputError("Input must be a non-negative integer, got boolean.")

    if not isinstance(n, int):
        if isinstance(n, float) and n.is_integer():
            n = int(n)
        else:
            logger.error("Non-integer value supplied: %s (type: %s)", n, type(n).__name__)
            raise InvalidInputError(f"Input must be a non-negative integer, got {type(n).__name__}.")

    if n < 0:
        logger.error("Negative integer supplied: %d", n)
        raise InvalidInputError(f"Factorial is not defined for negative numbers: {n}")

    if n > settings.max_input:
        logger.error("Input integer %d exceeds maximum limit %d", n, settings.max_input)
        raise ExceedsMaximumInputError(
            f"Input integer {n} exceeds the maximum allowed limit of {settings.max_input}."
        )

    return n


@lru_cache(maxsize=128)
def compute_factorial(n: int) -> int:
    """
    Computes the factorial of a given non-negative integer synchronously with LRU caching.

    Args:
        n (int): Non-negative integer.

    Returns:
        int: Computed factorial result.

    Raises:
        InvalidInputError: If input is invalid or negative.
        ExceedsMaximumInputError: If input exceeds limit.
    """
    valid_n = validate_input(n)
    logger.debug("Computing factorial synchronously for n=%d", valid_n)

    try:
        result = math.factorial(valid_n)
        logger.info("Successfully calculated factorial for n=%d", valid_n)
        return result
    except Exception as exc:
        logger.exception("Unexpected error occurred while calculating factorial for n=%d", valid_n)
        raise exc


async def compute_factorial_async(n: int) -> int:
    """
    Asynchronously computes the factorial by offloading calculation to an executor pool.

    Args:
        n (int): Non-negative integer.

    Returns:
        int: Computed factorial result.

    Raises:
        InvalidInputError: If input is invalid or negative.
        ExceedsMaximumInputError: If input exceeds limit.
    """
    valid_n = validate_input(n)
    logger.debug("Dispatching asynchronous factorial computation for n=%d", valid_n)

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, compute_factorial, valid_n)
        return result
    except Exception as exc:
        logger.error("Error during asynchronous computation for n=%d: %s", valid_n, str(exc))
        raise
