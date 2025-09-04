from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.api.notifications.models import Notification
from app.api.notifications.schema import NotificationCreate
from app.commons.pagination import CursorPaginationParams


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(self, data: NotificationCreate) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=data.user_id,
            title=data.title,
            message=data.message,
            type=data.type,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_user_notifications(
        self,
        user_id: str,
        pagination: CursorPaginationParams,
        unread_only: bool = False,
    ):
        """Get notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read == False)  # noqa

        query = query.order_by(Notification.created_datetime.desc())

        # Apply pagination logic here (simplified)
        result = await self.db.execute(query.limit(pagination.limit))
        notifications = result.scalars().all()

        return notifications, False, False, None, None  # Simplified pagination response

    async def mark_as_read(self, notification_id: UUID, user_id: str) -> Notification:
        """Mark notification as read."""
        query = (
            update(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
            .values(is_read=True)
        )
        await self.db.execute(query)
        await self.db.commit()

        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one()

    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for user."""
        query = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa
        )
        result = await self.db.execute(query)
        return len(result.scalars().all())
