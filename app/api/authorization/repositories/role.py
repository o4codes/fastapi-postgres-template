from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.authorization.models import Role
from app.api.authorization.repositories.role_queries import get_user_roles_query
from app.commons.repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for handling direct database operations on Role entities."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Role, db_session)

    async def get_with_permissions(self, id: UUID) -> Optional[Role]:
        """Get a role with its permissions loaded."""
        query = (
            select(self.model)
            .options(selectinload(self.model.permissions))
            .where(self.model.id == id)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get a role by its name."""
        return await self.get_by_attribute(name=name)

    async def get_default_role(self) -> Optional[Role]:
        """Get the default role."""
        return await self.get_by_attribute(is_default=True)

    async def get_user_roles(self, user_id: UUID) -> List[Role]:
        """
        Get all roles a user has.

        Args:
            user_id: User ID

        Returns:
            List of roles the user has
        """
        query = get_user_roles_query(user_id)
        result = await self.db_session.execute(query)
        return list(result.scalars().unique())
