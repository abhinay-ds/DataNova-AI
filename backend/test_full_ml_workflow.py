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

    # ==========================================
    # Context
    # ==========================================

    context = AIContext(

        message=(
            "Analyze my dataset, train the best "
            "model to predict Salary, and evaluate it."
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
    # Gemini Planner
    # ==========================================

    planner = PlannerAgent()

    plan = await planner.execute(
        context
    )

    print("=" * 60)
    print("GENERATED PLAN")
    print("=" * 60)

    for index, task in enumerate(
        plan.tasks,
        start=1
    ):

        print(
            f"{index}. {task.capability}"
        )

        print(
            f"   Action: {task.action}"
        )

        print(
            f"   Input: {task.input_data}"
        )

        print()

    # ==========================================
    # Execute Plan
    # ==========================================

    result = await bootstrap.agent_orchestrator.execute(
        plan,
        context
    )

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
    # Completed
    # ==========================================

    print("COMPLETED TASKS")
    print("-" * 60)

    for task in result.completed_tasks:

        print(
            "✔",
            task.capability
        )

        print(
            "  Output:",
            task.output_data
        )

        print()

    # ==========================================
    # Failed
    # ==========================================

    print("FAILED TASKS")
    print("-" * 60)

    for task in result.failed_tasks:

        print(
            "✘",
            task.capability
        )

        print(
            "  Error:",
            task.output_data
        )

        print()


asyncio.run(main())