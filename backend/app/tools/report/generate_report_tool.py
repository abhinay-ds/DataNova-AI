from app.tools.base_tool import BaseTool

from app.services.report_service import ReportService

from app.core.ai_engine.response import AIResponse


class GenerateReportTool(BaseTool):
    """
    Tool for generating AI reports.
    """

    @property
    def name(self) -> str:
        return "generate_report"

    def execute(self, **kwargs) -> AIResponse:

        try:

            report = ReportService.generate_report(
                **kwargs
            )

            return AIResponse(
                success=True,
                message="Report generated successfully.",
                data=report,
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )