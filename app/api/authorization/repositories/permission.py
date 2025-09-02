from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authorization.models import Permission
from app.commons.repository import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    """Repository for handling direct database operations on Permission entities."""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Permission, db_session)

    async def get_by_code(self, code: str) -> Optional[Permission]:
        """Get a permission by its code."""
        return await self.get_by_attributes(code=code)

    async def get_multiple_by_ids(self, ids: list[UUID]) -> list[Permission]:
        """Get multiple permissions by their IDs."""
        query = select(self.model).where(self.model.id.in_(ids))
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
