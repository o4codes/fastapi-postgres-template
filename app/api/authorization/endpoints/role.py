from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authorization import schema as auth_schema
from app.api.authorization import services as auth_services
from app.configs.db import get_db_session
from app.commons.pagination import PaginationParams

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)

@router.post(
    "",
    response_model=auth_schema.RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
)
async def create_role(
    data: auth_schema.RoleCreate,
    db: AsyncSession = Depends(get_db_session),
) -> auth_schema.RoleResponse:
    """
    Create a new role with the provided data.

    Args:
        data: Role data
        db: Database session

    Returns:
        Created role
    """
    service = auth_services.RoleService(db)
    role = await service.create_role(data)
    return role

@router.get(
    "",
    response_model=List[auth_schema.RoleResponse],
    summary="List all roles",
)
async def list_roles(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db_session),
) -> List[auth_schema.RoleResponse]:
    """
    List all roles with pagination.

    Args:
        pagination: Pagination parameters
        db: Database session

    Returns:
        List of roles
    """
    service = auth_services.RoleService(db)
    roles = await service.list_roles(
        skip=pagination.skip,
        limit=pagination.limit,
    )
    return roles

@router.get(
    "/{role_id}",
    response_model=auth_schema.RoleResponse,
    summary="Get a specific role",
)
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> auth_schema.RoleResponse:
    """
    Get a specific role by ID.

    Args:
        role_id: Role ID
        db: Database session

    Returns:
        Role details
    """
    service = auth_services.RoleService(db)
    role = await service.get_role(role_id)
    return role

@router.patch(
    "/{role_id}",
    response_model=auth_schema.RoleResponse,
    summary="Update a role",
)
async def update_role(
    role_id: UUID,
    data: auth_schema.RoleUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> auth_schema.RoleResponse:
    """
    Update a role with the provided data.

    Args:
        role_id: Role ID
        data: Updated role data
        db: Database session

    Returns:
        Updated role
    """
    service = auth_services.RoleService(db)
    role = await service.update_role(role_id, data)
    return role

@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a role",
)
async def delete_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Delete a role.

    Args:
        role_id: Role ID
        db: Database session
    """
    service = auth_services.RoleService(db)
    await service.delete_role(role_id)
