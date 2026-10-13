"""
Pydantic models for request/response bodies and JWT payload.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """Response model for JWT token."""
    access_token: str = Field(..., description="Encoded JWT token.")
    token_type: str = Field("bearer", description="Token type, always 'bearer'.")


class TokenData(BaseModel):
    """Data stored inside JWT payload."""
    username: Optional[str] = Field(None, description="Username of the authenticated user.")
    exp: Optional[int] = Field(None, description="Expiration timestamp (unix epoch).")


class User(BaseModel):
    """Simple user model (in real world this would be from DB)."""
    username: str = Field(..., description="Unique username.")
    full_name: Optional[str] = Field(None, description="Full name of the user.")
    disabled: bool = Field(False, description="Whether the user is disabled.")
