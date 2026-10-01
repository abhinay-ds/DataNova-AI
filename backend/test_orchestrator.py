import asyncio

from app.core.bootstrap import Bootstrap
from app.core.ai_engine.context import AIContext
from app.core.planner.planner_agent import PlannerAgent


async def main():

    bootstrap = Bootstrap()

    planner = PlannerAgent()

    context = AIContext(
        message="Analyze dataset"
    )

    plan = await planner.execute(context)

    print("=" * 60)
    print("Execution Plan")
    print("=" * 60)

    print("Objective:", plan.objective)
    print()

    for task in plan.tasks:
        print(task.capability)

    print()

    result = await bootstrap.agent_orchestrator.execute(
        plan,
        context
    )

    print("=" * 60)
    print("Execution Result")
    print("=" * 60)

    print("Success :", result.success)
    print("Message :", result.message)

    print()
    print("=" * 60)
    print("Responses")
    print("=" * 60)

    for response in result.responses:

        print("Success :", response.success)
        print("Message :", response.message)

        if hasattr(response, "data"):
            print("Data :", response.data)

        print()

    print("=" * 60)
    print("Completed Tasks")
    print("=" * 60)

    for task in result.completed_tasks:
        print("✔", task.capability)

    print()

    print("=" * 60)
    print("Failed Tasks")
    print("=" * 60)

    for task in result.failed_tasks:
        print("✘", task.capability)


asyncio.run(main())