from fastapi import APIRouter
from app.api.users.endpoints.user import router as admin_user_router
from app.api.users.endpoints.me import router as current_user_router

router = APIRouter()
router.include_router(admin_user_router)
router.include_router(current_user_router)
