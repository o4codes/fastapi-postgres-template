from datetime import datetime
import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.commons.models import TimestampMixin, UUIDMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.api.authorization.models import Role, Permission


class User(UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """User model with role-based access control."""

    __tablename__ = "users"

    public_id: Mapped[str] = mapped_column(
        String(length=36),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    email: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        nullable=False,
        index=True,
    )
    phone_number: Mapped[str] = mapped_column(
        String(length=20),
        unique=True,
        nullable=True,
        index=True,
    )
    password: Mapped[str] = mapped_column(
        String(length=255),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(
        String(length=100),
        nullable=False,
    )
    middle_name: Mapped[str] = mapped_column(
        String(length=100),
        nullable=True,
    )
    last_name: Mapped[str] = mapped_column(
        String(length=100),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    last_login_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        lazy="selectin",  # Eager loading for roles
        viewonly=True,
    )

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="user_permissions",
        lazy="selectin",  # Eager loading for direct permissions
        viewonly=True,
    )

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        name_parts = [self.first_name]
        if self.middle_name:
            name_parts.append(self.middle_name)
        name_parts.append(self.last_name)
        return " ".join(name_parts)

    def has_permission(self, permission_code: str) -> bool:
        """Check if user has a specific permission either directly or through roles."""
        # Check direct permissions
        if any(p.code == permission_code for p in self.permissions):
            return True

        # Check permissions through roles
        return any(role.has_permission(permission_code) for role in self.roles)

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)
