from fastapi import APIRouter, Depends

from server.common.deps import require_roles
from server.models.user import User


router = APIRouter()


@router.get("/invoices")
def list_invoices(_: User = Depends(require_roles(["billing", "admin"]))):
    return {"invoices": []}
"""billing（参考）サービスのAPIエンドポイント定義。\n請求関連の読み取りを提供する（RBAC保護）。"""
