"""
Pytest fixtures shared across the test suite.
"""

import pytest
from fastapi.testclient import TestClient

from app.api import app

@pytest.fixture(scope="session")
def client() -> TestClient:
    """Provides a synchronous TestClient for the FastAPI app."""
    return TestClient(app)
