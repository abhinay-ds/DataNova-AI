from __future__ import annotations

import pandas as pd

from app.services.visualization_service import VisualizationService
from app.tools.base_tool import BaseTool


class BarChartTool(BaseTool):

    @property
    def name(self):
        return "bar_chart"

    @property
    def description(self):
        return (
            "Generate an intelligent bar chart. "
            "Categorical columns are counted automatically, "
            "while numeric values can be aggregated."
        )

    def execute(self, **kwargs):

        dataset = kwargs.get("dataset")

        if dataset is None or dataset.empty:

            raise ValueError(
                "Dataset is required for bar chart."
            )

        # =================================================
        # Get requested columns
        # =================================================

        column = (
            kwargs.get("column")
            or kwargs.get("category")
        )

        x = (
            kwargs.get("x")
            or kwargs.get("x_column")
            or kwargs.get("category")
        )

        y = (
            kwargs.get("y")
            or kwargs.get("y_column")
            or kwargs.get("value")
        )

        # =================================================
        # Single categorical column
        #
        # Example:
        # "Create a bar chart of Sex"
        #
        # Sex
        # male
        # female
        #
        # becomes:
        #
        # male     577
        # female   314
        # =================================================

        if column and column in dataset.columns:

            series = dataset[column].dropna()

            unique_count = series.nunique()

            if unique_count > 50:

                raise ValueError(
                    f"Column '{column}' has {unique_count} "
                    "unique values. Please choose a "
                    "lower-cardinality categorical column."
                )

            counts = (
                series
                .value_counts()
                .reset_index()
            )

            counts.columns = [
                column,
                "__count__"
            ]

            return VisualizationService.bar_chart(
                df=counts,
                x=column,
                y="__count__"
            )

        # =================================================
        # Standard X/Y bar chart
        # =================================================

        if not x:

            raise ValueError(
                "Bar chart requires an x/category column."
            )

        if not y:

            raise ValueError(
                "Bar chart requires a y/value column."
            )

        if x not in dataset.columns:

            raise ValueError(
                f"Column '{x}' not found in dataset."
            )

        if y not in dataset.columns:

            raise ValueError(
                f"Column '{y}' not found in dataset."
            )

        df = dataset[[x, y]].copy()

        # =================================================
        # Numeric Y
        # =================================================

        df[y] = pd.to_numeric(
            df[y],
            errors="coerce"
        )

        df = df.dropna(
            subset=[x, y]
        )

        if df.empty:

            raise ValueError(
                "No valid data available for bar chart."
            )

        # =================================================
        # Categorical X + Numeric Y
        #
        # Automatically calculate mean.
        #
        # Example:
        #
        # Sex + Fare
        #
        # becomes:
        #
        # female -> average Fare
        # male   -> average Fare
        # =================================================

        if not pd.api.types.is_numeric_dtype(
            df[x]
        ):

            grouped = (
                df.groupby(
                    x,
                    as_index=False
                )[y]
                .mean()
            )

            return VisualizationService.bar_chart(
                df=grouped,
                x=x,
                y=y
            )

        # =================================================
        # Numeric X + Numeric Y
        #
        # Group repeated X values.
        # =================================================

        grouped = (
            df.groupby(
                x,
                as_index=False
            )[y]
            .mean()
            .sort_values(by=x)
        )

        return VisualizationService.bar_chart(
            df=grouped,
            x=x,
            y=y
        )