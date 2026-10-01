from __future__ import annotations

import pandas as pd

from app.core.ai_engine.response import AIResponse


class RecommendationService:
    """
    Generates preprocessing recommendations.
    """

    @classmethod
    def generate(cls, df: pd.DataFrame):

        recommendations = []

        if df.isnull().sum().sum():

            recommendations.append(
                "Handle missing values before training."
            )

        if df.duplicated().sum():

            recommendations.append(
                "Remove duplicate rows."
            )

        if len(df.select_dtypes(include="number").columns) > 0:

            recommendations.append(
                "Consider feature scaling for numerical columns."
            )

        if len(df.select_dtypes(include="object").columns) > 0:

            recommendations.append(
                "Encode categorical variables before machine learning."
            )

        if not recommendations:

            recommendations.append(
                "Dataset looks clean and ready for analysis."
            )

        return AIResponse(
            success=True,
            message="Recommendations generated successfully.",
            data=recommendations,
        )