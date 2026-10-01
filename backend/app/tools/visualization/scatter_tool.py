from __future__ import annotations

import pandas as pd

from app.services.visualization_service import VisualizationService
from app.tools.base_tool import BaseTool


class ScatterTool(BaseTool):

    @property
    def name(self):
        return "scatter"

    @property
    def description(self):
        return (
            "Generate a scatter plot using two numeric columns."
        )

    def execute(self, **kwargs):

        dataset = kwargs.get("dataset")

        if dataset is None or dataset.empty:

            raise ValueError(
                "Dataset is required for scatter plot."
            )

        # =================================================
        # Get X
        # =================================================

        x = (
            kwargs.get("x")
            or kwargs.get("x_column")
            or kwargs.get("x_axis")
        )

        # =================================================
        # Get Y
        # =================================================

        y = (
            kwargs.get("y")
            or kwargs.get("y_column")
            or kwargs.get("y_axis")
        )

        if not x:

            raise ValueError(
                "Scatter plot requires an x-axis column."
            )

        if not y:

            raise ValueError(
                "Scatter plot requires a y-axis column."
            )

        # =================================================
        # Validate columns
        # =================================================

        if x not in dataset.columns:

            raise ValueError(
                f"Column '{x}' not found in dataset."
            )

        if y not in dataset.columns:

            raise ValueError(
                f"Column '{y}' not found in dataset."
            )

        # =================================================
        # Prepare data
        # =================================================

        df = dataset[[x, y]].copy()

        df[x] = pd.to_numeric(
            df[x],
            errors="coerce"
        )

        df[y] = pd.to_numeric(
            df[y],
            errors="coerce"
        )

        df = df.dropna(
            subset=[x, y]
        )

        if df.empty:

            raise ValueError(
                "The selected columns do not contain "
                "enough numeric data for a scatter plot."
            )

        # =================================================
        # Generate chart
        # =================================================

        response = VisualizationService.scatter(
            df=df,
            x=x,
            y=y,
        )

        # =================================================
        # Add metadata
        # =================================================

        if hasattr(response, "data") and response.data:

            response.data["rows_used"] = len(df)

        return response