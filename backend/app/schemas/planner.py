from pydantic import BaseModel, Field


class PlannedTask(BaseModel):

    capability: str

    action: str = ""

    priority: str = "MEDIUM"

    input_data: dict = Field(
        default_factory=dict
    )


class PlannerResponse(BaseModel):

    objective: str

    tasks: list[PlannedTask] = Field(
        default_factory=list
    )