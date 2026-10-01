from __future__ import annotations

import pandas as pd

from app.core.ai_engine.response import AIResponse


class QualityService:
    """
    Computes an overall dataset quality score.
    """

    @classmethod
    def evaluate(cls, df: pd.DataFrame) -> AIResponse:

        score = 100

        issues = []

        # -------------------------
        # Missing Values
        # -------------------------

        missing = int(df.isnull().sum().sum())

        if missing:

            penalty = min(20, missing // 10 + 5)

            score -= penalty

            issues.append(
                f"{missing} missing values detected."
            )

        # -------------------------
        # Duplicate Rows
        # -------------------------

        duplicates = int(df.duplicated().sum())

        if duplicates:

            penalty = min(10, duplicates)

            score -= penalty

            issues.append(
                f"{duplicates} duplicate rows detected."
            )

        # -------------------------
        # Constant Columns
        # -------------------------

        constant_columns = []

        for column in df.columns:

            if df[column].nunique(dropna=False) <= 1:
                constant_columns.append(column)

        if constant_columns:

            score -= len(constant_columns) * 2

            issues.append(
                f"{len(constant_columns)} constant columns found."
            )

        # -------------------------
        # Empty Dataset
        # -------------------------

        if df.empty:

            score = 0

            issues.append(
                "Dataset is empty."
            )

        # -------------------------
        # Score Limits
        # -------------------------

        score = max(0, min(score, 100))

        # -------------------------
        # Rating
        # -------------------------

        if score >= 90:

            rating = "Excellent"

        elif score >= 75:

            rating = "Good"

        elif score >= 60:

            rating = "Average"

        elif score >= 40:

            rating = "Poor"

        else:

            rating = "Very Poor"

        return AIResponse(
            success=True,
            message="Quality score generated successfully.",
            data={
                "score": score,
                "rating": rating,
                "issues": issues,
            },
        )