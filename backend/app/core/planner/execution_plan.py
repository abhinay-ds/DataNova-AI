from dataclasses import dataclass, field
from app.core.execution.ai_task import AITask

@dataclass
class ExecutionPlan:
    objective: str
    tasks: list[AITask] = field(default_factory=list)