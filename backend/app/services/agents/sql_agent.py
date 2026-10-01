from __future__ import annotations

import logging

from app.services.agents.base_agent import BaseAgent

from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse

from app.services.sql_service import SQLService

logger = logging.getLogger(__name__)


class SQLAgent(BaseAgent):
    """
    SQL Agent

    Responsibilities
    ----------------
    - Generate SQL queries
    - Execute SQL queries
    - Return query results
    """

    def __init__(self):
        self.sql_service = SQLService()

    @property
    def name(self) -> str:
        return "SQL Agent"

    @property
    def capabilities(self) -> list[str]:
        return [
            "generate_sql",
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

            task = context.current_task

            query = (
                task.input_data.get("query")
                if task and hasattr(task, "input_data")
                else context.message
            )

            result = self.sql_service.execute_query(
                context.dataset,
                query,
            )

            response = AIResponse(
                success=True,
                message="SQL query executed successfully.",
                data=result,
            )

            if task is not None:
                task.output_data = result

            if hasattr(context, "memory"):

                try:

                    context.memory.task.last_task = task

                    context.memory.task.last_result = result

                except Exception:
                    pass

            return response

        except Exception as e:

            logger.exception("SQLAgent failed.")

            return AIResponse(
                success=False,
                message=str(e),
            )