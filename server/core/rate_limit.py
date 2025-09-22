import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from fastapi import FastAPI, Request


def add_rate_limit_middleware(app: FastAPI, max_requests: int = 60, window_seconds: int = 60) -> None:
    hits: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    @app.middleware("http")
    async def rate_limiter(request: Request, call_next):  # type: ignore[override]
        key = (request.client.host if request.client else "unknown", request.url.path)
        now = time.time()
        dq = hits[key]
        # purge
        cutoff = now - window_seconds
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) >= max_requests:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        dq.append(now)
        return await call_next(request)

