from fastapi import APIRouter

from .endpoints import profile, sessions


router = APIRouter(prefix="/accounts", tags=["accounts"])

router.include_router(profile.router)
router.include_router(sessions.router)

