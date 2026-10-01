from typing import Dict, List

from app.services.agents.base_agent import BaseAgent


class CapabilityRegistry:
    """
    Stores and manages the mapping between
    capabilities and their corresponding agents.
    """

    def __init__(self):
        self._registry: Dict[str, BaseAgent] = {}

    def register(self, capability: str, agent: BaseAgent) -> None:
        """
        Register an agent for a capability.
        """

        capability = capability.lower().strip()

        if capability in self._registry:
            raise ValueError(
                f"Capability '{capability}' is already registered."
            )

        self._registry[capability] = agent

    def get_agent(self, capability: str) -> BaseAgent:
        """
        Retrieve the agent responsible for a capability.
        """

        capability = capability.lower().strip()

        if capability not in self._registry:
            raise ValueError(
                f"No agent registered for capability '{capability}'."
            )

        return self._registry[capability]

    def has_capability(self, capability: str) -> bool:
        """
        Check whether a capability exists.
        """

        return capability.lower().strip() in self._registry

    def unregister(self, capability: str) -> None:
        """
        Remove a capability from the registry.
        """

        capability = capability.lower().strip()

        if capability in self._registry:
            del self._registry[capability]

    def list_capabilities(self) -> List[str]:
        """
        Return all registered capabilities.
        """

        return sorted(self._registry.keys())

    def clear(self) -> None:
        """
        Remove every registered capability.
        """

        self._registry.clear()

    def __len__(self) -> int:
        return len(self._registry)

    def __contains__(self, capability: str) -> bool:
        return capability.lower().strip() in self._registry

    def __repr__(self) -> str:
        return (
            f"CapabilityRegistry("
            f"{len(self._registry)} capabilities)"
        )