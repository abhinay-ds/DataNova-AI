from abc import ABC, abstractmethod


class BaseTool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool name."""
        pass

    @abstractmethod
    def execute(self, **kwargs):
        """Execute the tool."""
        pass