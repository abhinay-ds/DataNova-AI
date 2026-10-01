from __future__ import annotations

from app.services.dataset_profiler_service import (
    DatasetProfilerService,
)
from app.services.quality_service import QualityService
from app.services.recommendation_service import (
    RecommendationService,
)
from app.services.insight_service import InsightService
from app.services.report_service import ReportService

from app.core.ai_engine.response import AIResponse


class AnalysisPipeline:
    """
    Central dataset analysis pipeline.

    Produces one consistent response structure
    for the DataNova AI frontend.
    """

    @classmethod
    def run(cls, dataset):

        # =================================================
        # Validate Dataset
        # =================================================

        if dataset is None:

            return AIResponse(
                success=False,
                message="Please upload a dataset first.",
                data=None,
            )


        if dataset.empty:

            return AIResponse(
                success=False,
                message="Dataset is empty.",
                data=None,
            )


        try:

            # =================================================
            # Profile
            # =================================================

            profile_response = (
                DatasetProfilerService.profile(
                    dataset
                )
            )


            if not profile_response.success:

                return profile_response


            profile = (
                profile_response.data
                or {}
            )


            # =================================================
            # Quality
            # =================================================

            quality_response = (
                QualityService.evaluate(
                    dataset
                )
            )


            if not quality_response.success:

                return quality_response


            quality = (
                quality_response.data
                or {}
            )


            # =================================================
            # Recommendations
            # =================================================

            recommendation_response = (
                RecommendationService.generate(
                    dataset
                )
            )


            if not recommendation_response.success:

                return recommendation_response


            recommendations = (
                recommendation_response.data
                or []
            )


            # =================================================
            # Insights
            # =================================================

            insight_response = (
                InsightService.generate(
                    dataset
                )
            )


            if not insight_response.success:

                return insight_response


            insights = (
                insight_response.data
                or []
            )


            # =================================================
            # Report
            # =================================================

            report_response = (
                ReportService.generate(
                    dataset
                )
            )


            report = (
                report_response.data
                if hasattr(
                    report_response,
                    "data",
                )
                else None
            )


            # =================================================
            # Build Frontend-Friendly Overview
            # =================================================

            shape = (
                profile.get(
                    "shape",
                    {}
                )
            )

            missing_values = (
                profile.get(
                    "missing_values",
                    {}
                )
            )

            duplicates = profile.get(
                "duplicates",
                0
            )

            memory_usage = profile.get(
                "memory_usage",
                {}
            )


            missing_total = sum(
                int(value or 0)
                for value
                in missing_values.values()
            )


            # =================================================
            # Final Structured Response
            # =================================================

            analysis = {

                "overview": {

                    "rows": shape.get(
                        "rows",
                        len(dataset),
                    ),

                    "columns": shape.get(
                        "columns",
                        len(dataset.columns),
                    ),

                    "column_names": profile.get(
                        "columns",
                        dataset.columns.tolist(),
                    ),

                    "missing_values_total":
                        missing_total,

                    "missing_values":
                        missing_values,

                    "duplicate_rows":
                        duplicates,

                    "memory_usage":
                        memory_usage,

                },


                "quality": quality,


                "insights": insights,


                "recommendations":
                    recommendations,


                "profile": profile,


                "report": report,

            }


            # =================================================
            # Return
            # =================================================

            return AIResponse(

                success=True,

                message=(
                    "Dataset analysis completed "
                    "successfully."
                ),

                data=analysis,

            )


        except Exception as e:

            return AIResponse(

                success=False,

                message=str(e),

                data=None,

            )