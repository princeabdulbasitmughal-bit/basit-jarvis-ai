"""
Integration tests for the ``/ping`` endpoint.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_ping_success(client: AsyncClient) -> None:
    """
    Verify that the ``/ping`` endpoint returns a 200 response with the expected payload.
    """
    response = await client.get("/ping")
    assert response.status_code == 200
    json_body = response.json()
    assert isinstance(json_body, dict)
    assert json_body.get("status") == "ok"
    assert json_body.get("message") == "pong"
