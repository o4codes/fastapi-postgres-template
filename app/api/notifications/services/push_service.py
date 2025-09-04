from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.api.notifications.models import PushToken
from app.api.notifications.schema import PushTokenCreate, PushNotificationSend
from loguru import logger


class PushNotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_token(self, user_id: str, data: PushTokenCreate) -> PushToken:
        """Register a push notification token."""
        # Remove existing token if exists
        await self.db.execute(delete(PushToken).where(PushToken.token == data.token))

        token = PushToken(
            user_id=user_id,
            token=data.token,
            platform=data.platform,
        )
        self.db.add(token)
        await self.db.commit()
        await self.db.refresh(token)
        return token

    async def remove_token(self, user_id: str, token: str) -> bool:
        """Remove a push notification token."""
        result = await self.db.execute(
            delete(PushToken).where(
                PushToken.user_id == user_id, PushToken.token == token
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def get_user_tokens(self, user_id: str) -> list[PushToken]:
        """Get all tokens for a user."""
        result = await self.db.execute(
            select(PushToken).where(PushToken.user_id == user_id)
        )
        return result.scalars().all()

    async def send_push_notification(self, data: PushNotificationSend) -> bool:
        """Send push notification to users."""
        try:
            if data.user_ids:
                # Send to specific users
                query = select(PushToken).where(PushToken.user_id.in_(data.user_ids))
            else:
                # Send to all users
                query = select(PushToken)

            result = await self.db.execute(query)
            tokens = result.scalars().all()

            # Here you would integrate with actual push notification service
            # like Firebase FCM, Apple Push Notification service, etc.
            logger.info(f"Sending push notification to {len(tokens)} devices")
            logger.info(f"Title: {data.title}, Message: {data.message}")

            # Placeholder for actual push notification logic
            for token in tokens:
                logger.info(
                    f"Sending to {token.platform} device: {token.token[:20]}..."
                )

            return True
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False
