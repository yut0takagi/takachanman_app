from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from server.core.config import settings
from server.core.database import get_db
from server.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    decode_token,
)
from server.models.user import User, Role
from server.schemas.auth import UserCreate, UserOut, TokenPair, TokenRefresh
from server.common.deps import get_current_user


router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    # assign default roles
    role_objs = (
        db.query(Role).filter(Role.name.in_(settings.default_roles)).all()
        if settings.default_roles
        else []
    )
    # Ensure roles exist
    existing_names = {r.name for r in role_objs}
    to_create = [name for name in settings.default_roles if name not in existing_names]
    for name in to_create:
        r = Role(name=name)
        db.add(r)
        db.flush()
        role_objs.append(r)
    user.roles = role_objs
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(id=user.id, email=user.email, roles=[r.name for r in user.roles])


@router.post("/login", response_model=TokenPair)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
def refresh_token(payload: TokenRefresh):
    try:
        data = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user_id = data.get("sub")
    return TokenPair(access_token=create_access_token(user_id), refresh_token=create_refresh_token(user_id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(id=user.id, email=user.email, roles=[r.name for r in user.roles])
"""/common/auth 配下の認証API。\nユーザ登録・ログイン・トークン更新・ユーザ情報取得を提供する。"""
