from typing import List, Tuple
from uuid import UUID

from app.commons.pagination import CursorPaginationParams

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authorization.models import Role
from app.api.authorization.repositories.permission import PermissionRepository
from app.api.authorization.repositories.role import RoleRepository
from app.api.authorization.schema.role import RoleCreate, RoleUpdate


class RoleService:
    """Service layer for Role-related business logic."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.role_repository = RoleRepository(db_session)
        self.permission_repository = PermissionRepository(db_session)

    async def get_user_roles(self, user_id: UUID) -> List[Role]:
        """
        Get all roles a user has.

        Args:
            user_id: User ID

        Returns:
            List of roles the user has
        """
        return await self.role_repository.get_user_roles(user_id)

    async def create_role(self, data: RoleCreate) -> Role:
        """
        Create a new role with permissions and business logic validation.
        """
        # Check if role with same name exists
        existing = await self.role_repository.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role with name '{data.name}' already exists",
            )

        # If this is set as default role, unset any existing default
        if data.is_default:
            current_default = await self.role_repository.get_default_role()
            if current_default:
                await self.role_repository.update(
                    instance=current_default, fields={"is_default": False}
                )

        # Get permissions if IDs provided
        permissions = []
        if data.permission_ids:
            permissions = await self.permission_repository.get_multiple_by_ids(
                data.permission_ids
            )
            if len(permissions) != len(data.permission_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some permission IDs are invalid",
                )

        # Create role
        role_data = data.model_dump(exclude={"permission_ids"})
        role = await self.role_repository.create(**role_data)

        # Add permissions
        if permissions:
            role.permissions = permissions
            await self.db_session.commit()
            await self.db_session.refresh(role)

        return role

    async def update_role(self, role_id: UUID, data: RoleUpdate) -> Role:
        """
        Update a role with business logic validation.
        """
        # Get existing role
        role = await self.role_repository.get_with_permissions(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        # If name is being updated, check it doesn't conflict
        if data.name and data.name != role.name:
            existing = await self.role_repository.get_by_name(data.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Role with name '{data.name}' already exists",
                )

        # If this is set as default role, unset any existing default
        if data.is_default and not role.is_default:
            current_default = await self.role_repository.get_default_role()
            if current_default and current_default.id != role.id:
                await self.role_repository.update(
                    instance=current_default, fields={"is_default": False}
                )

        # Update permissions if provided
        if data.permission_ids is not None:
            permissions = await self.permission_repository.get_multiple_by_ids(
                data.permission_ids
            )
            if len(permissions) != len(data.permission_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some permission IDs are invalid",
                )
            role.permissions = permissions

        # Update other fields
        update_data = data.model_dump(exclude={"permission_ids"}, exclude_unset=True)
        updated_role = await self.role_repository.update(
            instance=role, fields=update_data
        )
        return updated_role

    async def get_role(self, role_id: UUID) -> Role:
        """
        Get a role by ID with proper error handling.
        """
        role = await self.role_repository.get_with_permissions(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        return role

    async def list_roles(
        self,
        pagination: CursorPaginationParams,
    ) -> Tuple[List[Role], bool, bool, str | None, str | None]:
        """
        List roles with cursor-based pagination.

        Args:
            pagination: Cursor pagination parameters

        Returns:
            Tuple containing:
            - List of roles
            - Whether there are more results after
            - Whether there are more results before
            - Next cursor if there are more results
            - Previous cursor if applicable
        """
        return await self.role_repository.list_with_cursor(params=pagination)

    async def delete_role(self, role_id: UUID) -> None:
        """
        Delete a role with proper error handling.
        """
        role = await self.role_repository.get(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        if role.is_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete a system role",
            )
        await self.role_repository.delete(role)
