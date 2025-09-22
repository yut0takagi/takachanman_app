from fastapi import APIRouter

router = APIRouter()


@router.get("/invoice")
def get_invoice() -> dict:
    return {"invoice": {"id": "demo", "amount": 0}}

