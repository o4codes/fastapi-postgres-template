from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.api.notifications.models import PushToken
from app.api.notifications.schema import PushTokenCreate, PushNotificationSend
from app.commons.notifications import FCMService
from loguru import logger


class PushNotificationService:
    def __init__(self, db: AsyncSession, fcm_service: FCMService = None):
        self.db = db
        self.fcm_service = fcm_service or FCMService()

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
                query = select(PushToken).where(PushToken.user_id.in_(data.user_ids))
            else:
                query = select(PushToken)

            result = await self.db.execute(query)
            tokens = result.scalars().all()

            if not tokens:
                logger.warning("No push tokens found for notification")
                return False

            token_strings = [token.token for token in tokens]

            fcm_result = await self.fcm_service.send_to_tokens(
                tokens=token_strings,
                title=data.title,
                body=data.message,
                data=data.data,
            )

            logger.info(
                f"FCM result: {fcm_result['success_count']} success, {fcm_result['failure_count']} failures"
            )
            return fcm_result["success_count"] > 0

        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False
