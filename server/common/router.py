import base64
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel

from server.common.deps import require_roles, get_optional_user
from server.common.metrics import get_metrics, render_prometheus
from server.common.audit import record_event, recent_events
from server.models.user import User
from server.core.config import settings
from server.core.database import get_db
from server.core.security import hash_password, verify_password
from sqlalchemy import text
from sqlalchemy.orm import Session
from server.common.utils.logging_utils import get_logs, set_log_level


router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/metrics")
def metrics() -> dict:
    return get_metrics()


class AuditIn(BaseModel):
    action: str
    target: str | None = None
    meta: dict | None = None


@router.post("/audit/events")
def audit_event(payload: AuditIn, user: User = Depends(require_roles(["admin"]))):
    record_event(action=payload.action, actor=user.email, target=payload.target, meta=payload.meta)
    return {"ok": True}


@router.get("/audit/events")
def audit_events(_: User = Depends(require_roles(["admin"]))):
    return {"events": recent_events()}


@router.get("/version")
def version() -> dict:
    return {
        "name": "takachanman unified server",
        "version": "0.1.0",
        "env": settings.env,
        "debug": settings.debug,
    }


@router.get("/config")
def config(_: User = Depends(require_roles(["admin"]))):
    # sanitize secrets
    return {
        "env": settings.env,
        "debug": settings.debug,
        "cors_origins": settings.cors_origins,
        "rate_limit_max": settings.rate_limit_max,
        "rate_limit_window": settings.rate_limit_window,
        "database_url": settings.database_url or f"sqlite:///{settings.sqlite_path}",
        "access_token_expires_minutes": settings.access_token_expires_minutes,
        "refresh_token_expires_minutes": settings.refresh_token_expires_minutes,
        "default_roles": settings.default_roles,
    }


@router.get("/ping")
def ping() -> dict:
    return {"pong": True}


@router.get("/time")
def time_now() -> dict:
    now = datetime.now(timezone.utc)
    return {"utc_iso": now.isoformat(), "epoch": int(now.timestamp())}


@router.get("/uuid")
def uuid_new() -> dict:
    return {"uuid": str(uuid.uuid4())}


@router.get("/ip")
def client_ip(request: Request) -> dict:
    ip = request.client.host if request.client else None
    return {"ip": ip}


@router.get("/headers")
def headers(request: Request) -> dict:
    return {"headers": {k: v for k, v in request.headers.items()}}


@router.post("/echo")
def echo(payload: dict | None = None) -> dict:
    return {"echo": payload}


@router.get("/uptime")
def uptime() -> dict:
    m = get_metrics()
    return {"uptime_seconds": m.get("uptime_seconds", 0)}


class HashIn(BaseModel):
    text: str


@router.post("/crypto/hash")
def crypto_hash(payload: HashIn, _: User = Depends(require_roles(["admin"]))):
    return {"hash": hash_password(payload.text)}


class VerifyIn(BaseModel):
    text: str
    hashed: str


@router.post("/crypto/verify")
def crypto_verify(payload: VerifyIn, _: User = Depends(require_roles(["admin"]))):
    return {"valid": verify_password(payload.text, payload.hashed)}


class B64In(BaseModel):
    text: str


@router.post("/base64/encode")
def b64_encode(payload: B64In) -> dict:
    return {"encoded": base64.b64encode(payload.text.encode()).decode()}


@router.post("/base64/decode")
def b64_decode(payload: B64In) -> dict:
    try:
        return {"decoded": base64.b64decode(payload.text.encode()).decode()}
    except Exception:
        return {"decoded": None}


@router.get("/env")
def env_vars(_: User = Depends(require_roles(["admin"]))):
    env = {k: v for k, v in os.environ.items() if k.startswith("APP_")}
    return {"env": env}


@router.get("/health/deep")
def health_deep(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": True}
    except Exception:
        return {"status": "degraded", "db": False}


@router.get("/readiness")
def readiness(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        return {"ready": False}


@router.get("/liveness")
def liveness() -> dict:
    return {"alive": True}


@router.get("/whoami")
def whoami(user: User | None = Depends(get_optional_user)) -> dict:
    if not user:
        return {"authenticated": False, "user": None}
    return {
        "authenticated": True,
        "user": {"id": user.id, "email": user.email, "roles": [r.name for r in user.roles]},
    }


@router.get("/metrics/prometheus")
def metrics_prometheus() -> Response:
    text = render_prometheus()
    return Response(content=text, media_type="text/plain; version=0.0.4; charset=utf-8")


@router.get("/logs")
def logs(limit: int = 200, level: str | None = None, _: User = Depends(require_roles(["admin"]))):
    return {"logs": get_logs(limit=limit, level=level)}


class LogLevelIn(BaseModel):
    name: str = ""  # empty for root
    level: str


@router.post("/logs/level")
def logs_level(payload: LogLevelIn, _: User = Depends(require_roles(["admin"]))):
    set_log_level(payload.name, payload.level)
    return {"ok": True}
