from app.services.report_service import ReportService
from app.tools.base_tool import BaseTool


class GenerateReportTool(BaseTool):

    @property
    def name(self):
        return "generate_report"

    def execute(self, **kwargs):

        return ReportService.generate(
            kwargs["dataset"]
        )