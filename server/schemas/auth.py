from pydantic import BaseModel, EmailStr
from typing import List


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    roles: List[str]

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str
"""認証関連のPydanticスキーマ。
ユーザ登録/出力、トークンペイロード等を定義する。"""
