from app.tools.base_tool import BaseTool
from app.services.evaluation_service import EvaluationService


class EvaluateTool(BaseTool):

    @property
    def name(self):
        return "evaluate_model"

    def execute(self, **kwargs):

        dataset = kwargs.get("dataset")
        target = kwargs.get("target")

        if dataset is None:
            raise ValueError("Dataset is required.")

        if target is None:
            raise ValueError("Target column is required.")

        return EvaluationService.evaluate(
            dataset,
            target,
        )