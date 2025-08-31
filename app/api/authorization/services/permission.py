from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authorization.models import Permission
from app.api.authorization.repositories.permission import PermissionRepository
from app.api.authorization.schema.permission import PermissionCreate, PermissionUpdate

class PermissionService:
    """Service layer for Permission-related business logic."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.repository = PermissionRepository(db_session)

    async def create_permission(self, data: PermissionCreate) -> Permission:
        """
        Create a new permission with business logic validation.
        """
        # Check if permission with same code exists
        existing = await self.repository.get_by_code(data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission with code '{data.code}' already exists"
            )

        # Create permission
        permission = await self.repository.create(**data.model_dump())
        return permission

    async def update_permission(
        self,
        permission_id: UUID,
        data: PermissionUpdate
    ) -> Permission:
        """
        Update a permission with business logic validation.
        """
        # Get existing permission
        permission = await self.repository.get(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )

        # If code is being updated, check it doesn't conflict
        if data.code and data.code != permission.code:
            existing = await self.repository.get_by_code(data.code)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Permission with code '{data.code}' already exists"
                )

        # Update permission
        updated_permission = await self.repository.update(
            permission,
            **data.model_dump(exclude_unset=True)
        )
        return updated_permission

    async def get_permission(self, permission_id: UUID) -> Optional[Permission]:
        """
        Get a permission by ID with proper error handling.
        """
        permission = await self.repository.get(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return permission

    async def list_permissions(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> list[Permission]:
        """
        List permissions with pagination.
        """
        return await self.repository.list(skip=skip, limit=limit)

    async def delete_permission(self, permission_id: UUID) -> None:
        """
        Delete a permission with proper error handling.
        """
        permission = await self.repository.get(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        await self.repository.delete(permission)
