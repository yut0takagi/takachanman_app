from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt, JWTError
from passlib.context import CryptContext

from server.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(subject: str, token_type: str, expires_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)
    to_encode = {"sub": subject, "type": token_type, "iat": int(now.timestamp()), "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_access_token(subject: str) -> str:
    return create_token(subject, "access", settings.access_token_expires_minutes)


def create_refresh_token(subject: str) -> str:
    return create_token(subject, "refresh", settings.refresh_token_expires_minutes)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError("Invalid token") from e
"""セキュリティ関連ユーティリティ。
bcrypt によるパスワードハッシュ/検証と、JWT の発行/検証を提供する。"""
