"""/common/analytics 配下のアナリティクス共通API。
イベントトラッキングなど、横断利用される分析系エンドポイントを提供する。"""
from fastapi import APIRouter, Depends

from server.common.deps import require_roles
from server.models.user import User


router = APIRouter()


@router.post("/events")
def track_event(_: User = Depends(require_roles(["analyst", "admin"]))):
    return {"ok": True}

