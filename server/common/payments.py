"""/common/payments 配下の決済共通API。
請求一覧や返金作成など、サービス横断で利用する支払い系エンドポイントを提供する。"""
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

