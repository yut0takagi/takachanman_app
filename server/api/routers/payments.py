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
