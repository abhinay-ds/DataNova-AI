from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):

    message: str

    session_id: Optional[str] = None

    project_id: Optional[int] = None

    conversation_id: Optional[int] = None