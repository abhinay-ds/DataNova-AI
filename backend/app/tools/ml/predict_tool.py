from app.tools.base_tool import BaseTool
from app.services.prediction_service import PredictionService


class PredictTool(BaseTool):

    @property
    def name(self):
        return "predict"

    def execute(self, **kwargs):

        dataset = kwargs.get("dataset")

        if dataset is None:
            raise ValueError(
                "Dataset is required."
            )

        return PredictionService.predict(
            dataset
        )