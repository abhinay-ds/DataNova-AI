from __future__ import annotations

from app.core.ai_engine.response import AIResponse
from app.services.visualization_service import VisualizationService
from app.tools.base_tool import BaseTool


class SmartChartTool(BaseTool):

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

        if dataset is None:
            return AIResponse(
                success=False,
                message="Dataset is required.",
            )

        if not x:
            return AIResponse(
                success=False,
                message="Grouping column is required.",
            )

        if not y:
            return AIResponse(
                success=False,
                message="Metric column is required.",
            )

        return VisualizationService.smart_chart(
            df=dataset,
            x=x,
            y=y,
            aggregation=aggregation,
            chart_type=chart_type,
        )