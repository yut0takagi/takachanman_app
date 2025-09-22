from fastapi import APIRouter

from .endpoints import invoice, refund


router = APIRouter(prefix="/payments", tags=["payments"])

router.include_router(invoice.router)
router.include_router(refund.router)

