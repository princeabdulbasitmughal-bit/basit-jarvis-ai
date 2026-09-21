"""
Application entry point.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import uvicorn
from fastapi import FastAPI

from .api.router import router
from .core.logger import logger, configure_logging
from .core.config import settings

def create_app() -> FastAPI:
    """
    Construct and configure the FastAPI application instance.

    Returns:
        A fully configured ``FastAPI`` object.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.include_router(router)

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("Starting %s", settings.APP_NAME)

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("Shutting down %s", settings.APP_NAME)

    return app

app: FastAPI = create_app()

def _run_uvicorn() -> None:
    """
    Run the ASGI server using uvicorn. This function is separated
    to make unit‑testing of the FastAPI app easier.
    """
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )

if __name__ == "__main__":
    # Ensure logging is configured before uvicorn starts.
    configure_logging()
    _run_uvicorn()
