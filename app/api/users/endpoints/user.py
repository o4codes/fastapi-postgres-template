from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users import schema
from app.api.users.services import UserService
from app.configs.db import get_db_session
from app.commons.pagination import PaginationParams

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post(
    "",
    response_model=schema.UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
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
    return user

@router.get(
    "",
    response_model=schema.UserList,
    summary="List all users",
)
async def list_users(
    pagination: PaginationParams = Depends(),
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db_session),
) -> schema.UserList:
    """
    List all users with pagination.

    Args:
        pagination: Pagination parameters
        include_deleted: Whether to include soft-deleted users
        db: Database session

    Returns:
        List of users
    """
    service = UserService(db)
    users = await service.list_users(
        skip=pagination.skip,
        limit=pagination.limit,
        include_deleted=include_deleted,
    )
    total = await service.count_users(include_deleted=include_deleted)
    return schema.UserList(total=total, items=users)

@router.get(
    "/{user_id}",
    response_model=schema.UserResponse,
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
    return user

@router.patch(
    "/{user_id}",
    response_model=schema.UserResponse,
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
    return updated_user

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
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
    "/{user_id}/restore",
    response_model=schema.UserResponse,
    summary="Restore a deleted user",
)
async def restore_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> schema.UserResponse:
    """
    Restore a soft-deleted user.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        Restored user details
    """
    service = UserService(db)
    user = await service.get_by_id(str(user_id), include_deleted=True)
    restored_user = await service.restore(user)
    return restored_user

@router.post(
    "/{user_id}/change-password",
    response_model=schema.UserResponse,
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
    return updated_user

@router.post(
    "/{user_id}/verify",
    response_model=schema.UserResponse,
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
    return verified_user
