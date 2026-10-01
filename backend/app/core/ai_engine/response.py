from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AIResponse:

    success: bool

    message: str

    data: Dict[str, Any] = field(default_factory=dict)

    agent: str = ""

    intent: str = ""

    execution_time: float = 0.0