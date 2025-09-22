from fastapi import APIRouter, Depends

from server.common.models import Message
from server.core.deps import get_app_settings


router = APIRouter()


@router.get("/profile", response_model=Message)
def read_profile(_: None = Depends(get_app_settings)) -> Message:
    return Message(message="profile ok")

