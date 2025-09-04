from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class NotificationBase(BaseModel):
    title: str
    message: str
    type: str = "info"


class NotificationCreate(NotificationBase):
    user_id: str


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    is_read: bool
    created_datetime: datetime
    updated_datetime: datetime

    class Config:
        from_attributes = True
