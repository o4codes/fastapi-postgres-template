from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.commons.models import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.api.users.models.user import User
    from app.api.authorization.models.role import Role

class UserRole(UUIDMixin, TimestampMixin):
    """Association model for user roles."""
    
    __tablename__ = "user_roles"
    
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", backref="user_roles")
    role: Mapped["Role"] = relationship("Role", backref="user_roles")
