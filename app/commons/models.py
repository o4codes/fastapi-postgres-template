from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

class UUIDMixin:
    """Mixin that adds a UUID primary key column to a model."""
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )

class TimestampMixin:
    """Mixin that adds created_datetime and updated_datetime columns to a model."""
    created_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

class SoftDeleteMixin:
    """Mixin that adds deleted_datetime column to a model for soft deletion."""
    deleted_datetime: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

class AuditMixin:
    """Mixin that adds audit fields (created_by, updated_by) to a model."""
    created_by: Mapped[Optional[UUID]] = mapped_column(
        nullable=True,
    )
    updated_by: Mapped[Optional[UUID]] = mapped_column(
        nullable=True,
    )

class SlugMixin:
    """Mixin that adds a slug column to a model."""
    slug: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        nullable=False,
        index=True,
    )
