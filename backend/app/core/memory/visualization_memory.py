from dataclasses import dataclass, field


@dataclass
class VisualizationMemory:

    last_chart = None

    chart_history: list = field(default_factory=list)

    generated_files: list = field(default_factory=list)