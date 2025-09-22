from fastapi import APIRouter

router = APIRouter()


@router.post("/refund")
def create_refund() -> dict:
    return {"status": "refunded", "id": "demo"}

