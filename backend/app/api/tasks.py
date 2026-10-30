from datetime import datetime
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.project import Project
from app.models.user import User


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/projects",
    tags=["Tasks"],
)


class TaskItem(BaseModel):
    id: str
    conversation_id: int
    message_id: int
    prompt: Optional[str] = None
    capability: str
    status: str  # "completed" | "failed"
    created_at: str


def get_owned_project(
    project_id: int,
    current_user: User,
    db: Session,
) -> Project:
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.owner_id == current_user.id,
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return project


@router.get(
    "/{project_id}/tasks",
    response_model=List[TaskItem],
)
def list_project_tasks(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = get_owned_project(project_id, current_user, db)

    # Find all conversations belonging to this project
    conversations = (
        db.query(Conversation)
        .filter(Conversation.project_id == project.id)
        .all()
    )

    if not conversations:
        return []

    conversation_ids = [c.id for c in conversations]

    # Query all messages in those conversations, ordered chronologically
    messages = (
        db.query(Message)
        .filter(Message.conversation_id.in_(conversation_ids))
        .order_by(Message.created_at.asc())
        .all()
    )

    # Map assistant messages back to user prompts and extract executed tasks
    # We maintain previous user prompt for context
    tasks: List[TaskItem] = []
    current_prompt_by_conv: dict[int, str] = {}

    for msg in messages:
        if msg.role == "user":
            current_prompt_by_conv[msg.conversation_id] = msg.content
        elif msg.role == "assistant":
            data = msg.message_data or {}
            completed = data.get("completed_tasks") or []
            failed = data.get("failed_tasks") or []
            prompt = current_prompt_by_conv.get(msg.conversation_id)

            created_time_str = (
                msg.created_at.isoformat()
                if isinstance(msg.created_at, datetime)
                else str(msg.created_at)
            )

            idx = 0
            for cap in completed:
                idx += 1
                tasks.append(
                    TaskItem(
                        id=f"msg_{msg.id}_c_{idx}",
                        conversation_id=msg.conversation_id,
                        message_id=msg.id,
                        prompt=prompt,
                        capability=str(cap),
                        status="completed",
                        created_at=created_time_str,
                    )
                )

            for cap in failed:
                idx += 1
                tasks.append(
                    TaskItem(
                        id=f"msg_{msg.id}_f_{idx}",
                        conversation_id=msg.conversation_id,
                        message_id=msg.id,
                        prompt=prompt,
                        capability=str(cap),
                        status="failed",
                        created_at=created_time_str,
                    )
                )

    # Return newest tasks first
    tasks.reverse()
    return tasks
