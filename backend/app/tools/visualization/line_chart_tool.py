from __future__ import annotations

import os
import uuid

import matplotlib.pyplot as plt
import pandas as pd

from app.tools.base_tool import BaseTool
from app.core.ai_engine.response import AIResponse


class LineChartTool(BaseTool):

    @property
    def name(self) -> str:
        return "line_chart"

    @property
    def description(self) -> str:
        return (
            "Generate an intelligent line chart. "
            "Numeric Y values are automatically aggregated "
            "by the X column using their mean."
        )

    def execute(
        self,
        dataset: pd.DataFrame,
        x: str,
        y: str,
        **kwargs
    ) -> AIResponse:

        try:

            # =================================================
            # Validate dataset
            # =================================================

            if dataset is None or dataset.empty:

                return AIResponse(
                    success=False,
                    message="Dataset is empty."
                )

            # =================================================
            # Validate columns
            # =================================================

            if x not in dataset.columns:

                return AIResponse(
                    success=False,
                    message=f"Column '{x}' not found."
                )

            if y not in dataset.columns:

                return AIResponse(
                    success=False,
                    message=f"Column '{y}' not found."
                )

            # =================================================
            # Select required columns
            # =================================================

            df = dataset[[x, y]].copy()

            # =================================================
            # Convert Y to numeric
            # =================================================

            df[y] = pd.to_numeric(
                df[y],
                errors="coerce"
            )

            df = df.dropna(
                subset=[y]
            )

            if df.empty:

                return AIResponse(
                    success=False,
                    message=(
                        f"No numeric values available "
                        f"in '{y}'."
                    )
                )

            # =================================================
            # Determine X type
            # =================================================

            x_numeric = pd.api.types.is_numeric_dtype(
                df[x]
            )

            # =================================================
            # Numeric X
            #
            # Example:
            # Age + Fare
            #
            # Age  Fare
            # 20   25
            # 20   30
            # 20   40
            #
            # becomes:
            #
            # Age  Average Fare
            # 20      31.67
            # =================================================

            if x_numeric:

                df[x] = pd.to_numeric(
                    df[x],
                    errors="coerce"
                )

                df = df.dropna(
                    subset=[x]
                )

                grouped = (
                    df.groupby(
                        x,
                        as_index=False
                    )[y]
                    .mean()
                    .sort_values(by=x)
                )

                x_label = x
                y_label = f"Average {y}"
                title = f"Average {y} vs {x}"

            # =================================================
            # Categorical X
            #
            # Example:
            # Month + Sales
            #
            # Automatically calculate average Y
            # for each category.
            # =================================================

            else:

                # Remove extremely high-cardinality columns
                # such as Name or Ticket when possible.
                unique_count = df[x].nunique(
                    dropna=True
                )

                if unique_count > 100:

                    return AIResponse(
                        success=False,
                        message=(
                            f"Column '{x}' has too many "
                            f"unique values ({unique_count}) "
                            "for a meaningful line chart. "
                            "Please choose a lower-cardinality "
                            "column."
                        )
                    )

                grouped = (
                    df.dropna(subset=[x])
                    .groupby(
                        x,
                        as_index=False
                    )[y]
                    .mean()
                )

                x_label = x
                y_label = f"Average {y}"
                title = f"Average {y} by {x}"

            # =================================================
            # Validate grouped result
            # =================================================

            if grouped.empty:

                return AIResponse(
                    success=False,
                    message="Unable to create chart from the selected columns."
                )

            # =================================================
            # Limit extremely large categorical charts
            # =================================================

            if len(grouped) > 100:

                return AIResponse(
                    success=False,
                    message=(
                        "The selected X column produces too many "
                        "categories for a readable line chart. "
                        "Please choose a more suitable column."
                    )
                )

            # =================================================
            # Output directory
            # =================================================

            output_dir = os.path.join(
                "outputs",
                "charts"
            )

            os.makedirs(
                output_dir,
                exist_ok=True
            )

            filename = (
                f"{uuid.uuid4().hex}.png"
            )

            chart_path = os.path.join(
                output_dir,
                filename
            )

            # =================================================
            # Create chart
            # =================================================

            plt.figure(
                figsize=(10, 6)
            )

            plt.plot(
                grouped[x],
                grouped[y],
                marker="o",
                linewidth=2
            )

            plt.xlabel(
                x_label
            )

            plt.ylabel(
                y_label
            )

            plt.title(
                title
            )

            plt.grid(
                True,
                alpha=0.3
            )

            plt.tight_layout()

            # =================================================
            # Save
            # =================================================

            plt.savefig(
                chart_path,
                dpi=150,
                bbox_inches="tight"
            )

            plt.close()

            # =================================================
            # Return
            # =================================================

            return AIResponse(
                success=True,
                message="Line chart generated successfully.",
                data={
                    "chart_type": "line_chart",
                    "chart_path": chart_path,
                    "x": x,
                    "y": y,
                    "aggregation": "mean",
                    "points": len(grouped),
                }
            )

        except Exception as e:

            plt.close("all")

            return AIResponse(
                success=False,
                message=str(e)
            )