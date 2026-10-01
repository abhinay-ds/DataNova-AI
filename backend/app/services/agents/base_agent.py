from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def capabilities(self) -> list[str]:
        pass

    @abstractmethod
    async def execute(self, context: Any):
        pass