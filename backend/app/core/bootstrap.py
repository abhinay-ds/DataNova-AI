from app.core.workflow.workflow_engine import WorkflowEngine
from app.core.orchestrator.orchestrator import AgentOrchestrator
from app.core.registry.capability_loader import load_capabilities
from app.core.registry.tool_loader import load_tools
from app.core.ai_engine.engine import AIEngine


class Bootstrap:

    def __init__(self):

        # -----------------------------------------
        # Tool Registry
        # -----------------------------------------

        self.tool_registry = load_tools()

        # -----------------------------------------
        # Capability Registry
        # -----------------------------------------

        self.capability_registry = load_capabilities()

        # -----------------------------------------
        # Orchestrator
        # -----------------------------------------

        self.agent_orchestrator = AgentOrchestrator(
            self.capability_registry
        )

        # -----------------------------------------
        # Workflow Engine
        # -----------------------------------------

        self.workflow_engine = WorkflowEngine()

        # -----------------------------------------
        # AI Engine
        # -----------------------------------------

        self.ai_engine = AIEngine(
            capability_registry=self.capability_registry,
            tool_registry=self.tool_registry
        )