from __future__ import annotations

import logging

from app.services.agents.base_agent import BaseAgent
from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse
from app.services.data_analysis_service import DataAnalysisService


logger = logging.getLogger(__name__)


class DataAnalysisAgent(BaseAgent):

    # ------------------------------------------------------------------
    # AGENT NAME
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:

        return "DataAnalysisAgent"


    # ------------------------------------------------------------------
    # CAPABILITIES
    # ------------------------------------------------------------------

    @property
    def capabilities(self) -> list[str]:

        return [
            "data_analysis",
        ]


    # ------------------------------------------------------------------
    # EXECUTE
    # ------------------------------------------------------------------

    async def execute(
        self,
        context: AIContext,
    ) -> AIResponse:

        logger.info(
            "DataAnalysisAgent started"
        )


        # --------------------------------------------------------------
        # Get dataset
        # --------------------------------------------------------------

        dataset = context.dataset


        if (
            dataset is None
            and context.memory is not None
        ):

            try:

                dataset = (
                    context.memory
                    .dataset
                    .get_dataset()
                )

            except Exception:

                logger.exception(
                    "Failed to retrieve dataset "
                    "from memory"
                )


        # --------------------------------------------------------------
        # Validate dataset
        # --------------------------------------------------------------

        if dataset is None:

            return AIResponse(
                success=False,
                message=(
                    "Please upload a dataset "
                    "before asking an analysis question."
                ),
                data=None,
                agent=self.name,
                intent="data_analysis",
            )


        # --------------------------------------------------------------
        # Get question
        # --------------------------------------------------------------

        question = (
            context.message or ""
        ).strip()


        if not question:

            return AIResponse(
                success=False,
                message=(
                    "Please ask a question "
                    "about your dataset."
                ),
                data=None,
                agent=self.name,
                intent="data_analysis",
            )


        # --------------------------------------------------------------
        # Get conversation history
        # --------------------------------------------------------------

        conversation_history = []


        if context.memory is not None:

            try:

                conversation_history = (
                    context.memory
                    .conversation
                    .get_history()
                )

            except Exception:

                logger.exception(
                    "Failed to retrieve "
                    "conversation history"
                )


        # --------------------------------------------------------------
        # Analyze
        # --------------------------------------------------------------

        try:

            response = (
                DataAnalysisService.answer(
                    dataset=dataset,
                    question=question,
                    conversation_history=
                        conversation_history,
                )
            )


            return AIResponse(
                success=response.success,
                message=response.message,
                data=response.data,
                agent=self.name,
                intent="data_analysis",
            )


        except Exception as e:

            logger.exception(
                "DataAnalysisAgent failed"
            )


            return AIResponse(
                success=False,
                message=(
                    f"I couldn't analyze the dataset: "
                    f"{str(e)}"
                ),
                data=None,
                agent=self.name,
                intent="data_analysis",
            )