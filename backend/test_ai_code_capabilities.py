import asyncio

from app.core.bootstrap import Bootstrap
from app.core.ai_engine.context import AIContext
from app.core.planner.planner_agent import PlannerAgent


async def run_test(
    bootstrap,
    planner,
    message,
):

    print()
    print("=" * 70)
    print("USER REQUEST")
    print("=" * 70)

    print(message)

    context = AIContext(
        message=message,
        capability_registry=(
            bootstrap.capability_registry
        ),
        tool_registry=(
            bootstrap.tool_registry
        ),
    )

    # ==========================================
    # Generate Plan
    # ==========================================

    plan = await planner.execute(
        context
    )

    print()
    print("GENERATED PLAN")
    print("-" * 70)

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

    # ==========================================
    # Execute
    # ==========================================

    result = await bootstrap.agent_orchestrator.execute(
        plan,
        context
    )

    print()
    print("EXECUTION")
    print("-" * 70)

    print(
        "Success:",
        result.success
    )

    print(
        "Message:",
        result.message
    )

    for task in result.completed_tasks:

        print()
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


async def main():

    bootstrap = Bootstrap()

    planner = PlannerAgent()

    # ==========================================
    # 1. SQL
    # ==========================================

    await run_test(
        bootstrap,
        planner,
        """
Generate SQL to calculate the average salary
for each department from an employees table.
"""
    )

    # ==========================================
    # 2. Explain Code
    # ==========================================

    await run_test(
        bootstrap,
        planner,
        """
Explain this Python code:

numbers = [1, 2, 3, 4, 5]

squares = [
    number ** 2
    for number in numbers
]

print(squares)
"""
    )

    # ==========================================
    # 3. Debug Code
    # ==========================================

    await run_test(
        bootstrap,
        planner,
        """
Debug this Python code:

numbers = [10, 20, 30]

for i in range(len(numbers) + 1):
    print(numbers[i])

The error is:

IndexError: list index out of range
"""
    )

    # ==========================================
    # 4. Optimize Code
    # ==========================================

    await run_test(
        bootstrap,
        planner,
        """
Optimize this Python code:

result = []

for i in range(len(numbers)):
    result.append(numbers[i] * 2)
"""
    )

    # ==========================================
    # 5. Convert Code
    # ==========================================

    await run_test(
        bootstrap,
        planner,
        """
Convert this Python code to JavaScript:

numbers = [1, 2, 3, 4, 5]

total = sum(numbers)

print(total)
"""
    )


if __name__ == "__main__":
    asyncio.run(main())