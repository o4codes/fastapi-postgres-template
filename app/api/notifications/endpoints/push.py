from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.notifications import schema
from app.api.notifications.services import PushNotificationService
from app.configs.db import get_db_session
from app.commons.dependencies.auth import CurrentUser
from app.commons.dependencies.permissions import requires_permissions
from app.commons.schemas import APIResponse

router = APIRouter(
    prefix="/push",
    tags=["Notifications"],
)


@router.post(
    "/register",
    response_model=APIResponse[schema.PushTokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register push notification token",
)
async def register_push_token(
    data: schema.PushTokenCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> schema.PushTokenResponse:
    """Register a push notification token for current user."""
    service = PushNotificationService(db)
    token = await service.register_token(current_user.id, data)
    return APIResponse(
        status=True,
        message="Push token registered successfully",
        data=token,
    )


@router.delete(
    "/unregister",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unregister push notification token",
)
async def unregister_push_token(
    token: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Unregister a push notification token."""
    service = PushNotificationService(db)
    await service.remove_token(current_user.id, token)


@router.post(
    "/send",
    response_model=APIResponse[bool],
    summary="Send push notification",
    dependencies=[Depends(requires_permissions("notification:send"))],
)
async def send_push_notification(
    data: schema.PushNotificationSend,
    db: AsyncSession = Depends(get_db_session),
) -> bool:
    """Send push notification to users."""
    service = PushNotificationService(db)
    success = await service.send_push_notification(data)
    return APIResponse(
        status=True,
        message="Push notification sent"
        if success
        else "Failed to send push notification",
        data=success,
    )
