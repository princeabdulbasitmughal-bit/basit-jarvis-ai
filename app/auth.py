"""
JWT authentication utilities.
"""

import datetime
from typing import Any, Dict

import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from .config import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    """
    Data extracted from a validated JWT.
    """

    username: str | None = None
    exp: datetime.datetime | None = None


def create_access_token(data: Dict[str, Any], expires_delta: datetime.timedelta | None = None) -> str:
    """
    Creates a signed JWT access token.

    Args:
        data: Payload data (must be JSON serialisable).
        expires_delta: Optional custom expiry.

    Returns:
        Signed JWT as a string.
    """
    to_encode = data.copy()
    now = datetime.datetime.utcnow()
    expire = now + (expires_delta or datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decodes and validates a JWT.

    Args:
        token: JWT string.

    Returns:
        TokenData instance.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str | None = payload.get("sub")
        exp_timestamp = payload.get("exp")
        exp = datetime.datetime.utcfromtimestamp(exp_timestamp) if exp_timestamp else None
        return TokenData(username=username, exp=exp)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> TokenData:
    """
    FastAPI dependency that extracts and validates the JWT from the request.

    Args:
        credentials: HTTPAuthorizationCredentials automatically provided by FastAPI.

    Returns:
        TokenData of the authenticated user.

    Raises:
        HTTPException: If credentials are missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    return decode_access_token(token)
