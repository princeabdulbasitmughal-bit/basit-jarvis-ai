"""
FastAPI application entry point.
"""

import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .auth import create_access_token, TokenData
from .config import get_settings
from .logger import logger
from .metrics import router as metrics_router

settings = get_settings()
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


@app.post("/token", response_model=Dict[str, str])
async def login(form_data: OAuth2PasswordRequestForm = ...):
    """
    Dummy login endpoint that issues JWTs.
    In a real-world scenario replace with proper credential validation.

    Args:
        form_data: Form containing ``username`` and ``password``.

    Returns:
        Access token dictionary.
    """
    # Dummy validation – replace with DB/LDAP/etc.
    if form_data.username != "admin" or form_data.password != "secret":
        logger.warning("Invalid login attempt for user %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data: Dict[str, Any] = {"sub": form_data.username}
    access_token = create_access_token(token_data)
    logger.info("User %s logged in successfully", form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/", include_in_schema=False)
async def root() -> Dict[str, str]:
    """
    Simple health‑check endpoint.
    """
    return {"message": "Telemetry service is running"}


# Register routers
app.include_router(metrics_router)


# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error",
    )
