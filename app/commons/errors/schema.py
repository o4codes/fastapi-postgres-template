import time
from typing import Any, Optional

from pydantic import BaseModel


class ErrorSchema(BaseModel):
    status: bool
    path: str
    timestamp: int = int(time.time() * 1000)
    message: str
    data: Optional[Any]
