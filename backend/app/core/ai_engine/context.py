from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, TYPE_CHECKING

import pandas as pd

from app.core.planner.execution_plan import ExecutionPlan


if TYPE_CHECKING:

    from app.core.memory.memory_manager import MemoryManager
    from app.core.workflow.workflow_engine import WorkflowEngine
    from app.core.registry.capability_registry import CapabilityRegistry
    from app.core.registry.tool_registry import ToolRegistry


def create_memory_manager():
    from app.core.memory.memory_manager import MemoryManager
    return MemoryManager()


@dataclass
class AIContext:

    # =====================================================
    # User Request
    # =====================================================

    message: str

    # =====================================================
    # User Information
    # =====================================================

    user_id: Optional[str] = None

    session_id: Optional[str] = None

    workspace_id: Optional[str] = None

    # =====================================================
    # Dataset
    # =====================================================

    dataset: Optional[pd.DataFrame] = None

    dataset_name: Optional[str] = None

    # =====================================================
    # AI Memory
    # =====================================================

    memory: "MemoryManager" = field(
        default_factory=create_memory_manager
    )

    # =====================================================
    # Runtime Services
    # =====================================================

    tool_registry: Optional["ToolRegistry"] = None

    capability_registry: Optional["CapabilityRegistry"] = None

    workflow_engine: Optional["WorkflowEngine"] = None

    # =====================================================
    # Execution Plan
    # =====================================================

    execution_plan: Optional[ExecutionPlan] = None

    current_task: Any = None

    task_results: dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # Planner Metadata
    # =====================================================

    intent: Optional[str] = None

    capability: Optional[str] = None

    # =====================================================
    # Conversation
    # =====================================================

    conversation_history: list[dict[str, Any]] = field(
        default_factory=list
    )

    # =====================================================
    # Uploaded Files
    # =====================================================

    uploaded_files: list[str] = field(
        default_factory=list
    )

    # =====================================================
    # Extra Metadata
    # =====================================================

    metadata: dict[str, Any] = field(
        default_factory=dict
    )