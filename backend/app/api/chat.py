from datetime import datetime, timezone
import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.bootstrap import Bootstrap
from app.core.ai_engine.context import AIContext
from app.core.memory.session_manager import SessionManager
from app.database import get_db
from app.models.analysis import Analysis
from app.models.chart import Chart
from app.models.conversation import Conversation
from app.models.dataset import Dataset
from app.models.message import Message
from app.models.project import Project
from app.models.user import User
from app.schemas.chat_request import ChatRequest
from app.services.file_service import FileService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

bootstrap = Bootstrap()


@router.post("/")
async def chat(
    request: ChatRequest,
    project_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # =====================================================
        # Project Validation & User Isolation
        # =====================================================
        target_project_id = request.project_id or project_id

        if target_project_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="project_id is required.",
            )

        project = (
            db.query(Project)
            .filter(
                Project.id == target_project_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        # =====================================================
        # Conversation Management
        # =====================================================
        conversation = None

        if request.conversation_id:
            conversation = (
                db.query(Conversation)
                .filter(
                    Conversation.id == request.conversation_id,
                    Conversation.project_id == project.id,
                )
                .first()
            )
            if conversation is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found.",
                )

        if conversation is None:
            conversation = (
                db.query(Conversation)
                .filter(Conversation.project_id == project.id)
                .order_by(
                    Conversation.updated_at.desc(),
                    Conversation.created_at.desc(),
                )
                .first()
            )

        if conversation is None:
            title = request.message.strip()[:60] if request.message else "New analysis"
            conversation = Conversation(
                project_id=project.id,
                title=title,
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # =====================================================
        # Persist User Message
        # =====================================================
        user_message_record = Message(
            role="user",
            content=request.message,
            conversation_id=conversation.id,
            message_data=None,
        )
        db.add(user_message_record)
        db.commit()

        # =====================================================
        # Session Memory & Dataset Restoration
        # =====================================================
        session_id = request.session_id or f"project_{project.id}_{conversation.id}"

        memory = SessionManager.get_memory(session_id)

        dataset = memory.dataset.get_dataset()

        # If memory has no dataset, attempt auto-restoration from project's latest dataset record
        if dataset is None:
            dataset_record = (
                db.query(Dataset)
                .filter(Dataset.project_id == project.id)
                .order_by(Dataset.created_at.desc())
                .first()
            )

            if dataset_record and dataset_record.storage_path:
                storage_path = dataset_record.storage_path
                # Handle relative path resolution
                if not os.path.isabs(storage_path):
                    backend_dir = os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                    storage_path = os.path.join(backend_dir, storage_path)

                if os.path.exists(storage_path):
                    try:
                        dataframe = FileService.load_dataframe(storage_path)
                        memory.dataset.set_dataset(dataframe)
                        dataset = dataframe

                        analysis_summary = FileService.analyze_dataset(
                            storage_path,
                            df=dataframe,
                            include_llm_summary=False,
                        )
                        if isinstance(analysis_summary, dict):
                            memory.dataset.set_profile(analysis_summary.get("profile", {}))
                            memory.dataset.set_quality(analysis_summary.get("quality", {}))
                            memory.dataset.set_insights(analysis_summary.get("insights", {}))
                            memory.dataset.set_recommendations(analysis_summary.get("recommendations", {}))
                    except Exception as load_err:
                        logger.warning("Failed to auto-restore dataset into memory: %s", load_err)

        # =====================================================
        # Restore Conversation History into Session Memory
        # =====================================================
        if not memory.conversation.get_history():
            past_messages = (
                db.query(Message)
                .filter(
                    Message.conversation_id == conversation.id,
                    Message.id != user_message_record.id,
                )
                .order_by(Message.created_at.asc())
                .all()
            )
            for pm in past_messages:
                memory.conversation.add_message(
                    role=pm.role,
                    content=pm.content,
                    data=pm.message_data,
                )

        history = memory.conversation.get_history()

        # =====================================================
        # Create AI Context & Execute
        # =====================================================
        context = AIContext(
            message=request.message,
            session_id=session_id,
            dataset=dataset,
            memory=memory,
            conversation_history=history,
        )

        result = await bootstrap.ai_engine.execute(context)

        # =====================================================
        # Prepare Responses
        # =====================================================
        responses = []

        for response in result.responses:
            if hasattr(response, "model_dump"):
                response_data = response.model_dump()
            elif hasattr(response, "__dict__"):
                response_data = dict(response.__dict__)
            else:
                response_data = {"message": str(response)}

            data = response_data.get("data")
            if isinstance(data, dict):
                chart_path = data.get("chart_path")
                if chart_path:
                    path = Path(chart_path)
                    response_data["data"] = {
                        **data,
                        "url": "/charts/" + path.name,
                    }

            responses.append(response_data)

        # =====================================================
        # Persist Assistant Message
        # =====================================================
        text_parts = []
        for r in responses:
            msg_text = r.get("message")
            if msg_text and str(msg_text).strip():
                clean_text = str(msg_text).strip()
                if clean_text != "Dataset analysis completed successfully.":
                    text_parts.append(clean_text)
                elif not text_parts:
                    text_parts.append(clean_text)

        assistant_content = "\n\n".join(text_parts) if text_parts else (result.message or "Response generated.")

        assistant_message_data = {
            "responses": responses,
            "completed_tasks": [task.capability for task in result.completed_tasks],
            "failed_tasks": [task.capability for task in result.failed_tasks],
        }

        assistant_message_record = Message(
            role="assistant",
            content=assistant_content,
            message_data=assistant_message_data,
            conversation_id=conversation.id,
        )
        db.add(assistant_message_record)

        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()

        # =====================================================
        # Minimal Analysis and Chart Persistence (Requirement 12)
        # =====================================================
        try:
            for r in responses:
                r_data = r.get("data")
                if isinstance(r_data, dict):
                    chart_path = r_data.get("chart_path")
                    if chart_path:
                        chart_type = r_data.get("chart_type") or r.get("intent") or "chart"
                        chart_entry = Chart(
                            project_id=project.id,
                            title=f"{str(chart_type).title()} Chart",
                            chart_type=str(chart_type),
                            file_path=str(chart_path),
                        )
                        db.add(chart_entry)

                    if (
                        "overview" in r_data
                        or "profile" in r_data
                        or "insights" in r_data
                        or r.get("intent") in ("analyze_dataset", "data_analysis")
                    ):
                        analysis_entry = Analysis(
                            project_id=project.id,
                            title=f"Analysis: {request.message[:80]}",
                            question=request.message,
                            result=str(r.get("message", "")),
                        )
                        db.add(analysis_entry)

            db.commit()
        except Exception as persist_err:
            logger.warning("Failed to persist analysis/chart metadata: %s", persist_err)
            db.rollback()

        # =====================================================
        # Return API Response
        # =====================================================
        return {
            "success": result.success,
            "message": result.message,
            "responses": responses,
            "completed_tasks": [
                task.capability for task in result.completed_tasks
            ],
            "failed_tasks": [
                task.capability for task in result.failed_tasks
            ],
            "conversation_id": conversation.id,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        logger.exception("Error in chat endpoint: %s", e)
        error_str = str(e)
        if "413" in error_str or "rate limit" in error_str.lower() or "tpm" in error_str.lower():
            detail_msg = "The request exceeded the AI token rate limit. Please try again in a few moments."
        elif "connection" in error_str.lower() or "timeout" in error_str.lower():
            detail_msg = "Unable to connect to the AI model service. Please check your network connection or try again."
        else:
            detail_msg = f"An unexpected error occurred: {error_str}" if settings.ENVIRONMENT == "development" else "An unexpected error occurred while processing your request."
        raise HTTPException(
            status_code=500,
            detail=detail_msg,
        )