from __future__ import annotations

from app.core.ai_engine.response import AIResponse
from app.services.visualization_service import VisualizationService
from app.tools.base_tool import BaseTool


class SmartChartTool(BaseTool):
    """
    Smart Chart Tool

    Generates an aggregated chart from a dataset.

    Example:
        x = "Pclass"
        y = "Survived"
        aggregation = "mean"
        chart_type = "bar"

    This produces survival rate by passenger class.
    """

    @property
    def name(self) -> str:
        return "smart_chart"

    def execute(
        self,
        dataset,
        x: str,
        y: str,
        aggregation: str = "mean",
        chart_type: str = "bar",
        **kwargs,
    ) -> AIResponse:

        # -----------------------------------------------------
        # Validate dataset
        # -----------------------------------------------------

        if dataset is None:

            return AIResponse(
                success=False,
                message="Dataset is required.",
            )

        # -----------------------------------------------------
        # Validate X
        # -----------------------------------------------------

        if not x:

            return AIResponse(
                success=False,
                message="Grouping column is required.",
            )

        # -----------------------------------------------------
        # Validate Y
        # -----------------------------------------------------

        if not y:

            return AIResponse(
                success=False,
                message="Metric column is required.",
            )

        # -----------------------------------------------------
        # Execute visualization
        # -----------------------------------------------------

        return VisualizationService.smart_chart(
            df=dataset,
            x=x,
            y=y,
            aggregation=aggregation,
            chart_type=chart_type,
        )