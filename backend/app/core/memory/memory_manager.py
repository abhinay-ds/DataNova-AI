from app.core.memory.conversation_memory import ConversationMemory
from app.core.memory.dataset_memory import DatasetMemory
from app.core.memory.model_memory import ModelMemory
from app.core.memory.visualization_memory import VisualizationMemory
from app.core.memory.report_memory import ReportMemory
from app.core.memory.task_memory import TaskMemory


class MemoryManager:

    def __init__(self):

        self.conversation = ConversationMemory()

        self.dataset = DatasetMemory()

        self.model = ModelMemory()

        self.visualization = VisualizationMemory()

        self.report = ReportMemory()

        self.task = TaskMemory()

    def clear(self):

        self.conversation.clear()

        self.dataset.clear()

        self.model.clear()

        self.visualization.clear()

        self.report.clear()

        self.task.clear()