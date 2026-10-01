from app.core.ai_engine.agent_result import AgentResult


class ResultAggregator:

    @staticmethod
    def aggregate(results: list[AgentResult]):

        final = {
            "analysis": None,
            "visualizations": [],
            "ml": None,
            "report": None,
            "code": None,
            "general": None,
        }

        for result in results:

            if not result.success:
                continue

            agent = result.agent.lower()

            if "analysis" in agent:

                final["analysis"] = result.data

            elif "visualization" in agent:

                final["visualizations"].append(
                    result.data
                )

            elif "ml" in agent:

                final["ml"] = result.data

            elif "report" in agent:

                final["report"] = result.data

            elif "code" in agent:

                final["code"] = result.data

            else:

                final["general"] = result.data

        return final