from fastapi import APIRouter
from .notifications import router as notifications_router
from .push import router as push_router

router = APIRouter()
router.include_router(notifications_router)
router.include_router(push_router)
