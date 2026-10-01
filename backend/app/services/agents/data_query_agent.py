import logging

from app.services.agents.base_agent import BaseAgent
from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse
from app.services.data_query_service import DataQueryService


logger = logging.getLogger(__name__)


class DataQueryAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "DataQueryAgent"

    @property
    def capabilities(self) -> list[str]:
        return [
            "data_question"
        ]

    async def execute(
        self,
        context: AIContext
    ) -> AIResponse:

        logger.info(
            "DataQueryAgent started"
        )

        # =================================================
        # Get dataset
        # =================================================

        dataset = context.dataset

        # -------------------------------------------------
        # Fallback to session memory
        # -------------------------------------------------

        if dataset is None and context.memory is not None:

            try:
                dataset = (
                    context.memory.dataset.get_dataset()
                )

            except Exception:

                logger.exception(
                    "Failed to retrieve dataset from memory"
                )

        # =================================================
        # Dataset validation
        # =================================================

        if dataset is None:

            return AIResponse(
                success=False,
                message="Please upload a dataset first.",
                agent=self.name,
                intent=(
                    context.intent
                    or "data_question"
                ),
            )

        # =================================================
        # Question validation
        # =================================================

        question = (
            context.message
            if context.message
            else ""
        ).strip()

        if not question:

            return AIResponse(
                success=False,
                message=(
                    "Please ask a question "
                    "about your dataset."
                ),
                agent=self.name,
                intent="data_question",
            )

        # =================================================
        # Conversation history
        # =================================================

        conversation_history = []

        if context.memory is not None:

            try:

                conversation_history = (
                    context.memory.conversation.get_history()
                )

            except Exception:

                logger.exception(
                    "Failed to get conversation history"
                )

                conversation_history = []

        # =================================================
        # Execute query
        # =================================================

        try:

            response = DataQueryService.answer(
                dataset=dataset,
                question=question,
                conversation_history=conversation_history,
            )

            # =================================================
            # Return response
            # =================================================

            return AIResponse(
                success=response.success,
                message=response.message,
                agent=self.name,
                intent="data_question",
                data=response.data,
            )

        except Exception as e:

            logger.exception(
                "DataQueryAgent failed"
            )

            return AIResponse(
                success=False,
                message=(
                    "I couldn't process your data question: "
                    f"{str(e)}"
                ),
                agent=self.name,
                intent="data_question",
            )