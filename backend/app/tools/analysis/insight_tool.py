from app.services.insight_service import InsightService
from app.tools.base_tool import BaseTool


class InsightTool(BaseTool):

    @property
    def name(self):
        return "insight"

    def execute(self, **kwargs):

        return InsightService.analyze(
            kwargs["dataset"]
        )