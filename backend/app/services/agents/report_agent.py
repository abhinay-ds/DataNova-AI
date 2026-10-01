from __future__ import annotations

import logging

from app.services.agents.base_agent import BaseAgent
from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse

from app.services.report_service import ReportService
from app.services.report_export_service import ReportExportService


logger = logging.getLogger(__name__)


class ReportAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "Report Agent"

    @property
    def capabilities(self) -> list[str]:
        return [
            "generate_report",
        ]

    async def execute(
        self,
        context: AIContext,
    ) -> AIResponse:

        logger.info(
            "Report Agent started."
        )

        # =================================================
        # Validate dataset
        # =================================================

        if context.dataset is None:

            return AIResponse(
                success=False,
                message="Please upload a dataset first.",
                agent="Report Agent",
                intent="generate_report",
            )

        try:

            # =================================================
            # Generate base report
            # =================================================

            report_response = ReportService.generate(
                context.dataset
            )

            if not report_response.success:

                return report_response

            report = report_response.data

            # =================================================
            # Get previous workflow results
            # =================================================

            task_results = getattr(
                context,
                "task_results",
                {}
            )

            # =================================================
            # Add analysis result
            # =================================================

            if "analyze_dataset" in task_results:

                report["analysis"] = (
                    task_results[
                        "analyze_dataset"
                    ]
                )

            # =================================================
            # Add correlation result
            # =================================================

            if "correlation" in task_results:

                report["correlation"] = (
                    task_results[
                        "correlation"
                    ]
                )

            # =================================================
            # Add model training result
            # =================================================

            if "train_model" in task_results:

                report["model_training"] = (
                    task_results[
                        "train_model"
                    ]
                )

            # =================================================
            # Add evaluation result
            # =================================================

            if "evaluate_model" in task_results:

                report["model_evaluation"] = (
                    task_results[
                        "evaluate_model"
                    ]
                )

            # =================================================
            # Add prediction result
            # =================================================

            if "predict" in task_results:

                report["predictions"] = (
                    task_results[
                        "predict"
                    ]
                )

            # =================================================
            # Add visualization results
            # =================================================

            visualization_names = [
                "histogram",
                "scatter",
                "line_chart",
                "bar_chart",
                "pie_chart",
                "boxplot",
                "heatmap",
            ]

            visualizations = {}

            for name in visualization_names:

                if name in task_results:

                    visualizations[name] = (
                        task_results[name]
                    )

            if visualizations:

                report["visualizations"] = (
                    visualizations
                )

            # =================================================
            # Workflow information
            # =================================================

            report["workflow"] = {

                "tasks_executed":
                    len(task_results),

                "task_names":
                    list(task_results.keys()),
            }

            # =================================================
            # Export HTML
            # =================================================

            export_response = (
                ReportExportService.export_html(
                    report
                )
            )

            if not export_response.success:

                return AIResponse(
                    success=False,
                    message=(
                        "Report generated, but "
                        "HTML export failed: "
                        + export_response.message
                    ),
                    data=report,
                    agent="Report Agent",
                    intent="generate_report",
                )

            # =================================================
            # Add export information
            # =================================================

            report["export"] = (
                export_response.data
            )

            # =================================================
            # Save task output
            # =================================================

            task = context.current_task

            if task is not None:

                task.output_data = report

            # =================================================
            # Save memory
            # =================================================

            if hasattr(context, "memory"):

                try:

                    context.memory.report.last_report = (
                        report
                    )

                    if task is not None:

                        context.memory.task.last_task = (
                            task
                        )

                        context.memory.task.last_result = (
                            report
                        )

                except Exception:

                    pass

            # =================================================
            # Return
            # =================================================

            return AIResponse(

                success=True,

                message=(
                    "Comprehensive report generated "
                    "and exported successfully."
                ),

                data=report,

                agent="Report Agent",

                intent="generate_report",
            )

        except Exception as e:

            logger.exception(
                "Report Agent failed."
            )

            return AIResponse(
                success=False,
                message=str(e),
                agent="Report Agent",
                intent="generate_report",
            )