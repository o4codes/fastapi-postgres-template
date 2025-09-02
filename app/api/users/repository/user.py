from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.authorization.models import Role
from app.api.users.models import User, UserRole, UserPermission
from app.commons.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user operations."""

    model = User

    async def get_by_email(
        self, email: str, include_deleted: bool = False
    ) -> Optional[User]:
        """Get user by email."""
        query = select(self.model).where(self.model.email == email)
        if not include_deleted:
            query = query.where(self.model.deleted_datetime.is_(None))
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_phone(
        self, phone_number: str, include_deleted: bool = False
    ) -> Optional[User]:
        """Get user by phone number."""
        query = select(self.model).where(self.model.phone_number == phone_number)
        if not include_deleted:
            query = query.where(self.model.deleted_datetime.is_(None))
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(
        self, id: str, include_deleted: bool = False
    ) -> Optional[User]:
        """Get user by ID with roles and permissions."""
        query = (
            select(self.model)
            .options(
                selectinload(self.model.roles), selectinload(self.model.permissions)
            )
            .where(self.model.id == id)
        )
        if not include_deleted:
            query = query.where(self.model.deleted_datetime.is_(None))
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def add_role(self, user: User, role: Role) -> UserRole:
        """Add role to user."""
        user_role = UserRole(user_id=user.id, role_id=role.id)
        self.db_session.add(user_role)
        return user_role

    async def remove_role(self, user: User, role: Role) -> None:
        """Remove role from user."""
        query = select(UserRole).where(
            UserRole.user_id == user.id, UserRole.role_id == role.id
        )
        result = await self.db_session.execute(query)
        user_role = result.scalar_one_or_none()
        if user_role:
            await self.db_session.delete(user_role)

    async def add_direct_permission(
        self, user: User, permission_id: str
    ) -> UserPermission:
        """Add direct permission to user."""
        user_permission = UserPermission(user_id=user.id, permission_id=permission_id)
        self.db_session.add(user_permission)
        return user_permission

    async def remove_direct_permission(self, user: User, permission_id: str) -> None:
        """Remove direct permission from user."""
        query = select(UserPermission).where(
            UserPermission.user_id == user.id,
            UserPermission.permission_id == permission_id,
        )
        result = await self.db_session.execute(query)
        user_permission = result.scalar_one_or_none()
        if user_permission:
            await self.db_session.delete(user_permission)

    async def get_users_by_role(
        self, role_id: str, include_deleted: bool = False
    ) -> List[User]:
        """Get all users with a specific role."""
        query = select(self.model).join(UserRole).where(UserRole.role_id == role_id)
        if not include_deleted:
            query = query.where(self.model.deleted_datetime.is_(None))
        result = await self.db_session.execute(query)
        return list(result.scalars().all())
