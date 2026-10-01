from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.core.bootstrap import Bootstrap
from app.core.ai_engine.context import AIContext
from app.core.memory.session_manager import SessionManager
from app.schemas.chat_request import ChatRequest


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


bootstrap = Bootstrap()


@router.post("/")
async def chat(request: ChatRequest):

    try:

        # =====================================================
        # Session
        # =====================================================

        session_id = request.session_id

        if not session_id:
            session_id = "default"

        memory = SessionManager.get_memory(
            session_id
        )

        # =====================================================
        # Get Dataset From SESSION MEMORY
        # =====================================================

        dataset = memory.dataset.get_dataset()

        # =====================================================
        # Get Conversation History
        # =====================================================
        #
        # IMPORTANT:
        # Do not add the current user message here.
        #
        # AgentOrchestrator is responsible for storing:
        #
        #   user message
        #   assistant response
        #
        # This prevents duplicate conversation entries.
        # =====================================================

        history = (
            memory.conversation.get_history()
        )

        # =====================================================
        # Create AI Context
        # =====================================================

        context = AIContext(
            message=request.message,

            session_id=session_id,

            dataset=dataset,

            memory=memory,

            conversation_history=history,
        )

        # =====================================================
        # Execute AI Engine
        # =====================================================

        result = await bootstrap.ai_engine.execute(
            context
        )

        # =====================================================
        # Prepare Responses
        # =====================================================

        responses = []

        for response in result.responses:

            # -------------------------------------------------
            # Convert AIResponse to dictionary
            # -------------------------------------------------

            if hasattr(response, "model_dump"):

                response_data = response.model_dump()

            elif hasattr(response, "__dict__"):

                response_data = dict(
                    response.__dict__
                )

            else:

                response_data = {
                    "message": str(response)
                }

            # -------------------------------------------------
            # Make chart paths browser-accessible
            # -------------------------------------------------

            data = response_data.get(
                "data"
            )

            if isinstance(data, dict):

                chart_path = data.get(
                    "chart_path"
                )

                if chart_path:

                    path = Path(
                        chart_path
                    )

                    response_data["data"] = {
                        **data,
                        "url": (
                            "/charts/"
                            + path.name
                        ),
                    }

            responses.append(
                response_data
            )

        # =====================================================
        # Return API Response
        # =====================================================

        return {
            "success": result.success,

            "message": result.message,

            "responses": responses,

            "completed_tasks": [
                task.capability
                for task in result.completed_tasks
            ],

            "failed_tasks": [
                task.capability
                for task in result.failed_tasks
            ],
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )