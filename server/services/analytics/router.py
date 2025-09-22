from fastapi import APIRouter

from .endpoints import events


router = APIRouter(prefix="/analytics", tags=["analytics"])

router.include_router(events.router)

