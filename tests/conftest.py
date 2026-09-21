"""
Pytest fixtures for the test suite.
"""

from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from app.main import app as fastapi_app

@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    """
    Override the default event loop fixture to have a session‑scoped loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(name="client")
async def client_fixture() -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an ``httpx.AsyncClient`` bound to the FastAPI application.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://testserver") as client:
        yield client
