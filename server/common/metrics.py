import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import FastAPI, Request


_start_time = time.time()
_total_requests = 0
_path_counters: Dict[str, int] = defaultdict(int)
_method_status_counters: Dict[Tuple[str, str, int], int] = defaultdict(int)


def add_metrics_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):  # type: ignore[override]
        global _total_requests
        _total_requests += 1
        path = request.url.path
        method = request.method
        response = await call_next(request)
        status = getattr(response, "status_code", 0)
        _path_counters[path] += 1
        _method_status_counters[(method, path, status)] += 1
        return response


def get_metrics() -> Dict[str, object]:
    uptime = time.time() - _start_time
    return {
        "uptime_seconds": int(uptime),
        "total_requests": _total_requests,
        "requests_by_path": dict(_path_counters),
        "requests_by_method_status": {
            f"{m} {p} {s}": c for (m, p, s), c in _method_status_counters.items()
        },
    }


def render_prometheus() -> str:
    lines = []
    uptime = int(time.time() - _start_time)
    lines.append("# HELP takachan_uptime_seconds Uptime of the server in seconds")
    lines.append("# TYPE takachan_uptime_seconds gauge")
    lines.append(f"takachan_uptime_seconds {uptime}")

    lines.append("# HELP takachan_http_requests_total Total HTTP requests")
    lines.append("# TYPE takachan_http_requests_total counter")
    lines.append(f"takachan_http_requests_total {_total_requests}")

    lines.append("# HELP takachan_http_requests_path_total Total HTTP requests by path")
    lines.append("# TYPE takachan_http_requests_path_total counter")
    for path, count in _path_counters.items():
        lines.append(f'takachan_http_requests_path_total{{path="{path}"}} {count}')

    lines.append("# HELP takachan_http_requests_by_method_status_total Total HTTP requests by method, path and status")
    lines.append("# TYPE takachan_http_requests_by_method_status_total counter")
    for (method, path, status), count in _method_status_counters.items():
        lines.append(
            f'takachan_http_requests_by_method_status_total{{method="{method}",path="{path}",status="{status}"}} {count}'
        )

    return "\n".join(lines) + "\n"
"""共通メトリクス機能。\nミドルウェアでリクエスト統計を収集し、JSON/Prometheus形式で提供する。"""
