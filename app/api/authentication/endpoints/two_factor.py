"""Two-Factor Authentication endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.schema import two_factor as two_factor_schema
from app.api.authentication.services.two_factor import TwoFactorAuthService
from app.configs.db import get_db_session
from app.commons.dependencies.auth import CurrentUser
from app.commons.schemas import ResponseWrapper

router = APIRouter(prefix="/2fa", tags=["Two-Factor Authentication"])


@router.post(
    "/setup",
    response_model=ResponseWrapper[two_factor_schema.Enable2FAResponse],
)
async def setup_2fa(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> two_factor_schema.Enable2FAResponse:
    """Set up 2FA for current user."""
    two_factor_service = TwoFactorAuthService(db)
    return await two_factor_service.setup_2fa(current_user.id)


@router.post(
    "/enable",
    response_model=ResponseWrapper[None],
)
async def enable_2fa(
    request: two_factor_schema.Enable2FARequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Enable 2FA for current user."""
    two_factor_service = TwoFactorAuthService(db)
    await two_factor_service.enable_2fa(current_user.id, request.totp_code)


@router.post(
    "/disable",
    response_model=ResponseWrapper[None],
)
async def disable_2fa(
    request: two_factor_schema.Disable2FARequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Disable 2FA for current user."""
    two_factor_service = TwoFactorAuthService(db)
    await two_factor_service.disable_2fa(
        current_user.id, request.password, request.totp_code
    )


@router.get(
    "/status",
    response_model=ResponseWrapper[two_factor_schema.TwoFactorAuthInfo],
)
async def get_2fa_status(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> two_factor_schema.TwoFactorAuthInfo:
    """Get 2FA status for current user."""
    two_factor_service = TwoFactorAuthService(db)
    return await two_factor_service.get_2fa_info(current_user.id)
