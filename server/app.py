from fastapi import FastAPI

from server.core.middleware import add_middleware
from server.common.errors import register_exception_handlers
from server.services.accounts.router import router as accounts_router
from server.services.payments.router import router as payments_router
from server.services.analytics.router import router as analytics_router


def create_app() -> FastAPI:
    app = FastAPI(title="takachanman app")
    add_middleware(app)
    register_exception_handlers(app)

    app.include_router(accounts_router)
    app.include_router(payments_router)
    app.include_router(analytics_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)
