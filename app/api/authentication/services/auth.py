"""Authentication services."""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis

from app.api.users.models import User
from app.commons.email_sender import AsyncEmailSender
from app.configs.settings import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession, redis_client: Redis = None):
        self.db = db
        self.email_sender = AsyncEmailSender()
        self.redis_client = redis_client

    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP."""
        return str(secrets.randbelow(1000000)).zfill(6)

    async def cache_password_reset_otp(self, email: str, otp: str) -> None:
        """Cache password reset OTP in Redis."""
        key = f"password_reset:{email}"
        # Store OTP with 10 minute expiry
        await self.redis_client.set(key, otp, ex=600)

    async def verify_password_reset_otp(self, email: str, otp: str) -> bool:
        """Verify password reset OTP from Redis."""
        key = f"password_reset:{email}"
        stored_otp = await self.redis_client.get(key)
        if stored_otp and stored_otp == otp:
            await self.redis_client.delete(key)
            return True
        return False

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Get password hash."""
        return pwd_context.hash(password)

    def create_access_token(
        self, user_id: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create access token."""
        to_encode = {"sub": str(user_id)}
        if expires_delta:
            expire = datetime.now(tz=timezone.utc) + expires_delta
        else:
            expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return encoded_jwt

    async def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user with email and password."""
        # Get user by email
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return user

    async def request_password_reset(self, email: str) -> None:
        """Request password reset by sending OTP."""
        # Get user by email
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            # Don't reveal if email exists
            return

        # Generate OTP
        otp = self.generate_otp()

        # Cache OTP in Redis
        await self.cache_password_reset_otp(email, otp)

        # Send password reset email with OTP
        await self.email_sender.send_email(
            to=email,
            subject="Password Reset OTP",
            body=f"Your password reset OTP is: {otp} This OTP will expire in 10 minutes.",
        )

    async def reset_password(self, email: str, otp: str, new_password: str) -> None:
        """Reset password using OTP."""
        # Verify OTP
        if not await self.verify_password_reset_otp(email, otp):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP",
            )

        # Get user
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email",
            )

        # Update password
        user.password = self.get_password_hash(new_password)
        await self.db.commit()
