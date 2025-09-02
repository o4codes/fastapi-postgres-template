from datetime import datetime
from typing import Optional, List
from pydantic import EmailStr, Field, field_validator

from app.api.authorization.schema import RoleResponse, PermissionResponse
from app.commons.schemas import (
    BaseSchema,
    TimestampSchema,
    UUIDSchema,
    SoftDeleteSchema,
)


class UserBase(BaseSchema):
    """Base schema for user data."""

    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    first_name: str = Field(..., max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., max_length=100)

    @field_validator("phone_number")
    def validate_phone_number(cls, v):
        if v:
            # Remove any whitespace and common separators
            v = "".join(filter(str.isdigit, v))
            if not (10 <= len(v) <= 15):  # Standard phone number lengths
                raise ValueError("Phone number must be between 10 and 15 digits")
            return f"+{v}"  # Store with + prefix
        return v


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "phone_number": "+1234567890",
                "first_name": "John",
                "middle_name": "William",
                "last_name": "Doe",
                "password": "securepassword123",
            }
        }


class UserUpdate(BaseSchema):
    """Schema for updating user details."""

    phone_number: Optional[str] = Field(None, max_length=20)
    first_name: Optional[str] = Field(None, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

    @field_validator("phone_number")
    def validate_phone_number(cls, v):
        if v:
            v = "".join(filter(str.isdigit, v))
            if not (10 <= len(v) <= 15):
                raise ValueError("Phone number must be between 10 and 15 digits")
            return f"+{v}"
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+1234567890",
                "first_name": "John",
                "middle_name": "William",
                "last_name": "Doe",
                "is_active": True,
                "is_verified": True,
            }
        }


class UserResponse(UserBase, UUIDSchema, TimestampSchema, SoftDeleteSchema):
    """Schema for user response data."""

    public_id: str
    is_active: bool
    is_verified: bool
    last_login_datetime: Optional[datetime]
    roles: List[RoleResponse]
    permissions: List[PermissionResponse]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "public_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john.doe@example.com",
                "phone_number": "+1234567890",
                "first_name": "John",
                "middle_name": "William",
                "last_name": "Doe",
                "is_active": True,
                "is_verified": True,
                "last_login": "2025-09-02T10:00:00Z",
                "created_at": "2025-09-02T09:00:00Z",
                "updated_at": "2025-09-02T09:00:00Z",
                "roles": [],
                "permissions": [],
            }
        }


class UserPasswordUpdate(BaseSchema):
    """Schema for updating user password."""

    current_password: str
    new_password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword123",
            }
        }


class UserList(BaseSchema):
    """Schema for paginated user list."""

    total: int
    items: List[UserResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 1,
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "public_id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "john.doe@example.com",
                        "phone_number": "+1234567890",
                        "first_name": "John",
                        "middle_name": "William",
                        "last_name": "Doe",
                        "is_active": True,
                        "is_verified": True,
                        "last_login": "2025-09-02T10:00:00Z",
                        "created_at": "2025-09-02T09:00:00Z",
                        "updated_at": "2025-09-02T09:00:00Z",
                        "roles": [],
                        "permissions": [],
                    }
                ],
            }
        }
