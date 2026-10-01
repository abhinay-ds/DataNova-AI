import asyncio

from app.core.ai_engine.context import AIContext
from app.core.planner.planner_agent import PlannerAgent


async def main():

    context = AIContext(
        message="Train a machine learning model"
    )

    planner = PlannerAgent()

    plan = await planner.execute(context)

    print("=" * 50)
    print("Execution Plan")
    print("=" * 50)

    print("Objective:", plan.objective)

    print()

    for task in plan.tasks:

        print("------------------------")
        print("Capability :", task.capability)
        print("Action     :", task.action)
        print("Priority   :", task.priority)
        print("Status     :", task.status)
        print("Input      :", task.input_data)


asyncio.run(main())