class DashboardService:

    @classmethod
    def build(cls, memory):

        return {
            "profile": memory.profile,
            "quality": memory.quality,
            "recommendations": memory.recommendations,
            "insights": memory.insights,
            "charts": memory.charts,
            "model": memory.trained_model,
        }