from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users.models import User
from app.api.users.schema import UserUpdate, UserCreate
from app.api.users.repository import UserRepository
from app.api.authorization.models import Role, Permission
from app.api.authorization.services import RoleService
from app.commons.exceptions import NotFoundException, ValidationError
from app.commons.security import hash_password, verify_password


class UserService:
    """Service for user operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)
        self.role_service = RoleService(session)

    async def get_by_id(self, id: UUID) -> Optional[User]:
        """Get user by ID."""
        user = await self.repository.get_by_id_with_relations(id)
        if not user:
            raise NotFoundException(f"User with id {id} not found")
        return user

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> List[User]:
        """List users with pagination."""
        return await self.repository.list_with_relations(
            skip=skip,
            limit=limit,
            include_deleted=include_deleted,
        )

    async def count_users(self, include_deleted: bool = False) -> int:
        """Count total number of users."""
        return await self.repository.count(include_deleted=include_deleted)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.repository.get_by_email(email)

    async def get_by_phone(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        return await self.repository.get_by_phone(phone_number)

    async def create(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone_number: Optional[str] = None,
        middle_name: Optional[str] = None,
    ) -> User:
        """Create a new user."""
        # Check if email or phone already exists
        if await self.get_by_email(email):
            raise ValidationError(f"Email {email} is already taken")
        if phone_number and await self.get_by_phone(phone_number):
            raise ValidationError(f"Phone number {phone_number} is already taken")

        # Hash password
        password = hash_password(password)

        # Create user
        user = UserCreate(
            email=email,
            password=password,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            phone_number=phone_number,
        )

        return await self.repository.create(user)

    async def update(
        self,
        user_id: UUID,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ) -> User:
        """Update user details."""
        update_data = {}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if middle_name is not None:
            update_data["middle_name"] = middle_name
        if is_active is not None:
            update_data["is_active"] = is_active
        if is_verified is not None:
            update_data["is_verified"] = is_verified

        # Create a schema object for update
        update_schema = UserUpdate(**update_data)

        return await self.repository.update(id=user_id, schema=update_schema)

    async def delete(self, user: User) -> None:
        """Delete a user."""
        await self.repository.delete(user)

    async def add_role(self, user: User, role: Role) -> User:
        """Add role to user."""
        if role not in user.roles:
            await self.repository.add_role(user, role)
            await self.session.refresh(user)
        return user

    async def remove_role(self, user: User, role: Role) -> User:
        """Remove role from user."""
        if role in user.roles:
            await self.repository.remove_role(user, role)
            await self.session.refresh(user)
        return user

    async def add_direct_permission(self, user: User, permission: Permission) -> User:
        """Add direct permission to user."""
        if permission not in user.permissions:
            await self.repository.add_direct_permission(user, permission.id)
            await self.session.refresh(user)
        return user

    async def remove_direct_permission(
        self, user: User, permission: Permission
    ) -> User:
        """Remove direct permission from user."""
        if permission in user.permissions:
            await self.repository.remove_direct_permission(user, permission.id)
            await self.session.refresh(user)
        return user

    async def update_last_login(self, user: User) -> User:
        """Update user's last login timestamp."""
        user.last_login = datetime.now()
        return await self.repository.update(user)

    async def get_users_by_role(self, role: Role) -> List[User]:
        """Get all users with a specific role."""
        return await self.repository.get_users_by_role(role.id)

    async def verify_user(self, user_id: UUID) -> User:
        """Mark user as verified."""
        return await self.update(user_id=user_id, is_verified=True)

    async def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user."""
        return await self.update(user_id=user_id, is_active=False)

    async def activate_user(self, user_id: UUID) -> User:
        """Activate a user."""
        return await self.update(user_id=user_id, is_active=True)

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> User:
        """
        Change a user's password.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            Updated user

        Raises:
            ValidationError: If current password is incorrect
        """
        user = await self.get_by_id(user_id)

        # Verify current password
        if not verify_password(current_password, user.password):
            raise ValidationError("Current password is incorrect")

        # Hash and update new password
        update_data = {"password": hash_password(new_password)}
        update_schema = UserUpdate(**update_data)

        return await self.repository.update(id=user_id, schema=update_schema)
