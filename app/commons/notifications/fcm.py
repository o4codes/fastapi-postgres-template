from typing import Optional, Dict, Any, List
from firebase_admin import messaging, credentials, initialize_app
from loguru import logger


class FCMService:
    """Firebase Cloud Messaging service for push notifications."""

    def __init__(self, service_account_path: Optional[str] = None):
        """Initialize FCM service with service account credentials."""
        if service_account_path:
            cred = credentials.Certificate(service_account_path)
            initialize_app(cred)

    async def send_to_token(
        self, token: str, title: str, body: str, data: Optional[Dict[str, str]] = None
    ) -> bool:
        """Send notification to a single device token."""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
            )

            response = messaging.send(message)
            logger.info(f"Successfully sent message: {response}")
            return True

        except Exception as e:
            logger.error(f"Failed to send FCM message: {e}")
            return False

    async def send_to_tokens(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Send notification to multiple device tokens."""
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
            )

            response = messaging.send_multicast(message)
            logger.info(f"Successfully sent {response.success_count} messages")

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": response.responses,
            }

        except Exception as e:
            logger.error(f"Failed to send FCM multicast message: {e}")
            return {"success_count": 0, "failure_count": len(tokens), "responses": []}

    async def send_to_topic(
        self, topic: str, title: str, body: str, data: Optional[Dict[str, str]] = None
    ) -> bool:
        """Send notification to a topic."""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                topic=topic,
            )

            response = messaging.send(message)
            logger.info(f"Successfully sent message to topic {topic}: {response}")
            return True

        except Exception as e:
            logger.error(f"Failed to send FCM topic message: {e}")
            return False
