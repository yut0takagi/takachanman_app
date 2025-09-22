from fastapi import APIRouter

router = APIRouter()


@router.post("/events")
def track_event() -> dict:
    return {"ok": True}

