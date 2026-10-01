import logging

from app.services.agents.base_agent import BaseAgent
from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse
from app.core.analysis_pipeline import AnalysisPipeline


logger = logging.getLogger(__name__)


class AnalysisAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "AnalysisAgent"

    @property
    def capabilities(self) -> list[str]:
        return [
            "analyze_dataset"
        ]

    async def execute(
        self,
        context: AIContext
    ) -> AIResponse:

        logger.info(
            "AnalysisAgent started"
        )

        # =================================================
        # Dataset validation
        # =================================================

        if context.dataset is None:

            return AIResponse(
                success=False,
                message="Please upload a dataset first.",
                agent="AnalysisAgent",
                intent=context.intent or "analyze_dataset",
            )


        try:

            # =================================================
            # Run structured analysis pipeline
            # =================================================

            response = AnalysisPipeline.run(
                context.dataset
            )


            # =================================================
            # Handle pipeline failure
            # =================================================

            if not response.success:

                return AIResponse(
                    success=False,
                    message=response.message,
                    agent="AnalysisAgent",
                    intent=context.intent or "analyze_dataset",
                    data=response.data,
                )


            # =================================================
            # Return structured analysis
            # =================================================

            return AIResponse(
                success=True,

                message=(
                    "Dataset analysis completed "
                    "successfully."
                ),

                agent="AnalysisAgent",

                intent=(
                    context.intent
                    or "analyze_dataset"
                ),

                data=response.data,
            )


        except Exception as e:

            logger.exception(
                "AnalysisAgent failed"
            )

            return AIResponse(
                success=False,
                message=str(e),
                agent="AnalysisAgent",
                intent=context.intent or "analyze_dataset",
            )