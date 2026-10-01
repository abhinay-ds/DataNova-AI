from dataclasses import dataclass, field
from typing import Any

from app.core.ai_engine.response import AIResponse
from app.core.execution.ai_task import AITask


@dataclass
class ExecutionResult:

    success: bool
    message: str = ""

    responses: list[AIResponse] = field(default_factory=list)

    task_results: dict[str, Any] = field(default_factory=dict)

    completed_tasks: list[AITask] = field(default_factory=list)

    failed_tasks: list[AITask] = field(default_factory=list)