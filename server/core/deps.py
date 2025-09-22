from typing import Generator

from .config import get_settings, Settings


def get_app_settings() -> Settings:
    return get_settings()


def get_db() -> Generator[None, None, None]:
    # Placeholder for a DB session dependency
    try:
        yield None
    finally:
        pass

