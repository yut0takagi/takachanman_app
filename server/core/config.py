import os
from functools import lru_cache
from typing import List


class Settings:
    def __init__(
        self,
        env: str = "local",
        debug: bool = True,
        cors_origins: List[str] | None = None,
        root_path: str = "",
    ) -> None:
        self.env = env
        self.debug = debug
        self.cors_origins = cors_origins or ["*"]
        self.root_path = root_path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", "local")
    debug = os.getenv("APP_DEBUG", "true").lower() in {"1", "true", "yes", "on"}
    root_path = os.getenv("APP_ROOT_PATH", "")
    cors = os.getenv("APP_CORS_ORIGINS", "*")
    cors_origins = [o.strip() for o in cors.split(",") if o.strip()]
    return Settings(env=env, debug=debug, cors_origins=cors_origins, root_path=root_path)

