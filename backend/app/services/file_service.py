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
        file_path: str,
        df: pd.DataFrame | None = None,
        include_llm_summary: bool = False,
    ):

        # -------------------------------------------------
        # Load dataframe (reuse passed dataframe if available)
        # -------------------------------------------------

        if df is None:
            df = cls.load_dataframe(
                file_path
            )

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

        # -------------------------------------------------
        # Dataset Preview
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
        # Summary (use fast summary by default to eliminate 2s latency)
        # -------------------------------------------------
        if include_llm_summary:
            summary_res = DatasetSummaryService.generate(df)
            summary_data = summary_res.data if hasattr(summary_res, "data") else summary_res
        else:
            summary_data = {
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "preview": preview,
            }

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
            "summary": summary_data,

            # First 5 rows
            "preview": preview,
        }