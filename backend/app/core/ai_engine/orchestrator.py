import logging
import time

from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse
from app.core.ai_engine.router import IntentRouter
from app.core.ai_engine.intent import Intent

from app.core.planner.planner_agent import PlannerAgent
from app.core.registry.capability_loader import load_capabilities
from app.core.orchestrator.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)


class AIOrchestrator:

    def __init__(self):

        self.planner = PlannerAgent()

        self.capability_registry = load_capabilities()

        self.agent_orchestrator = AgentOrchestrator(
            self.capability_registry
        )

    async def process(
        self,
        context: AIContext
    ) -> AIResponse:

        start_time = time.perf_counter()

        try:

            logger.info("========== AI Orchestrator Started ==========")

            # ----------------------------------------
            # Detect Intent
            # ----------------------------------------

            intent = IntentRouter.detect(context.message)
            context.intent = intent

            logger.info(f"Detected Intent: {intent.value}")

            # ----------------------------------------
            # Create Execution Plan
            # ----------------------------------------

            plan = await self.planner.execute(context)

            context.execution_plan = plan

            if not plan.tasks:

                return AIResponse(
                    success=False,
                    message="Planner could not determine any tasks.",
                    intent=intent.value,
                    execution_time=time.perf_counter() - start_time,
                )

            logger.info(
                f"Planner created {len(plan.tasks)} task(s)."
            )

            # ----------------------------------------
            # Execute Plan
            # ----------------------------------------

            execution_result = await self.agent_orchestrator.execute(
                plan,
                context
            )

            # ----------------------------------------
            # Execution Failed
            # ----------------------------------------

            if not execution_result.success:

                return AIResponse(
                    success=False,
                    message=execution_result.message,
                    intent=intent.value,
                    execution_time=time.perf_counter() - start_time,
                )

            # ----------------------------------------
            # No Responses
            # ----------------------------------------

            if not execution_result.responses:

                return AIResponse(
                    success=False,
                    message="No response generated.",
                    intent=intent.value,
                    execution_time=time.perf_counter() - start_time,
                )

            # ----------------------------------------
            # Final Response
            # ----------------------------------------

            response = execution_result.responses[-1]

            response.execution_time = (
                time.perf_counter() - start_time
            )

            logger.info("========== AI Orchestrator Finished ==========")

            return response

        except Exception as e:

            logger.exception("AI Orchestrator Error")

            return AIResponse(
                success=False,
                message=str(e),
                intent=Intent.GENERAL.value,
                execution_time=time.perf_counter() - start_time,
            )