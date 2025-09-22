from fastapi import FastAPI

from server.core.config import settings
from server.core.database import create_all
from server.core.rate_limit import add_rate_limit_middleware
from server.common.metrics import add_metrics_middleware
from server.common.auth import router as auth_router
from server.api.routers.analytics import router as analytics_router
from server.common.router import router as common_router
from server.api.routers.billing import router as billing_router
from fastapi.middleware.cors import CORSMiddleware
from server.common.utils.logging_utils import register_handler as register_logging_handler


def create_app() -> FastAPI:
    app = FastAPI(title="takachanman unified server", version="0.1.0")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limit (simple, in-memory)
    add_rate_limit_middleware(app, max_requests=settings.rate_limit_max, window_seconds=settings.rate_limit_window)
    # Request metrics
    add_metrics_middleware(app)
    # Log collection handler (ring buffer)
    register_logging_handler()

    # Routers
    # Centralized common features
    app.include_router(common_router, prefix="/common", tags=["common"])
    app.include_router(auth_router, prefix="/common/auth", tags=["auth"])
    try:
        from server.api.routers.payments import router as payments_router  # type: ignore

        app.include_router(payments_router, prefix="/common/payments", tags=["payments"])
    except Exception:
        app.include_router(billing_router, prefix="/common/billing", tags=["billing"])

    # Service specific namespaces
    app.include_router(analytics_router, prefix="/yutotkg/analytics", tags=["analytics"])

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()


@app.on_event("startup")
def on_startup() -> None:
    create_all()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
