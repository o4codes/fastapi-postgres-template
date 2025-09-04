from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.commons.models import TimestampMixin, UUIDMixin


class Notification(UUIDMixin, TimestampMixin):
    """In-app notification model."""

    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="info")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __str__(self) -> str:
        return f"{self.title} - {self.user_id}"
