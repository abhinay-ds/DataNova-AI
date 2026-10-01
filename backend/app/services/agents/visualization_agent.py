from __future__ import annotations

import logging
import re

from app.services.agents.base_agent import BaseAgent
from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse
from app.services.ai_service import AIService


logger = logging.getLogger(__name__)


class VisualizationAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "Visualization Agent"

    @property
    def capabilities(self) -> list[str]:
        return [
            "histogram",
            "scatter",
            "bar_chart",
            "line_chart",
            "pie_chart",
            "boxplot",
            "heatmap",
            "correlation",
            "smart_chart",
        ]

    # =========================================================
    # COLUMN HELPERS
    # =========================================================

    @staticmethod
    def _find_column_in_message(
        message: str,
        columns: list[str],
    ) -> list[str]:

        if not message:
            return []

        message_lower = message.lower()

        matches = []

        # Longest column names first prevents partial matches
        # such as "Age" matching part of another column.
        sorted_columns = sorted(
            columns,
            key=lambda value: len(str(value)),
            reverse=True,
        )

        for column in sorted_columns:

            column_name = str(column)

            # Case-insensitive exact-ish matching.
            pattern = (
                r"(?<![a-zA-Z0-9_])"
                + re.escape(column_name.lower())
                + r"(?![a-zA-Z0-9_])"
            )

            if re.search(pattern, message_lower):
                matches.append(column_name)

        return matches

    @classmethod
    def _resolve_scatter_axes(
        cls,
        context: AIContext,
        task,
    ) -> dict:

        input_data = dict(
            getattr(task, "input_data", {}) or {}
        )

        # -----------------------------------------------------
        # First: use planner-provided values
        # -----------------------------------------------------

        x = input_data.get("x")
        y = input_data.get("y")

        if x and y:
            return input_data

        dataset = context.dataset

        if dataset is None:
            return input_data

        try:
            columns = list(dataset.columns)
        except Exception:
            return input_data

        # -----------------------------------------------------
        # Second: inspect the original user message
        # -----------------------------------------------------

        message = getattr(
            context,
            "message",
            "",
        )

        matched_columns = cls._find_column_in_message(
            message=message,
            columns=columns,
        )

        # -----------------------------------------------------
        # Fill missing x
        # -----------------------------------------------------

        if not x and matched_columns:
            x = matched_columns[0]

        # -----------------------------------------------------
        # Fill missing y
        # -----------------------------------------------------

        if not y:
            for column in matched_columns:
                if column != x:
                    y = column
                    break

        # -----------------------------------------------------
        # Store resolved values
        # -----------------------------------------------------

        if x:
            input_data["x"] = x

        if y:
            input_data["y"] = y

        logger.info(
            "Resolved scatter axes: x=%s, y=%s",
            x,
            y,
        )

        return input_data

    # =========================================================
    # EXECUTE
    # =========================================================

    async def execute(
        self,
        context: AIContext,
    ) -> AIResponse:

        logger.info(
            "%s started.",
            self.name,
        )

        if context.dataset is None:
            return AIResponse(
                success=False,
                message="Please upload a dataset first.",
            )

        task = context.current_task

        if task is None:
            return AIResponse(
                success=False,
                message="No visualization task available.",
            )

        try:

            # -------------------------------------------------
            # Get visualization tool
            # -------------------------------------------------

            tool = context.tool_registry.get(
                task.capability
            )

            if tool is None:
                return AIResponse(
                    success=False,
                    message=(
                        f"No visualization tool found "
                        f"for '{task.capability}'."
                    ),
                )

            # -------------------------------------------------
            # Resolve scatter axes
            # -------------------------------------------------

            input_data = dict(
                getattr(task, "input_data", {}) or {}
            )

            if task.capability == "scatter":

                input_data = (
                    self._resolve_scatter_axes(
                        context=context,
                        task=task,
                    )
                )

                task.input_data = input_data

                if not input_data.get("x"):
                    return AIResponse(
                        success=False,
                        message=(
                            "I couldn't determine the "
                            "x-axis column. Please specify "
                            "which column should be on the x-axis."
                        ),
                    )

                if not input_data.get("y"):
                    return AIResponse(
                        success=False,
                        message=(
                            "I couldn't determine the "
                            "y-axis column. Please specify "
                            "which column should be on the y-axis."
                        ),
                    )

            # -------------------------------------------------
            # Execute visualization tool
            # -------------------------------------------------

            response = tool.execute(
                dataset=context.dataset,
                **input_data,
            )

            # -------------------------------------------------
            # Store result
            # -------------------------------------------------

            task.output_data = (
                response.data
                if hasattr(response, "data")
                else {}
            )

            # -------------------------------------------------
            # Generate AI explanation for Smart Charts
            # -------------------------------------------------

            if (
                response.success
                and task.capability == "smart_chart"
                and isinstance(response.data, dict)
            ):

                chart_data = response.data

                x = chart_data.get("x")
                y = chart_data.get("y")
                aggregation = chart_data.get(
                    "aggregation"
                )
                values = chart_data.get(
                    "values",
                    {},
                )

                if x and y and values:

                    prompt = f"""
You are an expert data analyst working inside DataNova AI.

Analyze the following chart result from a dataset.

Chart:
- Grouping column: {x}
- Metric column: {y}
- Aggregation: {aggregation}

Calculated values:
{values}

Write a concise analytical insight for the user.

Requirements:
- Explain the main pattern visible in the data.
- Mention important differences between groups.
- Use actual values when useful.
- Do not invent causes or information that is not present in the data.
- Do not mention that you are an AI.
- Do not describe the Python code.
- Keep the answer to 2-4 sentences.
"""

                    insight_response = AIService.generate(
                        prompt=prompt,
                        temperature=0.2,
                    )

                    if insight_response.success:

                        chart_data["ai_insight"] = (
                            insight_response.data
                        )

                        task.output_data = chart_data

            # -------------------------------------------------
            # Store memory
            # -------------------------------------------------

            if hasattr(context, "memory"):

                try:

                    context.memory.task.last_task = task

                    if hasattr(response, "data"):
                        context.memory.task.last_result = (
                            response.data
                        )

                    if hasattr(
                        context.memory,
                        "visualization",
                    ):
                        (
                            context.memory.visualization.last_chart
                        ) = response.data

                except Exception:
                    pass

            return response

        except Exception as e:

            logger.exception(
                "%s failed.",
                self.name,
            )

            return AIResponse(
                success=False,
                message=str(e),
            )