from app.core.analysis_pipeline import AnalysisPipeline
from app.tools.base_tool import BaseTool


class AnalyzeDatasetTool(BaseTool):

    @property
    def name(self):
        return "analyze_dataset"

    def execute(self, **kwargs):

        return AnalysisPipeline.run(
            kwargs["dataset"]
        )