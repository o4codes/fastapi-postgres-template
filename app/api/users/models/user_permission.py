from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.commons.models import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.api.users.models.user import User
    from app.api.authorization.models.permission import Permission

class UserPermission(UUIDMixin, TimestampMixin):
    """Association model for user direct permissions."""
    
    __tablename__ = "user_permissions"
    
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permission_id: Mapped[str] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", backref="user_permissions")
    permission: Mapped["Permission"] = relationship(
        "Permission",
        backref="user_permissions"
    )
