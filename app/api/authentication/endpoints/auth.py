"""Authentication endpoints."""


from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.authentication import schema as auth_schema
from app.api.authentication.services.auth import AuthService
from app.configs.db import get_db_session
from app.configs.cache import get_redis_client
from app.commons.schemas import APIResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/token",
    response_model=APIResponse[auth_schema.LoginResponse],
)
async def login(
    credentials: auth_schema.LoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> auth_schema.LoginResponse:
    """Login user with email and password."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(credentials.email, credentials.password)

    access_token = auth_service.create_access_token(user.id)
    return APIResponse(
        status=True,
        message="Login successful",
        data=auth_schema.LoginResponse(access_token=access_token, token_type="bearer"),
    )


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=APIResponse[None],
)
async def request_password_reset(
    reset_data: auth_schema.PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> None:
    """Request password reset OTP."""
    auth_service = AuthService(db, redis)
    background_tasks.add_task(auth_service.request_password_reset, reset_data.email)
    return APIResponse(status=True, message="Password reset request sent", data=None)


@router.post(
    "/password-reset/confirm",
    response_model=APIResponse[None],
)
async def reset_password(
    reset_data: auth_schema.PasswordResetConfirm,
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> None:
    """Reset password using OTP."""
    auth_service = AuthService(db, redis)
    await auth_service.reset_password(
        reset_data.email, reset_data.otp, reset_data.new_password
    )
    return APIResponse(status=True, message="Password reset successful", data=None)
