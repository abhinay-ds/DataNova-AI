from __future__ import annotations

import logging

from app.services.agents.base_agent import BaseAgent

from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse

from app.services.profile_service import ProfileService

logger = logging.getLogger(__name__)


class ProfileAgent(BaseAgent):
    """
    Dataset Profile Agent

    Responsibilities
    ----------------
    - Generate dataset profile
    - Calculate dataset statistics
    - Store profile in memory
    """

    def __init__(self):
        self.profile_service = ProfileService()

    @property
    def name(self) -> str:
        return "Profile Agent"

    @property
    def capabilities(self) -> list[str]:
        return [
            "profile_dataset",
        ]

    async def execute(
        self,
        context: AIContext,
    ) -> AIResponse:

        logger.info(f"{self.name} started.")

        if context.dataset is None:

            return AIResponse(
                success=False,
                message="Please upload a dataset first."
            )

        try:

            profile = self.profile_service.generate_profile(
                context.dataset
            )

            response = AIResponse(
                success=True,
                message="Dataset profile generated successfully.",
                data=profile,
            )

            if hasattr(context, "memory"):

                try:

                    context.memory.dataset.set_profile(
                        profile
                    )

                except Exception:
                    logger.exception(
                        "Failed to store dataset profile in memory."
                        )

            return response

        except Exception as e:

            logger.exception("ProfileAgent failed.")

            return AIResponse(
                success=False,
                message=str(e),
            )