from app.services.visualization_service import VisualizationService
from app.tools.base_tool import BaseTool


class HeatmapTool(BaseTool):

    @property
    def name(self):
        return "heatmap"

    def execute(self, **kwargs):

        return VisualizationService.heatmap(
            kwargs["dataset"]
        )