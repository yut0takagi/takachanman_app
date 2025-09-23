from fastapi import APIRouter, Depends

from server.common.deps import require_roles
from server.models.user import User


router = APIRouter()


@router.get("/invoices")
def list_invoices(_: User = Depends(require_roles(["billing", "admin"]))):
    return {"invoices": []}


@router.post("/refund")
def create_refund(_: User = Depends(require_roles(["billing", "admin"]))):
    return {"status": "refunded", "id": "demo"}
"""payments（共通）APIのエンドポイント定義。\n請求一覧や返金作成を提供する（RBAC保護）。"""
