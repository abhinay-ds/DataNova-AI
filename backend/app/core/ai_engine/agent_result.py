from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:

    agent: str

    success: bool

    data: Any = None

    message: str = ""