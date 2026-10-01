from __future__ import annotations

from app.services.visualization_service import VisualizationService
from app.tools.base_tool import BaseTool


class PieChartTool(BaseTool):

    @property
    def name(self):
        return "pie_chart"

    @property
    def description(self):
        return (
            "Generate a pie chart from a categorical column "
            "using automatic category counts."
        )

    def execute(self, **kwargs):

        dataset = kwargs.get("dataset")

        if dataset is None or dataset.empty:

            return {
                "success": False,
                "message": "Dataset is required for pie chart."
            }

        # =================================================
        # Explicit column
        # =================================================

        column = (
            kwargs.get("column")
            or kwargs.get("category")
            or kwargs.get("labels")
        )

        # =================================================
        # Explicit labels + values
        # =================================================

        labels = kwargs.get("labels")
        values = kwargs.get("values")

        if (
            labels
            and values
            and labels in dataset.columns
            and values in dataset.columns
        ):

            return VisualizationService.pie_chart(
                df=dataset,
                labels=labels,
                values=values
            )

        # =================================================
        # Requested categorical column
        # =================================================

        if column and column in dataset.columns:

            unique_count = dataset[column].nunique(
                dropna=True
            )

            if unique_count > 20:

                return {
                    "success": False,
                    "message": (
                        f"Column '{column}' has "
                        f"{unique_count} categories. "
                        "A pie chart would be difficult "
                        "to read. Choose a column with "
                        "fewer categories."
                    )
                }

            counts = (
                dataset[column]
                .dropna()
                .value_counts()
                .reset_index()
            )

            counts.columns = [
                column,
                "__count__"
            ]

            return VisualizationService.pie_chart(
                df=counts,
                labels=column,
                values="__count__"
            )

        # =================================================
        # Automatic selection
        # =================================================

        categorical_columns = (
            dataset
            .select_dtypes(
                include=[
                    "object",
                    "category",
                    "bool"
                ]
            )
            .columns
            .tolist()
        )

        # Avoid high-cardinality columns such as:
        # Name, Ticket, ID-like fields.

        suitable_columns = []

        for col in categorical_columns:

            unique_count = dataset[col].nunique(
                dropna=True
            )

            if 2 <= unique_count <= 10:

                suitable_columns.append(
                    col
                )

        if suitable_columns:

            column = suitable_columns[0]

            counts = (
                dataset[column]
                .dropna()
                .value_counts()
                .reset_index()
            )

            counts.columns = [
                column,
                "__count__"
            ]

            return VisualizationService.pie_chart(
                df=counts,
                labels=column,
                values="__count__"
            )

        return {
            "success": False,
            "message": (
                "No suitable categorical column "
                "found for pie chart."
            )
        }