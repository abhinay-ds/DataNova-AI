from app.services.visualization_service import VisualizationService
from app.tools.base_tool import BaseTool


class CorrelationTool(BaseTool):

    @property
    def name(self):
        return "correlation"

    def execute(self, **kwargs):

        return VisualizationService.correlation(
            kwargs["dataset"]
        )