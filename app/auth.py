"""Utility functions for JWT creation and verification."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt

from .config import get_settings
from .models import TokenData

_logger = logging.getLogger(__name__)
_settings = get_settings()


def create_access_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        data: Payload data (must be JSON serialisable).
        expires_delta: Optional custom expiry; defaults to settings value.

    Returns:
        Signed JWT as a string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, _settings.JWT_SECRET_KEY, algorithm=_settings.JWT_ALGORITHM)
        return encoded_jwt
    except Exception as exc:
        _logger.exception("Failed to encode JWT")
        raise


def decode_access_token(token: str) -> TokenData:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT string.

    Returns:
        TokenData instance with extracted claims.

    Raises:
        JWTError: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, _settings.JWT_SECRET_KEY, algorithms=[_settings.JWT_ALGORITHM])
        username: str | None = payload.get("sub")
        exp: int | None = payload.get("exp")
        return TokenData(username=username, exp=exp)
    except JWTError as exc:
        _logger.warning("Invalid JWT token: %s", exc)
        raise
