"""Cache configuration module."""
from typing import AsyncGenerator

from redis.asyncio import Redis, ConnectionPool

from app.configs.settings import get_settings

redis_pool = None
redis_client = None


def get_redis_pool() -> ConnectionPool:
    """Get or create Redis connection pool."""
    global redis_pool
    settings = get_settings()
    if not redis_pool:
        redis_pool = ConnectionPool.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}",
            password=settings.redis_password,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_pool


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """Get Redis client using dependency injection."""
    global redis_client
    if not redis_client:
        pool = get_redis_pool()
        redis_client = Redis(connection_pool=pool)
    try:
        yield redis_client
    finally:
        await redis_client.close()
