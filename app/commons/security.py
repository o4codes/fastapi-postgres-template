"""Security utilities for the application."""

from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def encode_jwt(
    payload: dict,
    key: str,
    algorithm: str = "HS256",
    expires_datetime: datetime = None,
) -> str:
    """Encode a JWT."""
    if not expires_datetime:
        expires_datetime = datetime.now(tz=timezone.utc) + timedelta(minutes=15)

    to_encode = payload.copy()
    to_encode.update({"exp": expires_datetime})
    encoded_jwt = jwt.encode(to_encode, key, algorithm=algorithm)
    return encoded_jwt


def decode_jwt(token: str, key: str, algorithms: list) -> dict:
    """Decode a JWT."""
    return jwt.decode(token, key, algorithms=algorithms)
