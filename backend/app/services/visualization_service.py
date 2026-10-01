from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

import matplotlib.pyplot as plt
import pandas as pd

from app.core.ai_engine.response import AIResponse
logger = logging.getLogger(__name__)


class VisualizationService:

    OUTPUT_DIR = Path("outputs/charts")

    # =========================================================
    # Internal Helpers
    # =========================================================

    @classmethod
    def _prepare_output_directory(cls):

        cls.OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    @classmethod
    def _save_current_figure(cls):

        cls._prepare_output_directory()

        filename = f"{uuid4().hex}.png"

        path = cls.OUTPUT_DIR / filename

        plt.tight_layout()

        plt.savefig(
            path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        return str(path)

    @classmethod
    def _validate_columns(
        cls,
        df: pd.DataFrame,
        *columns
    ):

        for column in columns:

            if column not in df.columns:

                return AIResponse(
                    success=False,
                    message=f"Column '{column}' not found."
                )

        return None

    # =========================================================
    # Histogram
    # =========================================================

    @classmethod
    def histogram(
        cls,
        df: pd.DataFrame,
        column: str,
    ) -> AIResponse:

        try:

            error = cls._validate_columns(
                df,
                column
            )

            if error:
                return error

            plt.figure(
                figsize=(8, 5)
            )

            df[column].hist(
                bins=20
            )

            plt.title(
                f"Histogram of {column}"
            )

            plt.xlabel(column)

            plt.ylabel(
                "Frequency"
            )

            chart_path = (
                cls._save_current_figure()
            )

            return AIResponse(
                success=True,
                message="Histogram generated successfully.",
                data={
                    "chart_type": "histogram",
                    "chart_path": chart_path,
                    "column": column,
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )

    # =========================================================
    # Scatter Plot
    # =========================================================

    @classmethod
    def scatter(
        cls,
        df: pd.DataFrame,
        x: str,
        y: str,
    ) -> AIResponse:

        try:

            error = cls._validate_columns(
                df,
                x,
                y
            )

            if error:
                return error

            plt.figure(
                figsize=(8, 5)
            )

            plt.scatter(
                df[x],
                df[y]
            )

            plt.title(
                f"{y} vs {x}"
            )

            plt.xlabel(x)

            plt.ylabel(y)

            chart_path = (
                cls._save_current_figure()
            )

            return AIResponse(
                success=True,
                message="Scatter plot generated successfully.",
                data={
                    "chart_type": "scatter",
                    "chart_path": chart_path,
                    "x": x,
                    "y": y,
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )

    # =========================================================
    # Line Chart
    # =========================================================

    @classmethod
    def line_chart(
        cls,
        df: pd.DataFrame,
        x: str,
        y: str,
    ) -> AIResponse:

        try:

            error = cls._validate_columns(
                df,
                x,
                y
            )

            if error:
                return error

            plt.figure(
                figsize=(8, 5)
            )

            plt.plot(
                df[x],
                df[y],
                marker="o"
            )

            plt.title(
                f"{y} vs {x}"
            )

            plt.xlabel(x)

            plt.ylabel(y)

            chart_path = (
                cls._save_current_figure()
            )

            return AIResponse(
                success=True,
                message="Line chart generated successfully.",
                data={
                    "chart_type": "line_chart",
                    "chart_path": chart_path,
                    "x": x,
                    "y": y,
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )

    # =========================================================
    # Bar Chart
    # =========================================================

    @classmethod
    def bar_chart(
        cls,
        df: pd.DataFrame,
        x: str,
        y: str,
    ) -> AIResponse:

        try:

            error = cls._validate_columns(
                df,
                x,
                y
            )

            if error:
                return error

            plt.figure(
                figsize=(8, 5)
            )

            plt.bar(
                df[x],
                df[y]
            )

            plt.title(
                f"{y} by {x}"
            )

            plt.xlabel(x)

            plt.ylabel(y)

            chart_path = (
                cls._save_current_figure()
            )

            return AIResponse(
                success=True,
                message="Bar chart generated successfully.",
                data={
                    "chart_type": "bar_chart",
                    "chart_path": chart_path,
                    "x": x,
                    "y": y,
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )

            # =========================================================
    # Smart Chart
    # =========================================================

    @classmethod
    def smart_chart(
        cls,
        df: pd.DataFrame,
        x: str,
        y: str,
        aggregation: str = "mean",
        chart_type: str = "bar",
    ) -> AIResponse:

        try:

            # -------------------------------------------------
            # Validate columns
            # -------------------------------------------------

            error = cls._validate_columns(
                df,
                x,
                y
            )

            if error:
                return error

            # -------------------------------------------------
            # Validate aggregation
            # -------------------------------------------------

            allowed_aggregations = {
                "mean",
                "sum",
                "count",
                "median",
                "min",
                "max",
            }

            aggregation = aggregation.lower()

            if aggregation not in allowed_aggregations:

                return AIResponse(
                    success=False,
                    message=(
                        f"Unsupported aggregation '{aggregation}'. "
                        f"Supported aggregations are: "
                        f"{', '.join(sorted(allowed_aggregations))}."
                    )
                )

            # -------------------------------------------------
            # Validate chart type
            # -------------------------------------------------

            allowed_chart_types = {
                "bar",
                "line",
            }

            chart_type = chart_type.lower()

            if chart_type not in allowed_chart_types:

                return AIResponse(
                    success=False,
                    message=(
                        f"Unsupported smart chart type "
                        f"'{chart_type}'. "
                        f"Supported types are: bar, line."
                    )
                )

            # -------------------------------------------------
            # Perform aggregation
            # -------------------------------------------------

            grouped = df.groupby(
                x,
                dropna=False
            )[y]

            if aggregation == "mean":
                aggregated = grouped.mean()

            elif aggregation == "sum":
                aggregated = grouped.sum()

            elif aggregation == "count":
                aggregated = grouped.count()

            elif aggregation == "median":
                aggregated = grouped.median()

            elif aggregation == "min":
                aggregated = grouped.min()

            elif aggregation == "max":
                aggregated = grouped.max()

            aggregated = aggregated.dropna()

            if aggregated.empty:

                return AIResponse(
                    success=False,
                    message=(
                        "No valid data was available "
                        "after aggregation."
                    )
                )

            # -------------------------------------------------
            # Generate chart
            # -------------------------------------------------

            plt.figure(
                figsize=(8, 5)
            )

            if chart_type == "bar":

                plt.bar(
                    aggregated.index.astype(str),
                    aggregated.values
                )

            elif chart_type == "line":

                plt.plot(
                    aggregated.index.astype(str),
                    aggregated.values,
                    marker="o"
                )

            # -------------------------------------------------
            # Labels
            # -------------------------------------------------

            aggregation_label = aggregation.capitalize()

            plt.title(
                f"{aggregation_label} {y} by {x}"
            )

            plt.xlabel(x)

            plt.ylabel(
                f"{aggregation_label} of {y}"
            )

            plt.xticks(
                rotation=0
            )

            # -------------------------------------------------
            # Save chart
            # -------------------------------------------------

            chart_path = (
                cls._save_current_figure()
            )

            # -------------------------------------------------
            # Response
            # -------------------------------------------------

            return AIResponse(
                success=True,
                message=(
                    "Smart chart generated successfully."
                ),
                data={
                    "chart_type": (
                        "bar_chart"
                        if chart_type == "bar"
                        else "line_chart"
                    ),
                    "chart_path": chart_path,
                    "x": x,
                    "y": y,
                    "aggregation": aggregation,
                    "rows": len(aggregated),
                    "values": {
                        str(index): float(value)
                        for index, value
                        in aggregated.items()
                    },
                },
            )

        except Exception as e:

            logger.exception(
                "Smart chart generation failed."
            )

            return AIResponse(
                success=False,
                message=str(e),
            )

    # =========================================================
    # Pie Chart
    # =========================================================

    @classmethod
    def pie_chart(
        cls,
        df: pd.DataFrame,
        labels: str,
        values: str,
    ) -> AIResponse:

        try:

            error = cls._validate_columns(
                df,
                labels,
                values
            )

            if error:
                return error

            plt.figure(
                figsize=(8, 8)
            )

            plt.pie(
                df[values],
                labels=df[labels],
                autopct="%1.1f%%",
                startangle=90
            )

            plt.title(
                f"{values} by {labels}"
            )

            chart_path = (
                cls._save_current_figure()
            )

            return AIResponse(
                success=True,
                message="Pie chart generated successfully.",
                data={
                    "chart_type": "pie_chart",
                    "chart_path": chart_path,
                    "labels": labels,
                    "values": values,
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )

    # =========================================================
    # Boxplot
    # =========================================================

    @classmethod
    def boxplot(
        cls,
        df: pd.DataFrame,
        column: str,
    ) -> AIResponse:

        try:

            error = cls._validate_columns(
                df,
                column
            )

            if error:
                return error

            plt.figure(
                figsize=(8, 5)
            )

            plt.boxplot(
                df[column].dropna()
            )

            plt.title(
                f"Box Plot of {column}"
            )

            plt.ylabel(column)

            chart_path = (
                cls._save_current_figure()
            )

            return AIResponse(
                success=True,
                message="Box plot generated successfully.",
                data={
                    "chart_type": "boxplot",
                    "chart_path": chart_path,
                    "column": column,
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )

        # =========================================================
    # Correlation
    # =========================================================

    @classmethod
    def correlation(
        cls,
        df: pd.DataFrame,
    ) -> AIResponse:

        try:

            identifier_columns = {
                "id",
                "passengerid",
                "customerid",
                "userid",
                "user_id",
                "index",
                "rowid",
                "recordid",
                "record_id",
            }

            def is_identifier(column):

                normalized = (
                    str(column)
                    .lower()
                    .replace(" ", "")
                    .replace("_", "")
                    .replace("-", "")
                )

                normalized_identifiers = {
                    str(name)
                    .lower()
                    .replace(" ", "")
                    .replace("_", "")
                    .replace("-", "")
                    for name in identifier_columns
                }

                return normalized in normalized_identifiers

            numeric_columns = [
                column
                for column in df.select_dtypes(
                    include="number"
                ).columns
                if not is_identifier(column)
            ]

            if len(numeric_columns) < 2:

                return AIResponse(
                    success=False,
                    message=(
                        "At least two meaningful numeric "
                        "columns are required for correlation."
                    ),
                )

            correlation = df[
                numeric_columns
            ].corr()

            if correlation.empty:

                return AIResponse(
                    success=False,
                    message=(
                        "No numeric columns available "
                        "for correlation analysis."
                    ),
                )

            return AIResponse(
                success=True,
                message=(
                    "Correlation matrix generated successfully."
                ),
                data={
                    "correlation_matrix":
                        correlation.round(
                            3
                        ).to_dict(),

                    "columns":
                        correlation.columns.tolist(),
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )
       # =========================================================
    # Heatmap
    # =========================================================

    @classmethod
    def heatmap(
        cls,
        df: pd.DataFrame,
    ) -> AIResponse:

        try:

            # -------------------------------------------------
            # Remove identifier columns
            # -------------------------------------------------

            identifier_columns = {
                "id",
                "passengerid",
                "customerid",
                "userid",
                "user_id",
                "index",
                "rowid",
                "recordid",
                "record_id",
            }

            def is_identifier(column):

                normalized = (
                    str(column)
                    .lower()
                    .replace(" ", "")
                    .replace("_", "")
                    .replace("-", "")
                )

                normalized_identifiers = {
                    str(name)
                    .lower()
                    .replace(" ", "")
                    .replace("_", "")
                    .replace("-", "")
                    for name in identifier_columns
                }

                return normalized in normalized_identifiers

            # -------------------------------------------------
            # Select meaningful numeric columns only
            # -------------------------------------------------

            numeric_columns = [
                column
                for column in df.select_dtypes(
                    include="number"
                ).columns
                if not is_identifier(column)
            ]

            if len(numeric_columns) < 2:

                return AIResponse(
                    success=False,
                    message=(
                        "At least two meaningful numeric "
                        "columns are required for a heatmap."
                    ),
                )

            # -------------------------------------------------
            # Correlation
            # -------------------------------------------------

            correlation = df[
                numeric_columns
            ].corr()

            if correlation.empty:

                return AIResponse(
                    success=False,
                    message=(
                        "No numeric columns available "
                        "for heatmap."
                    ),
                )

            # -------------------------------------------------
            # Generate heatmap
            # -------------------------------------------------

            plt.figure(
                figsize=(10, 8)
            )

            plt.imshow(
                correlation,
                interpolation="nearest",
                aspect="auto"
            )

            plt.colorbar()

            plt.xticks(
                range(
                    len(correlation.columns)
                ),
                correlation.columns,
                rotation=90
            )

            plt.yticks(
                range(
                    len(correlation.columns)
                ),
                correlation.columns
            )

            plt.title(
                "Correlation Heatmap"
            )

            chart_path = (
                cls._save_current_figure()
            )

            # -------------------------------------------------
            # Response
            # -------------------------------------------------

            return AIResponse(
                success=True,
                message=(
                    "Heatmap generated successfully."
                ),
                data={
                    "chart_type": "heatmap",
                    "chart_path": chart_path,
                    "columns":
                        correlation.columns.tolist(),
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )