import asyncio
import pandas as pd

from app.core.bootstrap import Bootstrap
from app.core.ai_engine.context import AIContext
from app.core.planner.planner_agent import PlannerAgent


async def main():

    bootstrap = Bootstrap()

    # ==========================================
    # Test dataset
    # ==========================================

    dataset = pd.DataFrame({

        "Age": [21, 25, 30, 35, 40],

        "Experience": [1, 3, 5, 8, 10],

        "Salary": [30000, 35000, 42000, 50000, 58000]
    })

    # ==========================================
    # User request
    # ==========================================

    context = AIContext(

        message=(
            "Generate Python code to analyze my dataset "
            "and show missing values, statistics, and "
            "a correlation matrix."
        ),

        dataset=dataset,

        capability_registry=(
            bootstrap.capability_registry
        ),

        tool_registry=(
            bootstrap.tool_registry
        ),
    )

    # ==========================================
    # Planner
    # ==========================================

    planner = PlannerAgent()

    plan = await planner.execute(
        context
    )

    print("=" * 60)
    print("AI GENERATED CODE PLAN")
    print("=" * 60)

    for task in plan.tasks:

        print(
            "Capability:",
            task.capability
        )

        print(
            "Action:",
            task.action
        )

        print(
            "Input:",
            task.input_data
        )

        print("-" * 60)

    # ==========================================
    # Execute
    # ==========================================

    result = await bootstrap.agent_orchestrator.execute(
        plan,
        context
    )

    print()
    print("=" * 60)
    print("EXECUTION RESULT")
    print("=" * 60)

    print(
        "Success:",
        result.success
    )

    print(
        "Message:",
        result.message
    )

    print()

    # ==========================================
    # Results
    # ==========================================

    for task in result.completed_tasks:

        print(
            "✔",
            task.capability
        )

        print(
            "Output:"
        )

        print(
            task.output_data
        )

        print()


if __name__ == "__main__":
    asyncio.run(main())