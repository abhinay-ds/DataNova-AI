from dataclasses import dataclass, field


@dataclass
class ModelMemory:

    trained_models: dict = field(default_factory=dict)

    best_model: object | None = None

    target_column: str | None = None

    metrics: dict = field(default_factory=dict)

    feature_importance: dict = field(default_factory=dict)

    preprocessing_pipeline = None