from fastapi import APIRouter, Depends, HTTPException, status  # FastAPIの道具（APIの入口、依存関係、エラー処理など）
from fastapi.security import OAuth2PasswordRequestForm          # ログイン時にユーザー名とパスワードを受け取るためのフォーム
from sqlalchemy.orm import Session                              # データベースとやりとりするための部品

from server.core.config import settings                         # 設定ファイル（初期ロールなど）
from server.core.database import get_db                         # データベースの接続を準備する関数
from server.core.security import (                              # セキュリティ関係の道具
    create_access_token,   # 短時間有効な通行証を作る
    create_refresh_token,  # 長時間有効な通行証を作る予備券
    hash_password,         # パスワードを暗号化（ぐちゃぐちゃにする）
    verify_password,       # 入力したパスワードが正しいか確認
    decode_token,          # トークン（通行証）の中身を解読
)
from server.models.user import User, Role                       # ユーザーや役割（ロール）のデータベースモデル
from server.schemas.auth import UserCreate, UserOut, TokenPair, TokenRefresh  # 入出力のデータ形式（スキーマ）
from server.common.deps import get_current_user                 # 今のユーザー情報を取得する便利関数

router = APIRouter()  # APIの入口をまとめる部品

# ------------------------------
# ユーザー登録API
# ------------------------------
@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """

    """
    exists = db.query(User).filter(User.email == payload.email).first()  # メールがすでに使われていないかチェック
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")  # 使われていたらエラーを返す
    user = User(email=payload.email, hashed_password=hash_password(payload.password))  # 新しいユーザーを作成（パスワードは暗号化）
    
    # デフォルトの役割（例: user）を確認して追加
    role_objs = (
        db.query(Role).filter(Role.name.in_(settings.default_roles)).all()
        if settings.default_roles
        else []
    )
    existing_names = {r.name for r in role_objs}  # すでにある役割
    to_create = [name for name in settings.default_roles if name not in existing_names]  # 新しく作るべき役割
    for name in to_create:
        r = Role(name=name)  # 役割を作成
        db.add(r)
        db.flush()
        role_objs.append(r)
    user.roles = role_objs  # ユーザーに役割をセット
    db.add(user)            # データベースに保存
    db.commit()             # 変更を確定
    db.refresh(user)        # 保存後の最新状態を取得
    return UserOut(id=user.id, email=user.email, roles=[r.name for r in user.roles])  # ユーザー情報を返す

# ------------------------------
# ログインAPI
# ------------------------------
@router.post("/login", response_model=TokenPair)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    """
    user = db.query(User).filter(User.email == form_data.username).first()  # 入力されたメールのユーザーを探す
    if not user or not verify_password(form_data.password, user.hashed_password):  # パスワードが違ったら
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")  # エラー（401: 許可なし）
    access = create_access_token(str(user.id))     # アクセストークンを作成（短時間有効）
    refresh = create_refresh_token(str(user.id))   # リフレッシュトークンを作成（更新用の予備券）
    return TokenPair(access_token=access, refresh_token=refresh)  # 2つのトークンを返す

# ------------------------------
# トークン更新API
# ------------------------------
@router.post("/refresh", response_model=TokenPair)
def refresh_token(payload: TokenRefresh):
    """
    
    """
    try:
        data = decode_token(payload.refresh_token)  # リフレッシュトークンを解読
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")  # 無効ならエラー
    if data.get("type") != "refresh":  # トークンの種類が「refresh」でないなら
        raise HTTPException(status_code=401, detail="Invalid token type")  # エラー
    user_id = data.get("sub")  # トークンからユーザーIDを取り出す
    return TokenPair(
        access_token=create_access_token(user_id),     # 新しいアクセストークンを発行
        refresh_token=create_refresh_token(user_id)    # 新しいリフレッシュトークンを発行
    )

# ------------------------------
# 自分の情報取得API
# ------------------------------
@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(id=user.id, email=user.email, roles=[r.name for r in user.roles])  # 自分のユーザー情報を返す