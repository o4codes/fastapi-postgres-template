from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users import schema
from app.api.users.services import UserService
from app.configs.db import get_db_session
from app.commons.dependencies.auth import CurrentUser
from app.commons.schemas import APIResponse

router = APIRouter(
    prefix="/users/me",
    tags=["Users"],
)


@router.get(
    "",
    response_model=APIResponse[schema.UserResponse],
    summary="Get current user profile",
)
async def get_current_user(
    current_user: CurrentUser,
) -> schema.UserResponse:
    """
    Get current user profile.

    Returns:
        Current user details
    """
    return APIResponse(status=True, message="Retrieved user profile", data=current_user)


@router.patch(
    "",
    response_model=APIResponse[schema.UserResponse],
    summary="Update current user profile",
)
async def update_current_user(
    data: schema.UserUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> schema.UserResponse:
    """
    Update current user profile.

    Args:
        data: User update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user details
    """
    service = UserService(db)
    updated_user = await service.update(
        user_id=current_user.id,
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
    )
    return APIResponse(
        status=True,
        message="Profile updated successfully",
        data=updated_user,
    )


@router.post(
    "/change-password",
    response_model=APIResponse[schema.UserResponse],
    summary="Change current user password",
)
async def change_current_user_password(
    data: schema.UserPasswordUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> schema.UserResponse:
    """
    Change current user password.

    Args:
        data: Password update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user details
    """
    service = UserService(db)
    updated_user = await service.change_password(
        current_user,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return APIResponse(
        status=True,
        message="Password changed successfully",
        data=updated_user,
    )


@router.post(
    "/verify",
    response_model=APIResponse[schema.UserResponse],
    summary="Verify current user",
)
async def verify_current_user(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> schema.UserResponse:
    """
    Mark current user as verified.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user details
    """
    service = UserService(db)
    verified_user = await service.verify_user(current_user.id)
    return APIResponse(
        status=True,
        message="User verified successfully",
        data=verified_user,
    )
