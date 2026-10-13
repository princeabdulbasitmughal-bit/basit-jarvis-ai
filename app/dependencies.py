"""
FastAPI dependencies for authentication and shared utilities.
"""

import logging
from datetime import datetime, timezone
from typing import Generator

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from .config import get_settings, Settings
from .models import TokenData

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def decode_jwt(token: str, settings: Settings) -> TokenData:
    """
    Decode a JWT token and return the payload.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        exp: int = payload.get("exp")
        if username is None or exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing required fields",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(username=username, exp=exp)
    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as exc:
        logger.warning("Invalid JWT token: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme), settings: Settings = Depends(get_settings)
) -> TokenData:
    """
    FastAPI dependency that validates JWT and returns token data.
    """
    return decode_jwt(token, settings)


def get_request_id(request: Request) -> str:
    """
    Extract or generate a request ID for logging correlation.
    """
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = f"{datetime.now(tz=timezone.utc).timestamp()}-{id(request)}"
    return request_id
