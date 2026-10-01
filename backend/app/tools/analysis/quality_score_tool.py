from app.services.quality_service import QualityService
from app.tools.base_tool import BaseTool


class QualityScoreTool(BaseTool):

    @property
    def name(self):
        return "quality_score"

    def execute(self, **kwargs):

        return QualityService.analyze(
            kwargs["dataset"]
        )