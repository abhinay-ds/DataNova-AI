from app.core.registry.tool_registry import ToolRegistry

# ==========================================
# Analysis Tools
# ==========================================

from app.tools.analysis.analyze_dataset_tool import AnalyzeDatasetTool
from app.tools.analysis.dataset_profile_tool import DatasetProfileTool
from app.tools.analysis.quality_score_tool import QualityScoreTool
from app.tools.analysis.insight_tool import InsightTool
from app.tools.analysis.recommendation_tool import RecommendationTool
from app.tools.visualization.smart_chart_tool import SmartChartTool


# ==========================================
# Machine Learning Tools
# ==========================================

from app.tools.ml.train_model_tool import TrainModelTool
from app.tools.ml.predict_tool import PredictTool
from app.tools.ml.evaluate_tool import EvaluateTool


# ==========================================
# Visualization Tools
# ==========================================
from app.tools.visualization.histogram_tool import HistogramTool
from app.tools.visualization.scatter_tool import ScatterTool
from app.tools.visualization.line_chart_tool import LineChartTool
from app.tools.visualization.bar_chart_tool import BarChartTool
from app.tools.visualization.pie_chart_tool import PieChartTool
from app.tools.visualization.boxplot_tool import BoxPlotTool
from app.tools.visualization.correlation_tool import CorrelationTool
from app.tools.visualization.heatmap_tool import HeatmapTool
from app.tools.visualization.smart_chart_tool import SmartChartTool


# ==========================================
# Report Tools
# ==========================================

from app.tools.report.generate_report_tool import GenerateReportTool


# ==========================================
# Code Intelligence Tools
# ==========================================

from app.tools.code.generation_python_tool import GeneratePythonTool
from app.tools.code.generate_sql_tool import GenerateSQLTool
from app.tools.code.explain_code_tool import ExplainCodeTool
from app.tools.code.optimize_code_tool import OptimizeCodeTool
from app.tools.code.convert_code_tool import ConvertCodeTool
from app.tools.code.debug_code_tool import DebugCodeTool


def load_tools() -> ToolRegistry:

    """
    Register all tools available in DataNova AI.
    """

    registry = ToolRegistry()

    # ======================================
    # Analysis
    # ======================================

    registry.register(
        "analyze_dataset",
        AnalyzeDatasetTool()
    )

    registry.register(
        "profile_dataset",
        DatasetProfileTool()
    )

    registry.register(
        "quality_score",
        QualityScoreTool()
    )

    registry.register(
        "insight",
        InsightTool()
    )

    registry.register(
        "recommendation",
        RecommendationTool()
    )

    # ======================================
    # Machine Learning
    # ======================================

    registry.register(
        "train_model",
        TrainModelTool()
    )

    registry.register(
        "predict",
        PredictTool()
    )

    registry.register(
        "evaluate_model",
        EvaluateTool()
    )

    # ======================================
    # Visualization
    # ======================================

    registry.register(
        "histogram",
        HistogramTool()
    )

    registry.register(
        "scatter",
        ScatterTool()
    )

    registry.register(
        "line_chart",
        LineChartTool()
    )

    registry.register(
        "bar_chart",
        BarChartTool()
    )

    registry.register(
        "pie_chart",
        PieChartTool()
    )

    registry.register(
        "boxplot",
        BoxPlotTool()
    )

    registry.register(
        "correlation",
        CorrelationTool()
    )

    registry.register(
        "heatmap",
        HeatmapTool()
    )
    
    registry.register(
        "smart_chart",
        SmartChartTool()
    )

    # ======================================
    # Code Intelligence
    # ======================================

    registry.register(
        "generate_python",
        GeneratePythonTool()
    )

    registry.register(
        "generate_sql",
        GenerateSQLTool()
    )

    registry.register(
        "explain_code",
        ExplainCodeTool()
    )

    registry.register(
        "optimize_code",
        OptimizeCodeTool()
    )

    registry.register(
        "convert_code",
        ConvertCodeTool()
    )

    registry.register(
        "debug_code",
        DebugCodeTool()
    )

    # ======================================
    # Reports
    # ======================================

    registry.register(
        "generate_report",
        GenerateReportTool()
    )

    return registry