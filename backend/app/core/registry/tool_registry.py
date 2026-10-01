from __future__ import annotations

from typing import Dict

from app.tools.base_tool import BaseTool


class ToolRegistry:
    """
    Registry for all tools available in DataNova AI.
    """

    def __init__(self) -> None:
        self._registry: Dict[str, BaseTool] = {}

    # -----------------------------------------
    # Register Tool
    # -----------------------------------------

    def register(
        self,
        name: str,
        tool: BaseTool
    ) -> None:

        name = name.lower().strip()

        if name in self._registry:
            raise ValueError(
                f"Tool '{name}' is already registered."
            )

        self._registry[name] = tool

    # -----------------------------------------
    # Get Tool
    # -----------------------------------------

    def get(
        self,
        name: str
    ) -> BaseTool:

        name = name.lower().strip()

        if name not in self._registry:
            raise ValueError(
                f"Tool '{name}' is not registered."
            )

        return self._registry[name]

    # -----------------------------------------
    # Check Tool
    # -----------------------------------------

    def has_tool(
        self,
        name: str
    ) -> bool:

        return name.lower().strip() in self._registry

    # -----------------------------------------
    # List Tools
    # -----------------------------------------

    def list_tools(self) -> list[str]:

        return sorted(
            self._registry.keys()
        )

    # -----------------------------------------
    # Remove Tool
    # -----------------------------------------

    def unregister(
        self,
        name: str
    ) -> None:

        name = name.lower().strip()

        if name not in self._registry:
            raise ValueError(
                f"Tool '{name}' is not registered."
            )

        del self._registry[name]

    # -----------------------------------------
    # Clear Registry
    # -----------------------------------------

    def clear(self) -> None:
        self._registry.clear()

    # -----------------------------------------
    # Magic Methods
    # -----------------------------------------

    def __contains__(
        self,
        name: str
    ) -> bool:

        return self.has_tool(name)

    def __len__(self) -> int:

        return len(self._registry)