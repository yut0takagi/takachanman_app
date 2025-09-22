import time
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings


def add_middleware(app: FastAPI) -> None:
    settings = get_settings()

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Simple logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable):  # type: ignore[override]
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time-ms"] = f"{duration_ms:.2f}"
        return response

    # Root path support (primarily for reverse proxies)
    if settings.root_path and getattr(app, "root_path", "") != settings.root_path:
        app.root_path = settings.root_path

