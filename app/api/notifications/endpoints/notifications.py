from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.notifications import schema
from app.api.notifications.services import NotificationService
from app.configs.db import get_db_session
from app.commons.dependencies.auth import CurrentUser
from app.commons.pagination import CursorPaginationParams, CursorPaginatedResponse
from app.commons.schemas import APIResponse

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=CursorPaginatedResponse[schema.NotificationResponse],
    summary="Get user notifications",
)
async def get_notifications(
    current_user: CurrentUser,
    cursor: str | None = None,
    limit: int = 10,
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db_session),
) -> CursorPaginatedResponse[schema.NotificationResponse]:
    """Get notifications for current user."""
    service = NotificationService(db)
    pagination = CursorPaginationParams(cursor=cursor, limit=limit)

    (
        items,
        has_next,
        has_previous,
        next_cursor,
        previous_cursor,
    ) = await service.get_user_notifications(
        user_id=current_user.id,
        pagination=pagination,
        unread_only=unread_only,
    )

    return CursorPaginatedResponse.create(
        items=items,
        has_next=has_next,
        has_previous=has_previous,
        next_cursor=next_cursor,
        previous_cursor=previous_cursor,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=APIResponse[schema.NotificationResponse],
    summary="Mark notification as read",
)
async def mark_notification_read(
    notification_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> schema.NotificationResponse:
    """Mark a notification as read."""
    service = NotificationService(db)
    notification = await service.mark_as_read(notification_id, current_user.id)
    return APIResponse(
        status=True,
        message="Notification marked as read",
        data=notification,
    )


@router.get(
    "/unread-count",
    response_model=APIResponse[int],
    summary="Get unread notifications count",
)
async def get_unread_count(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db_session),
) -> int:
    """Get count of unread notifications."""
    service = NotificationService(db)
    count = await service.get_unread_count(current_user.id)
    return APIResponse(
        status=True,
        message="Retrieved unread count",
        data=count,
    )
