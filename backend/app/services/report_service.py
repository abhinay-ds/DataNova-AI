from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from app.core.ai_engine.response import AIResponse
from app.services.dataset_profiler_service import DatasetProfilerService
from app.services.quality_service import QualityService
from app.services.recommendation_service import RecommendationService
from app.services.insight_service import InsightService


class ReportService:

    REPORT_FOLDER = Path("static/reports")

    @classmethod
    def generate(cls, df: pd.DataFrame) -> AIResponse:

        try:

            # =================================================
            # Validate dataset
            # =================================================

            if df is None or df.empty:

                return AIResponse(
                    success=False,
                    message="Dataset is empty.",
                    data=None,
                )

            # =================================================
            # Create report directory
            # =================================================

            cls.REPORT_FOLDER.mkdir(
                parents=True,
                exist_ok=True
            )

            # =================================================
            # Dataset Profile
            # =================================================

            profile_response = (
                DatasetProfilerService.profile(df)
            )

            if not profile_response.success:

                return AIResponse(
                    success=False,
                    message=profile_response.message,
                    data=None,
                )

            profile = profile_response.data

            # =================================================
            # Dataset Quality
            # =================================================

            quality_response = (
                QualityService.evaluate(df)
            )

            if not quality_response.success:

                return AIResponse(
                    success=False,
                    message=quality_response.message,
                    data=None,
                )

            quality = quality_response.data

            # =================================================
            # Recommendations
            # =================================================

            recommendation_response = (
                RecommendationService.generate(df)
            )

            if not recommendation_response.success:

                return AIResponse(
                    success=False,
                    message=recommendation_response.message,
                    data=None,
                )

            recommendation = (
                recommendation_response.data
            )

            # =================================================
            # Insights
            # =================================================

            insight_response = (
                InsightService.generate(df)
            )

            if not insight_response.success:

                return AIResponse(
                    success=False,
                    message=insight_response.message,
                    data=None,
                )

            insight = insight_response.data

            # =================================================
            # Build Report
            # =================================================

            report = {

                "generated_at":
                    datetime.now().isoformat(),

                "profile":
                    profile,

                "quality":
                    quality,

                "recommendations":
                    recommendation,

                "insights":
                    insight,
            }

            # =================================================
            # Return Report
            # =================================================

            return AIResponse(
                success=True,
                message="Report generated successfully.",
                data=report,
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
                data=None,
            )