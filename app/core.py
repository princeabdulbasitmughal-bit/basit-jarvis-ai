"""
Core business logic for generating a greeting.

Provides an async ``say_hello`` function that validates the input,
creates a greeting string and logs the operation.
"""

from __future__ import annotations

import re
from typing import Optional

from .exceptions import HelloError
from .logger import get_logger

_logger = get_logger()

_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s'-]*$")

async def say_hello(name: Optional[str] = None) -> str:
    """
    Generate a greeting for ``name``.

    The function is deliberately ``async`` to allow easy integration
    with asynchronous frameworks (e.g., FastAPI) and future I/O‑bound
    extensions.

    Parameters
    ----------
    name: Optional[str]
        The name to greet. If ``None`` or an empty/invalid string is
        supplied, the default ``"World"`` is used.

    Returns
    -------
    str
        A greeting in the form ``"Hello, <Name>!"``.

    Raises
    ------
    HelloError
        If the supplied ``name`` contains disallowed characters.
    """
    try:
        # 1️⃣ Default handling
        if not name:
            _logger.debug("No name supplied; using default 'World'.")
            name = "World"

        # 2️⃣ Sanitisation – strip surrounding whitespace
        sanitized = name.strip()
        _logger.debug("Sanitized name: %r", sanitized)

        # 3️⃣ Validation – simple regex to allow letters, spaces, hyphens, apostrophes
        if not _NAME_PATTERN.fullmatch(sanitized):
            raise HelloError(
                f"Invalid name supplied: {sanitized!r}. "
                "Only alphabetic characters, spaces, hyphens and apostrophes are allowed."
            )

        greeting = f"Hello, {sanitized}!"
        _logger.info("Generated greeting: %s", greeting)
        return greeting

    except HelloError:
        # Re‑raise known errors after logging
        _logger.exception("Failed to generate greeting due to validation error.")
        raise
    except Exception as exc:
        # Catch‑all for unexpected issues
        _logger.exception("Unexpected error in say_hello.")
        raise HelloError("An unexpected error occurred while generating the greeting.") from exc
