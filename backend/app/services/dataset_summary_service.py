from __future__ import annotations

import pandas as pd

from app.services.llm_service import LLMService


class DatasetSummaryService:
    """
    Generates an AI-powered executive summary of a dataset.
    """

    @classmethod
    def generate(cls, df: pd.DataFrame):

        rows, cols = df.shape

        prompt = f"""
You are DataNova AI.

Analyze the following dataset profile.

Rows: {rows}

Columns: {cols}

Column Names:
{", ".join(df.columns)}

Data Types:
{df.dtypes.to_string()}

Missing Values:
{df.isnull().sum().to_string()}

Duplicate Rows:
{df.duplicated().sum()}

Statistics:
{df.describe(include='all').to_string()}

Write a professional executive summary.

Your response should include:

1. Dataset Overview
2. Data Quality
3. Important Observations
4. Possible Machine Learning Tasks
5. Recommended Charts
6. Suggested Next Steps

Use markdown.
"""

        return LLMService.generate(prompt)