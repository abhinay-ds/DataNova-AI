from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskMemory:

    completed: list[Any] = field(
        default_factory=list
    )

    running: list[Any] = field(
        default_factory=list
    )

    failed: list[Any] = field(
        default_factory=list
    )

    # =====================================================
    # Completed Tasks
    # =====================================================

    def add_completed(self, task):
        self.completed.append(task)

    # =====================================================
    # Running Tasks
    # =====================================================

    def add_running(self, task):
        self.running.append(task)

    # =====================================================
    # Failed Tasks
    # =====================================================

    def add_failed(self, task):
        self.failed.append(task)

    # =====================================================
    # Remove Running Task
    # =====================================================

    def remove_running(self, task):

        if task in self.running:
            self.running.remove(task)

    # =====================================================
    # Clear
    # =====================================================

    def clear(self):

        self.completed.clear()
        self.running.clear()
        self.failed.clear()