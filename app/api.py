"""
FastAPI HTTP interface exposing the ``say_hello`` functionality.

Running the module directly starts a development server using Uvicorn.
"""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from .core import say_hello
from .exceptions import HelloError

app = FastAPI(title="Hello Service", version="1.0.0")

@app.get("/hello", response_class=JSONResponse, summary="Return a greeting")
async def hello_endpoint(name: Optional[str] = Query(None, description="Name to greet")):
    """
    HTTP GET endpoint that returns a greeting.

    Query Parameters
    ----------------
    name: Optional[str]
        The name to greet. If omitted, defaults to ``World``.

    Returns
    -------
    JSONResponse
        ``{"greeting": "<message>"}``
    """
    try:
        greeting = await say_hello(name)
        return {"greeting": greeting}
    except HelloError as exc:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

if __name__ == "__main__":
    # When executed directly, start a development server.
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
