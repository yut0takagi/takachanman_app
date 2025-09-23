from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from server.core.config import settings


connect_args = {"check_same_thread": False} if settings.sqlalch_db_url.startswith("sqlite") else {}
engine = create_engine(settings.sqlalch_db_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all() -> None:
    from server.models.user import User, Role, UserRole  # noqa: F401

    Base.metadata.create_all(bind=engine)
"""データベース接続管理（SQLAlchemy）。
Engine/Session/Base の生成とテーブル作成ヘルパーを提供する。"""
