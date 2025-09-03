"""Authentication endpoints."""
from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.api.authentication import schema as auth_schema
from app.api.authentication.services.auth import AuthService
from app.configs.db import get_db_session
from app.configs.cache import get_redis_client
from app.commons.schemas import ResponseWrapper
from app.commons.dependencies.auth import CurrentUser
from app.commons.dependencies.responses import ResponseWrapperRoute

router = APIRouter(
    prefix="/auth", tags=["Authentication"], route_class=ResponseWrapperRoute
)


@router.post(
    "/token",
    response_model=auth_schema.LoginResponse,
)
async def login(
    credentials: auth_schema.LoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> auth_schema.LoginResponse:
    """Login user with email and password."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(credentials.email, credentials.password)

    access_token = auth_service.create_access_token(user.id)
    return auth_schema.LoginResponse(access_token=access_token, token_type="bearer")


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_password_reset(
    request: auth_schema.PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> None:
    """Request password reset OTP."""
    auth_service = AuthService(db, redis)
    background_tasks.add_task(auth_service.request_password_reset, request.email)


@router.post(
    "/password-reset/confirm",
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


@router.post(
    "/2fa/setup",
    response_model=auth_schema.Enable2FAResponse,
)
async def setup_2fa(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> auth_schema.Enable2FAResponse:
    """Set up 2FA for current user."""
    auth_service = AuthService(db)
    return await auth_service.setup_2fa(current_user.id)


@router.post(
    "/2fa/enable",
)
async def enable_2fa(
    request: auth_schema.Enable2FARequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Enable 2FA for current user."""
    auth_service = AuthService(db)
    await auth_service.enable_2fa(current_user.id, request.totp_code)


@router.post(
    "/2fa/disable",
)
async def disable_2fa(
    request: auth_schema.Disable2FARequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Disable 2FA for current user."""
    auth_service = AuthService(db)
    await auth_service.disable_2fa(current_user.id, request.password, request.totp_code)
    auth_service = AuthService(db)
    await auth_service.disable_2fa(current_user.id, request.password, request.totp_code)


@router.get(
    "/2fa/status",
    response_model=ResponseWrapper[auth_schema.TwoFactorAuthInfo],
)
async def get_2fa_status(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> auth_schema.TwoFactorAuthInfo:
    """Get 2FA status for current user."""
    auth_service = AuthService(db)
    return await auth_service.get_2fa_info(current_user.id)
