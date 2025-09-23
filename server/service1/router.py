"""service1 サンプルサービスのAPIルータ。
/service1/ 配下で、公開・認証任意・RBAC保護の例を提供する。"""
from fastapi import APIRouter, Depends

from server.common.deps import get_optional_user, require_roles
from server.models.user import User


router = APIRouter()


@router.get("/hello")
def hello(user: User | None = Depends(get_optional_user)) -> dict:
    if user:
        return {"message": f"hello, {user.email}"}
    return {"message": "hello, guest"}


@router.get("/items")
def list_items() -> dict:
    return {"items": [{"id": 1, "name": "demo"}]}


@router.post("/items")
def create_item(_: User = Depends(require_roles(["user", "admin"]))) -> dict:
    return {"created": {"id": 2, "name": "new"}}


@router.get("/admin")
def admin_only(_: User = Depends(require_roles(["admin"]))) -> dict:
    return {"ok": True}

