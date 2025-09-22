from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", case_sensitive=False)

    # App
    env: str = "local"
    debug: bool = True
    secret_key: str = "changeme-secret"
    access_token_expires_minutes: int = 30
    refresh_token_expires_minutes: int = 60 * 24 * 7  # 7 days

    # CORS & rate limit
    cors_origins: List[str] = ["*"]
    rate_limit_max: int = 60
    rate_limit_window: int = 60

    # DB
    sqlite_path: str = "./app.db"
    database_url: str | None = None

    # RBAC
    default_roles: List[str] = ["user"]

    @property
    def sqlalch_db_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"sqlite:///{self.sqlite_path}"


settings = Settings()
