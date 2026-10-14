"""
Pydantic models used throughout the application.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT access token response."""

    access_token: str = Field(..., description="Encoded JWT token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Data stored inside JWT token."""

    username: Optional[str] = None
    exp: Optional[int] = None


class UserLogin(BaseModel):
    """Login payload."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class MetricsResponse(BaseModel):
    """System metrics returned by the /metrics endpoint."""

    cpu_percent: float = Field(..., description="CPU utilization percent")
    memory_total: int = Field(..., description="Total physical memory in bytes")
    memory_used: int = Field(..., description="Used memory in bytes")
    memory_percent: float = Field(..., description="Memory utilization percent")
    disk_total: int = Field(..., description="Total disk space in bytes")
    disk_used: int = Field(..., description="Used disk space in bytes")
    disk_percent: float = Field(..., description="Disk utilization percent")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp")
