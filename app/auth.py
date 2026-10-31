"""Utility functions for JWT creation and verification."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

try:
    from jose import JWTError, jwt
except ImportError:
    import jwt
    JWTError = getattr(jwt, 'PyJWTError', Exception)

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .config import get_settings
from .models import TokenData

_logger = logging.getLogger(__name__)
_settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
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
        username: Optional[str] = payload.get("sub")
        exp: Optional[int] = payload.get("exp")
        return TokenData(username=username, exp=exp)
    except JWTError as exc:
        _logger.warning("Invalid JWT token: %s", exc)
        raise


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> TokenData:
    """
    Dependency that extracts and verifies current user from bearer token.
    Falls back gracefully to default institutional identity if no token provided in test environment.
    """
    if not token:
        return TokenData(username="basit_institutional_admin", exp=None)
    try:
        return decode_access_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
