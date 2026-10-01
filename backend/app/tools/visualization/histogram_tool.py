from app.services.visualization_service import VisualizationService
from app.tools.base_tool import BaseTool


class HistogramTool(BaseTool):

    @property
    def name(self):
        return "histogram"

    def execute(self, **kwargs):

        column = (
            kwargs.get("column")
            or kwargs.get("column_name")
            or kwargs.get("feature")
        )

        if not column:
            raise ValueError(
                "Histogram requires a column."
            )

        return VisualizationService.histogram(
            df=kwargs["dataset"],
            column=column,
        )