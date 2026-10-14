"""
JWT utilities and FastAPI security dependencies.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import get_settings
from .models import TokenData

logger = logging.getLogger(__name__)

_security = HTTPBearer(auto_error=False)


def _create_jwt(payload: Dict[str, Any], expires_delta: timedelta) -> str:
    """Encode a JWT token."""
    settings = get_settings()
    to_encode = payload.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    logger.debug("JWT token created for payload: %s", payload)
    return token


def create_access_token(username: str) -> str:
    """
    Public helper to create a JWT access token for a given username.
    """
    settings = get_settings()
    return _create_jwt(
        {"sub": username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> str:
    """
    FastAPI dependency that validates the JWT token and returns the username.
    Raises HTTPException(401) if token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        token_data = TokenData(**payload)
        if token_data.username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing username",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.debug("Authenticated request for user: %s", token_data.username)
        return token_data.username
    except JWTError as exc:
        logger.warning("JWT validation error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
