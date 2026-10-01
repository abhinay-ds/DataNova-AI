from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    type: str
    response: Optional[str] = None
    url: Optional[str] = None