from app.tools.base_tool import BaseTool
from app.services.ml_service import MLService


class TrainModelTool(BaseTool):

    @property
    def name(self) -> str:
        return "train_model"

    def execute(self, **kwargs):

        dataset = kwargs.get("dataset")
        target = kwargs.get("target")

        if dataset is None:
            raise ValueError("Dataset is required.")

        if target is None:
            raise ValueError("Target column is required.")

        return MLService.train(
            df=dataset,
            target=target
        )