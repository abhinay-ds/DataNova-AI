import asyncio

from app.core.bootstrap import Bootstrap
from app.core.ai_engine.context import AIContext
from app.core.planner.planner_agent import PlannerAgent


async def main():

    bootstrap = Bootstrap()

    planner = PlannerAgent()

    context = AIContext(
        message="Analyze my dataset and train a model",
        capability_registry=bootstrap.capability_registry,
    )

    plan = await planner.execute(context)

    print("=" * 60)
    print("AI GENERATED EXECUTION PLAN")
    print("=" * 60)

    print("Objective:", plan.objective)

    print()

    for task in plan.tasks:

        print("Capability:", task.capability)

        print("Action:", task.action)

        print("Priority:", task.priority)

        print("Input:", task.input_data)

        print("-" * 40)


asyncio.run(main())