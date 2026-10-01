from pydantic import BaseModel


class Workspace(BaseModel):

    project_id: str

    dataset_name: str | None = None

    model_name: str | None = None

    report_name: str | None = None

    chart_paths: list[str] = []

    chat_history: list = []