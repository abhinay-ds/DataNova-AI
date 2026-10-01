from app.core.ai_engine.context import AIContext
from app.core.ai_engine.router import AIRouter


class AIEngine:

    def __init__(
        self,
        capability_registry,
        tool_registry
    ):

        self.router = AIRouter(
            capability_registry=capability_registry,
            tool_registry=tool_registry
        )

    async def execute(
        self,
        context: AIContext
    ):

        return await self.router.route(context)