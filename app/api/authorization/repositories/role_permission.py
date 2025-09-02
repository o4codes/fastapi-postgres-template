from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.authorization.models import RolePermission
from app.api.authorization.schema.role_permission import (
    RolePermissionCreate,
    RolePermissionUpdate,
)
from app.commons.repository import BaseRepository


class RolePermissionRepository(
    BaseRepository[RolePermission, RolePermissionCreate, RolePermissionUpdate]
):
    """Repository for handling direct database operations on RolePermission entities."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(RolePermission, db_session)

    async def get_by_role_and_permission(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> Optional[RolePermission]:
        """Get a role permission by role and permission IDs."""
        return await self.get_by_attributes(
            role_id=role_id,
            permission_id=permission_id,
        )

    async def get_by_role(
        self,
        role_id: UUID,
    ) -> List[RolePermission]:
        """Get all role permissions for a role."""
        query = (
            select(self.model)
            .where(self.model.role_id == role_id)
            .options(
                selectinload(self.model.permission),
                selectinload(self.model.role),
            )
        )
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
