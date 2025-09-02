from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authorization import schema as auth_schema
from app.api.authorization import services as auth_services
from app.configs.db import get_db_session
from app.commons.pagination import PaginationParams

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.post(
    "",
    response_model=auth_schema.PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new permission",
)
async def create_permission(
    data: auth_schema.PermissionCreate,
    db: AsyncSession = Depends(get_db_session),
) -> auth_schema.PermissionResponse:
    """
    Create a new permission with the provided data.

    Args:
        data: Permission data
        db: Database session

    Returns:
        Created permission
    """
    service = auth_services.PermissionService(db)
    permission = await service.create_permission(data)
    return permission


@router.get(
    "",
    response_model=List[auth_schema.PermissionResponse],
    summary="List all permissions",
)
async def list_permissions(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db_session),
) -> List[auth_schema.PermissionResponse]:
    """
    List all permissions with pagination.

    Args:
        pagination: Pagination parameters
        db: Database session

    Returns:
        List of permissions
    """
    service = auth_services.PermissionService(db)
    permissions = await service.list_permissions(
        skip=pagination.skip,
        limit=pagination.limit,
    )
    return permissions


@router.get(
    "/{permission_id}",
    response_model=auth_schema.PermissionResponse,
    summary="Get a specific permission",
)
async def get_permission(
    permission_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> auth_schema.PermissionResponse:
    """
    Get a specific permission by ID.

    Args:
        permission_id: Permission ID
        db: Database session

    Returns:
        Permission details
    """
    service = auth_services.PermissionService(db)
    permission = await service.get_permission(permission_id)
    return permission


@router.patch(
    "/{permission_id}",
    response_model=auth_schema.PermissionResponse,
    summary="Update a permission",
)
async def update_permission(
    permission_id: UUID,
    data: auth_schema.PermissionUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> auth_schema.PermissionResponse:
    """
    Update a permission with the provided data.

    Args:
        permission_id: Permission ID
        data: Updated permission data
        db: Database session

    Returns:
        Updated permission
    """
    service = auth_services.PermissionService(db)
    permission = await service.update_permission(permission_id, data)
    return permission


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a permission",
)
async def delete_permission(
    permission_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete a permission.

    Args:
        permission_id: Permission ID
        db: Database session
    """
    service = auth_services.PermissionService(db)
    await service.delete_permission(permission_id)
