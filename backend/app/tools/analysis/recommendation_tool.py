from app.services.recommendation_service import RecommendationService
from app.tools.base_tool import BaseTool


class RecommendationTool(BaseTool):

    @property
    def name(self):
        return "recommendation"

    def execute(self, **kwargs):

        return RecommendationService.analyze(
            kwargs["dataset"]
        )