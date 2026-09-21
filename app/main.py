"""
Convenient entry‑point for running the service.

Provides a ``run`` function that can be used by external scripts or
container orchestration tools.
"""

from __future__ import annotations

import sys
import logging

from .api import app
import uvicorn

def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """
    Start the FastAPI application using Uvicorn.

    Parameters
    ----------
    host: str
        Interface to bind to.
    port: int
        TCP port.
    reload: bool
        Enable auto‑reload (useful for development).
    """
    try:
        uvicorn.run(
            "app.api:app",
            host=host,
            port=port,
            reload=reload,
            log_level=logging.getLogger("hello_app").level // 10,  # map to uvicorn levels
        )
    except Exception as exc:
        logging.getLogger("hello_app").exception("Failed to start the server.")
        sys.exit(1)

if __name__ == "__main__":
    # Simple CLI hook
    run(reload=True)
