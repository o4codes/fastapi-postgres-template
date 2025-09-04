from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.local import local_handler
from loguru import logger

from app.api.authentication import endpoints as authentication_endpoints
from app.api.authorization import endpoints as authorization_endpoints
from app.api.health import endpoints as health_endpoints
from app.api.notifications import endpoints as notification_endpoints
from app.api.users import endpoints as user_endpoints
from app.commons.errors import EXCEPTION_HANDLERS_MAPPING
from app.commons.middlewares import RequestIDMiddleware, TimingMiddleware
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
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application")


# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=settings.description,
    docs_url="/api/docs/swagger",
    redoc_url="/api/docs/redoc",
    openapi_url="/api/docs/openapi.json",
    lifespan=lifespan,
    exception_handlers=EXCEPTION_HANDLERS_MAPPING,
)

# Add middlewares
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    EventHandlerASGIMiddleware,
    handlers=[local_handler],
)


# Include routers
app.include_router(
    authentication_endpoints.auth_router, prefix="/api/v1", tags=["Authentication"]
)
app.include_router(
    authentication_endpoints.two_factor_router,
    prefix="/api/v1",
    tags=["Two-Factor Authentication"],
)
app.include_router(
    authorization_endpoints.permission_router, prefix="/api/v1", tags=["Permissions"]
)
app.include_router(
    authorization_endpoints.role_router, prefix="/api/v1", tags=["Roles"]
)
app.include_router(health_endpoints.router, prefix="/api/v1", tags=["Health"])
app.include_router(
    notification_endpoints.router, prefix="/api/v1", tags=["Notifications"]
)
app.include_router(user_endpoints.router, prefix="/api/v1", tags=["Users"])
