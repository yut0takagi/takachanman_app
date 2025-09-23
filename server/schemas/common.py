from pydantic import BaseModel


class Message(BaseModel):
    message: str
"""共通スキーマ定義。簡易メッセージ等。"""
