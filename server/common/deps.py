from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.core.security import decode_token
from server.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/common/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/common/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(required: List[str]):
    def checker(user: User = Depends(get_current_user)) -> User:
        user_roles = {r.name for r in user.roles}
        if not (user_roles.intersection(set(required)) or ("admin" in user_roles)):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return checker


def get_optional_user(token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = db.query(User).filter(User.id == int(user_id)).first()
        return user
    except Exception:
        return None
"""共通依存関数。\n現在ユーザ取得・RBACチェック・任意認証ユーザ取得を提供する。"""
