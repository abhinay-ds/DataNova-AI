from app.services.visualization_service import VisualizationService
from app.tools.base_tool import BaseTool


class BoxPlotTool(BaseTool):

    @property
    def name(self):
        return "boxplot"

    def execute(self, **kwargs):

        dataset = kwargs.get("dataset")

        if dataset is None:
            return {
                "success": False,
                "message": "Dataset is required for boxplot."
            }

        column = kwargs.get("column")

        # -----------------------------------------
        # Automatically select a numerical column
        # if planner did not provide one
        # -----------------------------------------

        if column is None:

            numeric_columns = (
                dataset
                .select_dtypes(include="number")
                .columns
                .tolist()
            )

            if not numeric_columns:
                return {
                    "success": False,
                    "message": (
                        "No numerical columns are available "
                        "for a boxplot."
                    )
                }

            column = numeric_columns[0]

        # -----------------------------------------
        # Generate boxplot
        # -----------------------------------------

        return VisualizationService.boxplot(
            df=dataset,
            column=column,
        )