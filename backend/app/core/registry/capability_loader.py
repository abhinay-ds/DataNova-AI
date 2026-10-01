from app.core.registry.capability_registry import CapabilityRegistry

from app.services.agents.analysis_agent import AnalysisAgent
from app.services.agents.ml_agent import MLAgent
from app.services.agents.visualization_agent import VisualizationAgent
from app.services.agents.report_agent import ReportAgent
from app.services.agents.general_agent import GeneralAgent
from app.services.agents.code_agent import CodeAgent
from app.services.agents.data_query_agent import DataQueryAgent
from app.services.agents.data_analysis_agent import DataAnalysisAgent


def load_capabilities() -> CapabilityRegistry:

    registry = CapabilityRegistry()

    # --------------------------------------------------------------
    # Agents
    # --------------------------------------------------------------

    analysis_agent = AnalysisAgent()
    data_analysis_agent = DataAnalysisAgent()
    ml_agent = MLAgent()
    visualization_agent = VisualizationAgent()
    report_agent = ReportAgent()
    general_agent = GeneralAgent()
    code_agent = CodeAgent()
    data_query_agent = DataQueryAgent()

    # --------------------------------------------------------------
    # Dataset Analysis
    # --------------------------------------------------------------

    registry.register(
        "analyze_dataset",
        analysis_agent
    )

    # --------------------------------------------------------------
    # Flexible Data Analysis
    # --------------------------------------------------------------

    registry.register(
        "data_analysis",
        data_analysis_agent
    )

    # --------------------------------------------------------------
    # Data Query
    # --------------------------------------------------------------

    registry.register(
        "data_question",
        data_query_agent
    )

    # --------------------------------------------------------------
    # Machine Learning
    # --------------------------------------------------------------

    registry.register(
        "train_model",
        ml_agent
    )

    registry.register(
        "predict",
        ml_agent
    )

    registry.register(
        "evaluate_model",
        ml_agent
    )

    # --------------------------------------------------------------
    # Visualization
    # --------------------------------------------------------------

    registry.register(
        "histogram",
        visualization_agent
    )

    registry.register(
        "scatter",
        visualization_agent
    )

    registry.register(
        "line_chart",
        visualization_agent
    )

    registry.register(
        "bar_chart",
        visualization_agent
    )

    registry.register(
        "pie_chart",
        visualization_agent
    )

    registry.register(
        "boxplot",
        visualization_agent
    )

    registry.register(
        "correlation",
        visualization_agent
    )

    registry.register(
        "heatmap",
        visualization_agent
    )

    # NEW
    registry.register(
        "smart_chart",
        visualization_agent
    )

    # --------------------------------------------------------------
    # Reports
    # --------------------------------------------------------------

    registry.register(
        "generate_report",
        report_agent
    )

    # --------------------------------------------------------------
    # Code Generation
    # --------------------------------------------------------------

    registry.register(
        "generate_python",
        code_agent
    )

    registry.register(
        "generate_sql",
        code_agent
    )

    registry.register(
        "explain_code",
        code_agent
    )

    registry.register(
        "optimize_code",
        code_agent
    )

    registry.register(
        "convert_code",
        code_agent
    )

    registry.register(
        "debug_code",
        code_agent
    )

    # --------------------------------------------------------------
    # General
    # --------------------------------------------------------------

    registry.register(
        "general",
        general_agent
    )

    return registry