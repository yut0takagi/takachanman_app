from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):  # type: ignore[override]
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error", "error": str(exc.__class__.__name__)},
        )

