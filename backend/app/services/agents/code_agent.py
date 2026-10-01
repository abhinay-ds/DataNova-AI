from __future__ import annotations

import logging
from typing import Any

from app.services.agents.base_agent import BaseAgent
from app.services.code_generation_service import CodeGenerationService

from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse


logger = logging.getLogger(__name__)


class CodeAgent(BaseAgent):
    """
    Code Agent

    Responsibilities
    ----------------
    - Generate Python code
    - Generate SQL queries
    - Explain code
    - Optimize code
    - Convert code
    - Debug code

    For Python analysis requests, this agent can use the actual
    DataNova analysis result so that generated code reproduces
    the calculation/chart instead of guessing the analysis.
    """

    # =========================================================
    # Agent Information
    # =========================================================

    @property
    def name(self) -> str:
        return "Code Agent"

    @property
    def capabilities(self) -> list[str]:
        return [
            "generate_python",
            "generate_sql",
            "explain_code",
            "optimize_code",
            "convert_code",
            "debug_code",
        ]

    # =========================================================
    # Execute
    # =========================================================

    async def execute(
        self,
        context: AIContext,
    ) -> AIResponse:

        logger.info(
            f"{self.name} executing..."
        )

        task = context.current_task

        if task is None:
            return AIResponse(
                success=False,
                message="No task available.",
                data=None,
            )

        try:

            # -------------------------------------------------
            # Python code generation
            # -------------------------------------------------

            if task.capability == "generate_python":

                return await self._generate_python(
                    context=context,
                    task=task,
                )

            # -------------------------------------------------
            # Other code capabilities
            # -------------------------------------------------

            tool = context.tool_registry.get(
                task.capability
            )

            input_data = dict(
                task.input_data or {}
            )

            response = tool.execute(
                **input_data
            )

            # -------------------------------------------------
            # Store task output
            # -------------------------------------------------

            task.output_data = (
                response.data
                if hasattr(response, "data")
                else {}
            )

            # -------------------------------------------------
            # Store memory
            # -------------------------------------------------

            self._store_memory(
                context=context,
                task=task,
                response=response,
            )

            return response

        except Exception as e:

            logger.exception(
                "CodeAgent failed."
            )

            return AIResponse(
                success=False,
                message=str(e),
                data=None,
            )

    # =========================================================
    # Generate Python
    # =========================================================

    async def _generate_python(
        self,
        context: AIContext,
        task: Any,
    ) -> AIResponse:

        input_data = dict(
            task.input_data or {}
        )

        # -----------------------------------------------------
        # User question
        # -----------------------------------------------------

        question = (
            input_data.get("prompt")
            or input_data.get("question")
            or context.message
            or ""
        )

        # -----------------------------------------------------
        # Dataset columns
        # -----------------------------------------------------

        columns: list[str] = []

        if context.dataset is not None:

            try:
                columns = [
                    str(column)
                    for column in context.dataset.columns
                ]

            except Exception:

                columns = []

        # -----------------------------------------------------
        # Build analysis task information
        # -----------------------------------------------------

        analysis_task = {}

        possible_fields = [
            "x",
            "y",
            "aggregation",
            "chart_type",
            "column",
            "labels",
            "values",
        ]

        for field in possible_fields:

            if field in input_data:

                analysis_task[field] = (
                    input_data[field]
                )

        # -----------------------------------------------------
        # Find previous analysis result
        # -----------------------------------------------------

        previous_result = (
            self._get_previous_result(
                context=context,
                task=task,
            )
        )

        # -----------------------------------------------------
        # If we have an actual analysis result,
        # generate reproducible code from it.
        # -----------------------------------------------------

        if (
            previous_result
            and isinstance(previous_result, dict)
        ):

            # Smart chart result
            if (
                "x" in previous_result
                and "y" in previous_result
                and (
                    "aggregation"
                    in previous_result
                )
            ):

                analysis_task = {
                    "capability": "smart_chart",
                    "x": previous_result.get("x"),
                    "y": previous_result.get("y"),
                    "aggregation": previous_result.get(
                        "aggregation",
                        "mean",
                    ),
                    "chart_type": previous_result.get(
                        "chart_type",
                        "bar_chart",
                    ),
                }

            # If there is no task information but
            # the previous result contains a column.
            elif (
                not analysis_task
                and "column" in previous_result
            ):

                analysis_task = {
                    "column": previous_result.get(
                        "column"
                    )
                }

        # -----------------------------------------------------
        # Generate code using actual analysis context
        # -----------------------------------------------------

        if (
            previous_result
            and isinstance(previous_result, dict)
            and analysis_task
        ):

            response = (
                CodeGenerationService.generate_from_analysis(
                    question=question,
                    dataset_columns=columns,
                    task=analysis_task,
                    result=previous_result,
                )
            )

        else:

            # -------------------------------------------------
            # Fallback for ordinary code requests
            # -------------------------------------------------

            prompt = question

            prompt += (
                "\n\nDATASET CONTEXT:\n"
                "A pandas DataFrame named `df` is "
                "already loaded and available.\n"
                "Do NOT use pd.read_csv().\n"
                "Use the existing `df` DataFrame."
            )

            if columns:

                prompt += (
                    "\nAvailable columns:\n"
                    + ", ".join(columns)
                )

            # Add previous result when available
            if previous_result:

                prompt += (
                    "\n\nPREVIOUS ANALYSIS RESULT:\n"
                    + str(previous_result)
                )

                prompt += (
                    "\n\nGenerate code that reproduces "
                    "this analysis."
                )

            # Put enriched prompt back into task input
            input_data["prompt"] = prompt

            tool = context.tool_registry.get(
                task.capability
            )

            response = tool.execute(
                **input_data
            )

        # -----------------------------------------------------
        # Store task output
        # -----------------------------------------------------

        task.output_data = (
            response.data
            if hasattr(response, "data")
            else {}
        )

        # -----------------------------------------------------
        # Store memory
        # -----------------------------------------------------

        self._store_memory(
            context=context,
            task=task,
            response=response,
        )

        return response

    # =========================================================
    # Get Previous Result
    # =========================================================

    @staticmethod
    def _get_previous_result(
        context: AIContext,
        task: Any,
    ) -> Any:

        # -----------------------------------------------------
        # 1. Result injected by AgentOrchestrator
        # -----------------------------------------------------

        try:

            task_input = (
                task.input_data
                or {}
            )

            previous_results = (
                task_input.get(
                    "_previous_results"
                )
            )

            if previous_results:

                # If the orchestrator supplied a
                # dictionary of capability results,
                # find the most recent useful result.

                if isinstance(
                    previous_results,
                    dict,
                ):

                    for value in reversed(
                        list(
                            previous_results.values()
                        )
                    ):

                        if value:
                            return value

                return previous_results

        except Exception:

            pass

        # -----------------------------------------------------
        # 2. Memory fallback
        # -----------------------------------------------------

        try:

            if hasattr(context, "memory"):

                memory = context.memory

                if hasattr(
                    memory,
                    "task",
                ):

                    last_result = getattr(
                        memory.task,
                        "last_result",
                        None,
                    )

                    if last_result:
                        return last_result

                if hasattr(
                    memory,
                    "visualization",
                ):

                    last_chart = getattr(
                        memory.visualization,
                        "last_chart",
                        None,
                    )

                    if last_chart:
                        return last_chart

        except Exception:

            pass

        return None

    # =========================================================
    # Store Memory
    # =========================================================

    @staticmethod
    def _store_memory(
        context: AIContext,
        task: Any,
        response: AIResponse,
    ) -> None:

        if not hasattr(
            context,
            "memory",
        ):
            return

        try:

            context.memory.task.last_task = task

            if hasattr(
                response,
                "data",
            ):

                context.memory.task.last_result = (
                    response.data
                )

        except Exception:

            pass