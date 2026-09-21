"""
API router definitions.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get(
    "/ping",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    tags=["Health"],
)
async def ping(request: Request) -> dict:
    """
    Simple health‑check endpoint that returns a JSON payload.

    The endpoint is deliberately asynchronous to illustrate async handling
    and to keep the signature compatible with future I/O‑bound extensions.

    Args:
        request: The incoming FastAPI request object (unused, but kept for
                 possible future extensions such as request‑based logging).

    Returns:
        A dictionary with a ``status`` key set to ``"ok"`` and an optional
        ``message`` field.

    Raises:
        HTTPException: If an unexpected error occurs while processing the request.
    """
    try:
        # Placeholder for any future async work (e.g., DB ping)
        return {"status": "ok", "message": "pong"}
    except Exception as exc:  # pragma: no cover
        # Log the exception and raise a generic HTTPException.
        # The logger is imported lazily to avoid circular imports.
        from ..core.logger import logger

        logger.exception("Unhandled exception in ping endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc

# Global exception handler to transform unexpected errors into JSON responses.
@router.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # pragma: no cover
    """
    Convert any uncaught exception into a JSON response with a 500 status code.
    """
    from ..core.logger import logger

    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
