from dataclasses import dataclass, field

import pandas as pd


@dataclass
class DatasetContext:

    # =====================================================
    # Dataset
    # =====================================================

    dataset: pd.DataFrame | None = None

    cleaned_dataset: pd.DataFrame | None = None

    # =====================================================
    # Machine Learning
    # =====================================================

    trained_model = None

    # =====================================================
    # Analysis
    # =====================================================

    profile: dict = field(
        default_factory=dict
    )

    quality: dict = field(
        default_factory=dict
    )

    recommendations: dict = field(
        default_factory=dict
    )

    insights: dict = field(
        default_factory=dict
    )

    report: dict = field(
        default_factory=dict
    )

    # =====================================================
    # Visualization
    # =====================================================

    charts: list = field(
        default_factory=list
    )

    # =====================================================
    # Conversation
    # =====================================================

    conversation_history: list[dict] = field(
        default_factory=list
    )