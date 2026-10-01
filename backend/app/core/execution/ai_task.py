from dataclasses import dataclass, field

from app.core.execution.task_status import TaskStatus
from app.core.execution.task_priority import TaskPriority


@dataclass
class AITask:
    id: str
    capability: str
    action: str

    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM

    dependencies: list[str] = field(default_factory=list)
    input_data: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)