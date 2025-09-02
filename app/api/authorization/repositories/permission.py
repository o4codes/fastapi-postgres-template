from typing import Optional
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authorization import models as auth_models
from app.api.authorization.repositories import permission_queries
from app.commons.repository import BaseRepository


class PermissionRepository(BaseRepository[auth_models.Permission]):
    """Repository for handling direct database operations on Permission entities."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(auth_models.Permission, db_session)

    async def get_by_code(self, code: str) -> Optional[auth_models.Permission]:
        """Get a permission by its code."""
        return await self.get_by_attributes(code=code)

    async def get_multiple_by_ids(
        self, ids: list[UUID]
    ) -> list[auth_models.Permission]:
        """Get multiple permissions by their IDs."""
        query = select(self.model).where(self.model.id.in_(ids))
        result = await self.db_session.execute(query)
        return list(result.scalars().all())

    async def get_user_permissions(self, user_id: UUID) -> List[auth_models.Permission]:
        """
        Get all permissions a user has through their roles.

        Args:
            user_id: User ID

        Returns:
            List of permissions the user has
        """
        query = permission_queries.get_user_permissions_query(user_id)
        result = await self.db_session.execute(query)
        return list(result.scalars().unique())
