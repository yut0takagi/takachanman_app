from fastapi import APIRouter, Depends

from server.common.deps import require_roles
from server.models.user import User


router = APIRouter()


@router.post("/events")
def track_event(_: User = Depends(require_roles(["analyst", "admin"]))):
    return {"ok": True}
"""analytics サービスのAPIエンドポイント定義。
イベント計測などを提供する（RBAC保護）。"""
