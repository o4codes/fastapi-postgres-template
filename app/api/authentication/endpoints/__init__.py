"""Authentication endpoints."""
from fastapi import APIRouter

from app.api.authentication.endpoints.auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)
