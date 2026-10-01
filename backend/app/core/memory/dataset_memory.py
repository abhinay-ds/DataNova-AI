from __future__ import annotations

from typing import Any, Optional

import pandas as pd


class DatasetMemory:

    def __init__(self):
        self.dataset: Optional[pd.DataFrame] = None
        self.cleaned_dataset: Optional[pd.DataFrame] = None

        self.profile: dict[str, Any] = {}
        self.quality: dict[str, Any] = {}
        self.recommendations: dict[str, Any] = {}
        self.insights: dict[str, Any] = {}

    # =====================================================
    # Dataset
    # =====================================================

    def set_dataset(self, dataset: Optional[pd.DataFrame]):
        self.dataset = dataset

    def get_dataset(self) -> Optional[pd.DataFrame]:
        return self.dataset

    # =====================================================
    # Cleaned Dataset
    # =====================================================

    def set_cleaned_dataset(
        self,
        dataset: Optional[pd.DataFrame],
    ):
        self.cleaned_dataset = dataset

    def get_cleaned_dataset(self) -> Optional[pd.DataFrame]:
        return self.cleaned_dataset

    # =====================================================
    # Profile
    # =====================================================

    def set_profile(self, profile: dict[str, Any]):
        self.profile = profile

    def get_profile(self) -> dict[str, Any]:
        return self.profile

    # =====================================================
    # Quality
    # =====================================================

    def set_quality(self, quality: dict[str, Any]):
        self.quality = quality

    def get_quality(self) -> dict[str, Any]:
        return self.quality

    # =====================================================
    # Recommendations
    # =====================================================

    def set_recommendations(
        self,
        recommendations: dict[str, Any],
    ):
        self.recommendations = recommendations

    def get_recommendations(self) -> dict[str, Any]:
        return self.recommendations

    # =====================================================
    # Insights
    # =====================================================

    def set_insights(self, insights: dict[str, Any]):
        self.insights = insights

    def get_insights(self) -> dict[str, Any]:
        return self.insights

    # =====================================================
    # Clear
    # =====================================================

    def clear(self):

        self.dataset = None
        self.cleaned_dataset = None

        self.profile.clear()
        self.quality.clear()
        self.recommendations.clear()
        self.insights.clear()