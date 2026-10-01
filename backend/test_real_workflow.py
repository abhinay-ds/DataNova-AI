import asyncio

import pandas as pd

from app.core.bootstrap import Bootstrap
from app.core.ai_engine.context import AIContext


async def main():

    # =====================================================
    # Bootstrap
    # =====================================================

    bootstrap = Bootstrap()

    # =====================================================
    # Create test dataset
    # =====================================================

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

    # =====================================================
    # Context
    # =====================================================

    context = AIContext(

        message=(
            "Analyze my dataset and tell me "
            "the relationship between experience "
            "and salary."
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
    # AI Engine
    # =====================================================

    result = await bootstrap.ai_engine.execute(
        context
    )

    # =====================================================
    # Print result
    # =====================================================

    print("=" * 60)
    print("DATANOVA AI REAL WORKFLOW")
    print("=" * 60)

    print()

    print(
        "Success:",
        result.success
    )

    print(
        "Message:",
        result.message
    )

    print()

    print("Responses")
    print("-" * 60)

    for response in result.responses:

        print(
            "Success:",
            response.success
        )

        print(
            "Agent:",
            response.agent
        )

        print(
            "Message:",
            response.message
        )

        print()

    print("Completed Tasks")
    print("-" * 60)

    for task in result.completed_tasks:

        print(
            "✔",
            task.capability
        )

    print()

    print("Failed Tasks")
    print("-" * 60)

    for task in result.failed_tasks:

        print(
            "✘",
            task.capability
        )


asyncio.run(main())