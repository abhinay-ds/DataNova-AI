import asyncio
import pandas as pd

from app.core.bootstrap import Bootstrap
from app.core.ai_engine.context import AIContext
from app.core.planner.planner_agent import PlannerAgent


async def main():

    bootstrap = Bootstrap()

    # Dataset is supplied so the AI system knows
    # which dataset/model the request belongs to.

    dataset = pd.DataFrame({

        "Age": [
            21, 25, 30, 35, 40,
            45, 50, 28, 32, 38
        ],

        "Experience": [
            1, 3, 5, 8, 10,
            15, 20, 4, 6, 9
        ],

        "Salary": [
            30000, 35000, 42000, 50000, 58000,
            70000, 85000, 39000, 45000, 54000
        ]
    })

    context = AIContext(

        message=(
            "Predict the salary for "
            "Age 29 and Experience 5."
        ),

        dataset=dataset,

        capability_registry=(
            bootstrap.capability_registry
        ),

        tool_registry=(
            bootstrap.tool_registry
        ),
    )

    # =====================================================
    # Planner
    # =====================================================

    planner = PlannerAgent()

    plan = await planner.execute(
        context
    )

    print("=" * 60)
    print("AI GENERATED PLAN")
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

        print()

    # =====================================================
    # Execute
    # =====================================================

    result = await bootstrap.agent_orchestrator.execute(
        plan,
        context
    )

    print("=" * 60)
    print("PREDICTION RESULT")
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

    for task in result.completed_tasks:

        print(
            "✔",
            task.capability
        )

        print(
            "Output:",
            task.output_data
        )

        print()


asyncio.run(main())