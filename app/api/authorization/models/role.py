from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.commons.models import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.api.authorization.models.permission import Permission
    from app.api.authorization.models.role_permission import RolePermission


class Role(UUIDMixin, TimestampMixin):
    """Role model for user roles and permissions."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(length=100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        String(length=255),
        nullable=True,
    )
    is_default: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    is_system: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    # Relationships
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        lazy="selectin",  # Eager loading for permissions
        viewonly=True,  # Make this a read-only relationship
    )

    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return self.name

    def has_permission(self, permission_code: str) -> bool:
        """Check if role has a specific permission."""
        return any(p.code == permission_code for p in self.permissions)
