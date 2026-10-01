from app.core.ai_engine.context import AIContext
from app.core.planner.planner_agent import PlannerAgent
from app.core.orchestrator.orchestrator import AgentOrchestrator


class AIRouter:

    def __init__(
        self,
        capability_registry,
        tool_registry
    ):

        # -----------------------------------------
        # Registries
        # -----------------------------------------

        self.capability_registry = (
            capability_registry
        )

        self.tool_registry = (
            tool_registry
        )

        # -----------------------------------------
        # Planner
        # -----------------------------------------

        self.planner = PlannerAgent()

        # -----------------------------------------
        # Orchestrator
        # -----------------------------------------

        self.orchestrator = AgentOrchestrator(
            capability_registry
        )

    async def route(
        self,
        context: AIContext
    ):

        # -----------------------------------------
        # Attach runtime registries to context
        # -----------------------------------------

        context.capability_registry = (
            self.capability_registry
        )

        context.tool_registry = (
            self.tool_registry
        )

        # -----------------------------------------
        # Planner
        # -----------------------------------------

        plan = await self.planner.execute(
            context
        )

        # -----------------------------------------
        # Store plan
        # -----------------------------------------

        context.execution_plan = plan

        # -----------------------------------------
        # Execute plan
        # -----------------------------------------

        result = await self.orchestrator.execute(
            plan,
            context
        )

        return result