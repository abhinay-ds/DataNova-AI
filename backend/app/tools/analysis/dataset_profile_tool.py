from app.services.dataset_profiler_service import DatasetProfilerService
from app.tools.base_tool import BaseTool


class DatasetProfileTool(BaseTool):

    @property
    def name(self):
        return "dataset_profile"

    def execute(self, **kwargs):

        return DatasetProfilerService.profile(
            kwargs["dataset"]
        )