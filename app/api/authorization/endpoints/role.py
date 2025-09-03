from uuid import UUID

from typing import Callable
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authorization import schema as auth_schema
from app.api.authorization import services as auth_services
from app.configs.db import get_db_session
from app.commons.pagination import CursorPaginationParams, CursorPaginatedResponse
from app.commons.dependencies.responses import wrap_response
from app.commons.schemas import ResponseWrapper

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@router.post(
    "",
    response_model=ResponseWrapper[auth_schema.RoleResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
)
async def create_role(
    data: auth_schema.RoleCreate,
    db: AsyncSession = Depends(get_db_session),
    response_wrapper: Callable = Depends(
        wrap_response(message="Role created successfully")
    ),
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
    response_model=CursorPaginatedResponse[auth_schema.RoleResponse],
    summary="List all roles",
)
async def list_roles(
    cursor: str | None = None,
    limit: int = 10,
    order_by: str | None = None,
    direction: str = "forward",
    db: AsyncSession = Depends(get_db_session),
    response_wrapper: Callable = Depends(wrap_response(paginated=True)),
) -> CursorPaginatedResponse[auth_schema.RoleResponse]:
    """
    List all roles with cursor-based pagination.

    Args:
        cursor: Cursor for current position
        limit: Number of items per page (default: 10)
        order_by: Field to order by. Options: id, name, created_datetime, updated_datetime (default: id)
        direction: Pagination direction: 'forward' or 'backward' (default: forward)
        db: Database session

    Returns:
        Cursor paginated list of roles
    """
    service = auth_services.RoleService(db)

    pagination = CursorPaginationParams(
        cursor=cursor, limit=limit, order_by=order_by, direction=direction
    )

    (
        items,
        has_next,
        has_previous,
        next_cursor,
        previous_cursor,
    ) = await service.list_roles(
        pagination=pagination,
    )

    return CursorPaginatedResponse.create(
        items=items,
        has_next=has_next,
        has_previous=has_previous,
        next_cursor=next_cursor,
        previous_cursor=previous_cursor,
    )


@router.get(
    "/{role_id}",
    response_model=ResponseWrapper[auth_schema.RoleResponse],
    summary="Get a specific role",
)
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    response_wrapper: Callable = Depends(wrap_response()),
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
    response_model=ResponseWrapper[auth_schema.RoleResponse],
    summary="Update a role",
)
async def update_role(
    role_id: UUID,
    data: auth_schema.RoleUpdate,
    db: AsyncSession = Depends(get_db_session),
    response_wrapper: Callable = Depends(
        wrap_response(message="Role updated successfully")
    ),
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
