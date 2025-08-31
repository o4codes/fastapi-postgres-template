from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.configs.settings import get_settings

engine = None
SessionLocal = None


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
