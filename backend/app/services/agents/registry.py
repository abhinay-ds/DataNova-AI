from app.core.ai_engine.intent import Intent

from app.services.agents.profile_agent import ProfileAgent
from app.services.agents.analysis_agent import AnalysisAgent
from app.services.agents.visualization_agent import VisualizationAgent
from app.services.agents.ml_agent import MLAgent
from app.services.agents.sql_agent import SQLAgent
from app.services.agents.code_agent import CodeAgent
from app.services.agents.report_agent import ReportAgent
from app.services.agents.general_agent import GeneralAgent
from app.services.agents.ml_agent import MLAgent

class AgentRegistry:
    """
    Registry responsible for managing AI agents.
    """

    def __init__(self):

        self._agents = {
            Intent.PROFILE: ProfileAgent(),
            Intent.ANALYSIS: AnalysisAgent(),
            Intent.VISUALIZATION: VisualizationAgent(),
            Intent.ML: MLAgent(),
            Intent.SQL: SQLAgent(),
            Intent.CODE: CodeAgent(),
            Intent.REPORT: ReportAgent(),
            Intent.GENERAL: GeneralAgent(),
        }

    def get_agent(self, intent: Intent):
        """
        Return the agent for a given intent.
        """
        return self._agents.get(intent)

    def register(self, intent: Intent, agent):
        """
        Register a new agent.
        """
        self._agents[intent] = agent

    def unregister(self, intent: Intent):
        """
        Remove an agent.
        """
        self._agents.pop(intent, None)

    def list_agents(self):
        """
        Return all registered intents.
        """
        return list(self._agents.keys())