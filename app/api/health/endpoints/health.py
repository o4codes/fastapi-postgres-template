from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.configs.db import get_db, get_redis_client
from app.commons.health import check_database, check_redis

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis_client),
):
    """
    Health check endpoint that verifies database and Redis connections.
    Returns:
        dict: Health status of the application components
    """
    db_status = await check_database(db)
    redis_status = await check_redis(redis)
    
    overall_status = "healthy" if all(
        component["status"] == "healthy" 
        for component in [db_status, redis_status]
    ) else "unhealthy"
    
    return {
        "status": overall_status,
        "components": {
            "database": db_status,
            "redis": redis_status,
        }
    }
