"""Pydantic models used across the application."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="Encoded JWT access token")
    token_type: str = Field("bearer", description="Token type, always 'bearer'")


class TokenData(BaseModel):
    """Data extracted from a validated JWT."""

    username: Optional[str] = None
    exp: Optional[int] = None


class TelemetryMetrics(BaseModel):
    """Aggregated system metrics returned by the `/metrics` endpoint."""

    timestamp: datetime = Field(..., description="UTC timestamp of collection")
    cpu_percent: float = Field(..., description="Overall CPU utilization percentage")
    memory: Dict[str, float] = Field(
        ..., description="Memory usage (total, used, free) in MB"
    )
    disk: Dict[str, float] = Field(
        ..., description="Disk usage (total, used, free) in GB"
    )
    network: Dict[str, int] = Field(
        ..., description="Network I/O counters (bytes_sent, bytes_recv)"
    )
