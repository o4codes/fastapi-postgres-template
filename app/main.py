from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from app.api.authorization import endpoints as authorization_endpoints
from app.commons.exceptions import setup_exception_handlers
from app.configs.logger import setup_logger
from app.configs.settings import get_settings

settings = get_settings()

# Setup logging
setup_logger(debug_mode=settings.debug)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for FastAPI app lifespan.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up FastAPI application")
    setup_exception_handlers(app)
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application")


# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=settings.description,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Include routers
app.include_router(authorization_endpoints.permission_router, prefix="/api/v1", tags=["Permissions"])
app.include_router(authorization_endpoints.role_router, prefix="/api/v1", tags=["Roles"])
