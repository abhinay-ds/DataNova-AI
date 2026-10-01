import os
import pandas as pd

from app.services.dataset_profiler_service import DatasetProfilerService
from app.services.quality_service import QualityService
from app.services.insight_service import InsightService
from app.services.recommendation_service import RecommendationService
from app.services.dataset_summary_service import DatasetSummaryService


class FileService:

    # =====================================================
    # Load Dataset
    # =====================================================

    @staticmethod
    def load_dataframe(file_path: str) -> pd.DataFrame:

        extension = os.path.splitext(
            file_path
        )[1].lower()

        if extension == ".csv":

            return pd.read_csv(
                file_path
            )

        elif extension in [".xlsx", ".xls"]:

            return pd.read_excel(
                file_path
            )

        elif extension == ".json":

            return pd.read_json(
                file_path
            )

        raise ValueError(
            "Unsupported file format"
        )


    # =====================================================
    # Analyze Dataset
    # =====================================================

    @classmethod
    def analyze_dataset(
        cls,
        file_path: str
    ):

        # -------------------------------------------------
        # Load dataframe
        # -------------------------------------------------

        df = cls.load_dataframe(
            file_path
        )


        # -------------------------------------------------
        # Store dataset for Chat / AI analysis
        # -------------------------------------------------

        

        # -------------------------------------------------
        # Generate analysis components
        # -------------------------------------------------

        profile = (
            DatasetProfilerService.profile(
                df
            )
        )

        quality = (
            QualityService.evaluate(
                df
            )
        )

        insights = (
            InsightService.generate(
                df
            )
        )

        recommendations = (
            RecommendationService.generate(
                df
            )
        )

        summary = (
            DatasetSummaryService.generate(
                df
            )
        )


        # -------------------------------------------------
        # Dataset Preview
        # -------------------------------------------------
        #
        # Send first 5 rows to frontend.
        #
        # fillna("") ensures missing values are
        # JSON-friendly.
        # -------------------------------------------------

        preview_df = (
            df.head(5)
            .fillna("")
        )

        preview = (
            preview_df
            .to_dict(
                orient="records"
            )
        )


        # -------------------------------------------------
        # Return Complete Dataset Information
        # -------------------------------------------------

        return {

            # Original filename
            "filename": os.path.basename(
                file_path
            ),

            # Dataset profile
            "profile": profile.data,

            # Data quality
            "quality": quality.data,

            # Automatic insights
            "insights": insights.data,

            # Recommendations
            "recommendations": recommendations.data,

            # Dataset summary
            "summary": summary.data,

            # First 5 rows
            "preview": preview,
        }