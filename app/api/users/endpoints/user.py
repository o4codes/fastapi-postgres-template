from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users import schema
from app.api.users.services import UserService
from app.configs.db import get_db_session
from app.commons.pagination import CursorPaginationParams, CursorPaginatedResponse
from app.commons.schemas import APIResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=APIResponse[schema.UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    # dependencies=[
    #     Depends(requires_permissions("user:create")),
    #     Depends(requires_roles("admin", "user_manager")),
    # ],
)
async def create_user(
    data: schema.UserCreate,
    db: AsyncSession = Depends(get_db_session),
) -> schema.UserResponse:
    """
    Create a new user.

    Args:
        data: User creation data
        db: Database session

    Returns:
        Created user details
    """
    service = UserService(db)
    user = await service.create(
        email=data.email,
        password=data.password,  # TODO: Add password hashing
        first_name=data.first_name,
        middle_name=data.middle_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
    )
    return APIResponse(status=True, message="User created successfully", data=user)


@router.get(
    "",
    response_model=CursorPaginatedResponse[schema.UserResponse],
    summary="List all users",
    # dependencies=[Depends(requires_permissions("user:list"))],
)
async def list_users(
    cursor: str | None = None,
    limit: int = 10,
    order_by: str | None = None,
    direction: str = "forward",
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db_session),
) -> CursorPaginatedResponse[schema.UserResponse]:
    """
    List all users with cursor-based pagination.

    Args:
        cursor: Cursor for current position
        limit: Number of items per page (default: 10)
        order_by: Field to order by. Options: id, email, created_datetime, updated_datetime,
            first_name, last_name (default: id)
        direction: Pagination direction: 'forward' or 'backward' (default: forward)
        include_deleted: Whether to include soft-deleted users
        db: Database session

    Returns:
        Cursor paginated list of users
    """
    service = UserService(db)

    pagination = CursorPaginationParams(
        cursor=cursor, limit=limit, order_by=order_by, direction=direction
    )

    (
        items,
        has_next,
        has_previous,
        next_cursor,
        previous_cursor,
    ) = await service.list_users(
        pagination=pagination,
        include_deleted=include_deleted,
    )

    return CursorPaginatedResponse.create(
        items=items,
        has_next=has_next,
        has_previous=has_previous,
        next_cursor=next_cursor,
        previous_cursor=previous_cursor,
    )


@router.get(
    "/{user_id}",
    response_model=APIResponse[schema.UserResponse],
    summary="Get user details",
)
async def get_user(
    user_id: UUID,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db_session),
) -> schema.UserResponse:
    """
    Get user details by ID.

    Args:
        user_id: User ID
        include_deleted: Whether to include soft-deleted users
        db: Database session

    Returns:
        User details
    """
    service = UserService(db)
    user = await service.get_by_id(user_id)
    return APIResponse(status=True, message="Retrieved User details", data=user)


@router.patch(
    "/{user_id}",
    response_model=APIResponse[schema.UserResponse],
    summary="Update user details",
)
async def update_user(
    user_id: UUID,
    data: schema.UserUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> schema.UserResponse:
    """
    Update user details.

    Args:
        user_id: User ID
        data: User update data
        db: Database session

    Returns:
        Updated user details
    """
    service = UserService(db)
    updated_user = await service.update(
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
        middle_name=data.middle_name,
        is_active=data.is_active,
        is_verified=data.is_verified,
    )
    return APIResponse(
        status=True,
        message="User details updated successfully",
        data=updated_user,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    # dependencies=[
    #     Depends(requires_permissions("user:delete")),
    #     Depends(requires_roles("admin")),
    # ],
)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete (soft-delete) a user.

    Args:
        user_id: User ID
        db: Database session
    """
    service = UserService(db)
    user = await service.get_by_id(str(user_id))
    await service.delete(user)


@router.post(
    "/{user_id}/change-password",
    response_model=APIResponse[schema.UserResponse],
    summary="Change user password",
)
async def change_password(
    user_id: UUID,
    data: schema.UserPasswordUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> schema.UserResponse:
    """
    Change user password.

    Args:
        user_id: User ID
        data: Password update data
        db: Database session

    Returns:
        Updated user details
    """
    service = UserService(db)
    user = await service.get_by_id(str(user_id))
    updated_user = await service.change_password(
        user,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return APIResponse(
        status=True,
        message="Password changed successfully",
        data=updated_user,
    )


@router.post(
    "/{user_id}/verify",
    response_model=APIResponse[schema.UserResponse],
    summary="Verify a user",
)
async def verify_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> schema.UserResponse:
    """
    Mark a user as verified.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Updated user details
    """
    service = UserService(db)
    verified_user = await service.verify_user(user_id)
    return APIResponse(
        status=True,
        message="User verified successfully",
        data=verified_user,
    )
