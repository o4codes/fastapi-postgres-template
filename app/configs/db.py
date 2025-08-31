from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from redis.asyncio import Redis, ConnectionPool

from app.configs.settings import get_settings

engine = None
SessionLocal = None
redis_pool = None
redis_client = None

Base = declarative_base()


def get_db_engine():
    global engine, SessionLocal
    settings = get_settings()
    if not engine:
        engine = create_async_engine(
            f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}",
            echo=True,
        )

        SessionLocal = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return engine


async def get_db_session():
    get_db_engine()
    async with SessionLocal() as session:
        yield session


def get_redis_pool():
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


async def get_redis_client():
    """Get Redis client using dependency injection."""
    global redis_client
    if not redis_client:
        pool = get_redis_pool()
        redis_client = Redis(connection_pool=pool)
    try:
        yield redis_client
    finally:
        await redis_client.close()
