import logging

from app.services.agents.base_agent import BaseAgent

from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse

from app.core.analysis_pipeline import AnalysisPipeline


logger = logging.getLogger(__name__)


class AnalysisAgent(BaseAgent):
    """
    Analysis Agent

    Responsibilities
    ----------------
    - Analyze uploaded datasets
    - Generate dataset profile
    - Calculate quality score
    - Generate insights
    - Generate recommendations
    - Prepare structured analysis results
    """

    @property
    def name(self) -> str:
        return "AnalysisAgent"

    @property
    def capabilities(self) -> list[str]:
        return [
            "analyze_dataset",
        ]

    async def execute(
        self,
        context: AIContext,
    ) -> AIResponse:

        logger.info(
            "AnalysisAgent started"
        )

        # =====================================================
        # Dataset Validation
        # =====================================================

        if context.dataset is None:

            return AIResponse(
                success=False,
                message="Please upload a dataset first.",
                agent=self.name,
                intent=context.intent or "analyze_dataset",
            )

        try:

            df = context.dataset

            # =================================================
            # Run Complete Analysis Pipeline
            # =================================================

            pipeline_result = (
                AnalysisPipeline.run(
                    df
                )
            )

            # =================================================
            # Extract Results
            # =================================================

            profile_response = (
                pipeline_result.get(
                    "profile"
                )
            )

            quality_response = (
                pipeline_result.get(
                    "quality"
                )
            )

            recommendation_response = (
                pipeline_result.get(
                    "recommendation"
                )
            )

            insight_response = (
                pipeline_result.get(
                    "insight"
                )
            )

            report_response = (
                pipeline_result.get(
                    "report"
                )
            )

            # =================================================
            # Helper
            # =================================================

            def extract_data(response):

                if response is None:
                    return None

                if hasattr(
                    response,
                    "data"
                ):

                    return response.data

                return response

            # =================================================
            # Extract Structured Data
            # =================================================

            profile = extract_data(
                profile_response
            )

            quality = extract_data(
                quality_response
            )

            recommendations = extract_data(
                recommendation_response
            )

            insights = extract_data(
                insight_response
            )

            report = extract_data(
                report_response
            )

            # =================================================
            # Build Structured Analysis
            # =================================================

            analysis_data = {

                # ---------------------------------------------
                # Dataset Overview
                # ---------------------------------------------

                "overview": {

                    "rows": int(
                        df.shape[0]
                    ),

                    "columns": int(
                        df.shape[1]
                    ),

                    "column_names": [
                        str(column)
                        for column in df.columns
                    ],

                    "duplicate_rows": int(
                        df.duplicated().sum()
                    ),

                    "missing_values_total": int(
                        df.isnull()
                        .sum()
                        .sum()
                    ),

                },

                # ---------------------------------------------
                # Profile
                # ---------------------------------------------

                "profile": profile,

                # ---------------------------------------------
                # Quality
                # ---------------------------------------------

                "quality": quality,

                # ---------------------------------------------
                # Insights
                # ---------------------------------------------

                "insights": insights,

                # ---------------------------------------------
                # Recommendations
                # ---------------------------------------------

                "recommendations": recommendations,

                # ---------------------------------------------
                # Report
                # ---------------------------------------------

                "report": report,

            }

            # =================================================
            # Build Human-Readable Summary
            # =================================================

            rows = df.shape[0]
            columns = df.shape[1]

            missing = int(
                df.isnull()
                .sum()
                .sum()
            )

            duplicates = int(
                df.duplicated()
                .sum()
            )

            numeric_columns = (
                df.select_dtypes(
                    include="number"
                ).columns.tolist()
            )

            categorical_columns = (
                df.select_dtypes(
                    include=[
                        "object",
                        "category",
                        "bool",
                    ]
                ).columns.tolist()
            )

            summary_lines = [

                "Dataset analysis completed successfully.",

                "",

                f"Rows: {rows}",

                f"Columns: {columns}",

                f"Missing values: {missing}",

                f"Duplicate rows: {duplicates}",

                f"Numerical columns: "
                f"{len(numeric_columns)}",

                f"Categorical columns: "
                f"{len(categorical_columns)}",

            ]

            # =================================================
            # Quality Summary
            # =================================================

            if isinstance(
                quality,
                dict
            ):

                score = quality.get(
                    "score"
                )

                rating = quality.get(
                    "rating"
                )

                if score is not None:

                    summary_lines.append(
                        f"Quality score: "
                        f"{score}/100"
                    )

                if rating:

                    summary_lines.append(
                        f"Quality rating: "
                        f"{rating}"
                    )

            # =================================================
            # Return
            # =================================================

            return AIResponse(

                success=True,

                message="\n".join(
                    summary_lines
                ),

                agent=self.name,

                intent=(
                    context.intent
                    or "analyze_dataset"
                ),

                data=analysis_data,

            )

        except Exception as e:

            logger.exception(
                "AnalysisAgent failed"
            )

            return AIResponse(

                success=False,

                message=str(e),

                agent=self.name,

                intent=(
                    context.intent
                    or "analyze_dataset"
                ),

            )