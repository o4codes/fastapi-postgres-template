from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

async def check_database(db: AsyncSession) -> Dict[str, Any]:
    """Check database connection."""
    try:
        # Try to execute a simple query
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "message": "Database connection is healthy",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }

async def check_redis(redis: Redis) -> Dict[str, Any]:
    """Check Redis connection."""
    try:
        # Try to ping Redis
        await redis.ping()
        return {
            "status": "healthy",
            "message": "Redis connection is healthy",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}",
        }
