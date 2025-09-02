from .permission import router as permission_router
from .role import router as role_router

__all__ = [
    "permission_router",
    "role_router",
]
