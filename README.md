# Status Ping Service

A minimal **FastAPI** service that provides a health‑check endpoint (`GET /ping`).  
The project follows production‑ready practices:

* **Async‑first** design – all request handlers are async.
* Centralised **configuration** using Pydantic `BaseSettings`.
* Structured **logging** configured at import time.
* Comprehensive **type hints** and **docstrings**.
* **Error handling** with explicit exception handlers.
* **Test suite** using `pytest` and `httpx.AsyncClient`.

## Quick Start

