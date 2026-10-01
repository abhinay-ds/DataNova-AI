from typing import Any

from pydantic import BaseModel


class ChatResponse(BaseModel):
    success: bool
    message: str
    capability: str | None = None
    data: Any | None = None