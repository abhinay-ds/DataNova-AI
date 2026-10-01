from __future__ import annotations

import logging
import traceback

from app.core.orchestrator.execution_result import ExecutionResult
from app.core.execution.task_status import TaskStatus


logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Executes tasks produced by the PlannerAgent.

    Responsibilities
    ----------------
    - Execute planned tasks
    - Manage task status
    - Pass previous task results
    - Store task results
    - Store conversation history
    - Track completed and failed tasks
    - Log execution errors
    """

    def __init__(self, capability_registry):
        self.capability_registry = capability_registry

    async def execute(self, plan, context):

        result = ExecutionResult(
            success=True,
            message="Execution completed."
        )

        # =====================================================
        # Memory
        # =====================================================

        memory = getattr(
            context,
            "memory",
            None
        )

        # =====================================================
        # Store Current User Message
        # =====================================================

        if memory is not None:

            try:

                memory.conversation.add_message(
                    role="user",
                    content=context.message,
                )

            except Exception:

                logger.exception(
                    "Failed to store user message in memory."
                )

        # =====================================================
        # Execute Tasks
        # =====================================================

        for task in plan.tasks:

            context.current_task = task

            # =================================================
            # Mark Task Running
            # =================================================

            task.status = TaskStatus.RUNNING

            if memory is not None:

                try:

                    memory.task.add_running(
                        task
                    )

                except Exception:

                    logger.exception(
                        "Failed to add task to running memory."
                    )

            try:

                # =================================================
                # Ensure Input Data
                # =================================================

                if task.input_data is None:

                    task.input_data = {}

                # =================================================
                # Inject Previous Results
                # =================================================

                if context.task_results:

                    task.input_data[
                        "_previous_results"
                    ] = context.task_results.copy()

                # =================================================
                # Get Agent
                # =================================================

                agent = (
                    self.capability_registry.get_agent(
                        task.capability
                    )
                )

                if agent is None:

                    raise ValueError(
                        f"No agent registered for capability "
                        f"'{task.capability}'."
                    )

                # =================================================
                # Execute Agent
                # =================================================

                response = await agent.execute(
                    context
                )

                # =================================================
                # Store Output
                # =================================================

                task.output_data = getattr(
                    response,
                    "data",
                    None
                )

                # =================================================
                # Store Response
                # =================================================

                result.responses.append(
                    response
                )

                result.task_results[
                    task.id
                ] = task.output_data

                # =================================================
                # Store Result By Capability
                # =================================================

                context.task_results[
                    task.capability
                ] = task.output_data

                # =================================================
                # Check Response
                # =================================================

                if response.success:

                    task.status = (
                        TaskStatus.COMPLETED
                    )

                    result.completed_tasks.append(
                        task
                    )

                    # ---------------------------------------------
                    # Memory: Completed Task
                    # ---------------------------------------------

                    if memory is not None:

                        try:

                            memory.task.remove_running(
                                task
                            )

                            memory.task.add_completed(
                                task
                            )

                        except Exception:

                            logger.exception(
                                "Failed to update completed task memory."
                            )

                else:

                    task.status = (
                        TaskStatus.FAILED
                    )

                    result.failed_tasks.append(
                        task
                    )

                    result.success = False

                    # ---------------------------------------------
                    # Memory: Failed Task
                    # ---------------------------------------------

                    if memory is not None:

                        try:

                            memory.task.remove_running(
                                task
                            )

                            memory.task.add_failed(
                                task
                            )

                        except Exception:

                            logger.exception(
                                "Failed to update failed task memory."
                            )

                    # ---------------------------------------------
                    # Log Agent Failure
                    # ---------------------------------------------

                    logger.error(
                        "\n"
                        + "=" * 70
                        + "\n"
                        + "AGENT RETURNED FAILURE"
                        + "\n"
                        + "=" * 70
                        + f"\nTask ID    : {task.id}"
                        + f"\nCapability : {task.capability}"
                        + f"\nAction     : {task.action}"
                        + f"\nInput Data : {task.input_data}"
                        + f"\nMessage    : {getattr(response, 'message', '')}"
                        + "\n"
                        + "=" * 70
                    )

            # =====================================================
            # Exception Handling
            # =====================================================

            except Exception as e:

                task.status = TaskStatus.FAILED

                result.success = False

                result.failed_tasks.append(
                    task
                )

                # =================================================
                # Detailed Error Information
                # =================================================

                error_message = str(e)

                error_data = {
                    "error": error_message,
                    "capability": getattr(
                        task,
                        "capability",
                        "",
                    ),
                    "action": getattr(
                        task,
                        "action",
                        "",
                    ),
                    "input_data": getattr(
                        task,
                        "input_data",
                        {},
                    ),
                }

                task.output_data = error_data

                result.task_results[
                    task.id
                ] = error_data

                context.task_results[
                    task.capability
                ] = error_data

                # =================================================
                # PRINT EXACT ERROR TO TERMINAL
                # =================================================

                print("\n")
                print("=" * 80)
                print("TASK EXECUTION FAILED")
                print("=" * 80)

                print(
                    f"Task ID       : "
                    f"{getattr(task, 'id', '')}"
                )

                print(
                    f"Capability    : "
                    f"{getattr(task, 'capability', '')}"
                )

                print(
                    f"Action        : "
                    f"{getattr(task, 'action', '')}"
                )

                print(
                    f"Input Data    : "
                    f"{getattr(task, 'input_data', {})}"
                )

                print(
                    f"Error         : "
                    f"{error_message}"
                )

                print("-" * 80)
                print("FULL TRACEBACK")
                print("-" * 80)

                traceback.print_exc()

                print("=" * 80)
                print("\n")

                # Also send through logger
                logger.exception(
                    "Task execution failed."
                )

                # =================================================
                # Memory: Failed Task
                # =================================================

                if memory is not None:

                    try:

                        memory.task.remove_running(
                            task
                        )

                        memory.task.add_failed(
                            task
                        )

                    except Exception:

                        logger.exception(
                            "Failed to update failed task memory."
                        )

        # =====================================================
        # Final Message
        # =====================================================

        if result.failed_tasks:

            result.message = (
                f"{len(result.failed_tasks)} "
                f"task(s) failed."
            )

        else:

            result.message = (
                f"Successfully executed "
                f"{len(result.completed_tasks)} "
                f"task(s)."
            )

        # =====================================================
        # Store Assistant Responses
        # =====================================================

        if memory is not None:

            for response in result.responses:

                try:

                    response_content = {

                        "message": getattr(
                            response,
                            "message",
                            "",
                        ),

                        "data": getattr(
                            response,
                            "data",
                            {},
                        ),

                        "agent": getattr(
                            response,
                            "agent",
                            "",
                        ),

                        "intent": getattr(
                            response,
                            "intent",
                            "",
                        ),
                    }

                    memory.conversation.add_message(
                        role="assistant",
                        content=response_content,
                    )

                except Exception:

                    logger.exception(
                        "Failed to store assistant response in memory."
                    )

        return result