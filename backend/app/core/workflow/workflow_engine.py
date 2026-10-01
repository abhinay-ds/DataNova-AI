from app.core.workflow.workflow_state import WorkflowState


class WorkflowEngine:

    def __init__(self):
        self.state = WorkflowState.CREATED

    async def execute(self, orchestrator, plan, context):

        self.state = WorkflowState.RUNNING

        try:

            results = await orchestrator.execute(
                plan,
                context
            )

            self.state = WorkflowState.COMPLETED

            return results

        except Exception:

            self.state = WorkflowState.FAILED
            raise