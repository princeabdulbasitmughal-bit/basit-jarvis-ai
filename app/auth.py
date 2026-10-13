"""
Authentication utilities: JWT creation, verification and FastAPI dependencies.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

from .config import get_settings
from .models import TokenData, User

logger = logging.getLogger(__name__)

# Simple in‑memory user store for demonstration purposes.
# In production replace with DB lookup.
_FAKE_USERS_DB = {
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderland",
        "disabled": False,
        "hashed_password": "fakehashedsecret",  # not used in this demo
    },
    "bob": {
        "username": "bob",
        "full_name": "Bob Builder",
        "disabled": True,
        "hashed_password": "fakehashedbuilder",
    },
}


def _get_user(username: str) -> Optional[User]:
    """Retrieve a User object from the fake DB."""
    user_dict = _FAKE_USERS_DB.get(username)
    if not user_dict:
        return None
    return User(**user_dict)


def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token.

    Args:
        data: Payload data (must be JSON serializable).
        expires_delta: Optional custom expiration timedelta.

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )
        logger.debug("JWT created for payload: %s", to_encode)
        return encoded_jwt
    except Exception as exc:
        logger.exception("Failed to encode JWT")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token generation failed",
        ) from exc


def decode_token(token: str) -> TokenData:
    """
    Decode a JWT token and return its payload.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
        token_data = TokenData(**payload)
        logger.debug("JWT decoded successfully: %s", token_data)
        return token_data
    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, ValidationError) as exc:
        logger.warning("Invalid JWT token: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> User:
    """
    FastAPI dependency that validates JWT and returns the current user.

    Raises:
        HTTPException: 401 if token missing/invalid or user disabled.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    token_data = decode_token(token)
    if token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing username",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = _get_user(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return user
