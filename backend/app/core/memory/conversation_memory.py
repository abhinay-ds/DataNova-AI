from __future__ import annotations

from typing import Any, Optional

from app.core.memory.context import DatasetContext


class ConversationMemory:

    def __init__(self):
        self.context = DatasetContext()

    # =====================================================
    # Dataset
    # =====================================================

    def set_dataset(self, dataset):
        self.context.dataset = dataset

    def get_dataset(self):
        return self.context.dataset

    # =====================================================
    # Model
    # =====================================================

    def set_model(self, model):
        self.context.trained_model = model

    def get_model(self):
        return self.context.trained_model

    # =====================================================
    # Charts
    # =====================================================

    def add_chart(self, chart):
        self.context.charts.append(chart)

    def get_charts(self):
        return self.context.charts

    # =====================================================
    # Conversation
    # =====================================================

    def add_message(
        self,
        role: str,
        content: Any,
        data: Optional[dict[str, Any]] = None,
    ):
        """
        Store a conversation message.

        Examples:

        User message:
        {
            "role": "user",
            "content": "What percentage survived?"
        }

        Assistant message:
        {
            "role": "assistant",
            "content": "38.38% of passengers survived.",
            "data": {
                "type": "percentage",
                "column": "Survived",
                "value": 38.38,
                "condition": 1,
                "count": 342,
                "total": 891
            }
        }
        """

        message = {
            "role": role,
            "content": content,
        }

        # -------------------------------------------------
        # Store structured data separately when supplied
        # -------------------------------------------------

        if data is not None:
            message["data"] = data

        self.context.conversation_history.append(
            message
        )

    # =====================================================
    # Get Conversation History
    # =====================================================

    def get_history(self) -> list[dict[str, Any]]:
        return self.context.conversation_history

    # =====================================================
    # Get Last Message
    # =====================================================

    def get_last_message(
        self,
    ) -> Optional[dict[str, Any]]:

        if not self.context.conversation_history:
            return None

        return self.context.conversation_history[-1]

    # =====================================================
    # Get Last Assistant Message
    # =====================================================

    def get_last_assistant_message(
        self,
    ) -> Optional[dict[str, Any]]:

        for message in reversed(
            self.context.conversation_history
        ):

            if (
                isinstance(message, dict)
                and message.get("role") == "assistant"
            ):
                return message

        return None

    # =====================================================
    # Get Last Assistant Data
    # =====================================================

    def get_last_assistant_data(
        self,
    ) -> Optional[dict[str, Any]]:

        message = self.get_last_assistant_message()

        if message is None:
            return None

        # -------------------------------------------------
        # Normal structure
        #
        # {
        #     "role": "assistant",
        #     "content": "...",
        #     "data": {...}
        # }
        # -------------------------------------------------

        data = message.get("data")

        if isinstance(data, dict):
            return data

        # -------------------------------------------------
        # Structured content structure
        #
        # {
        #     "role": "assistant",
        #     "content": {
        #         "message": "...",
        #         "data": {...}
        #     }
        # }
        # -------------------------------------------------

        content = message.get("content")

        if isinstance(content, dict):

            data = content.get("data")

            if isinstance(data, dict):
                return data

            # Content itself might be the result data
            if content.get("type"):
                return content

        return None

    # =====================================================
    # Add User Message
    # =====================================================

    def add_user_message(
        self,
        content: str,
    ):

        self.add_message(
            role="user",
            content=content,
        )

    # =====================================================
    # Add Assistant Message
    # =====================================================

    def add_assistant_message(
        self,
        content: Any,
        data: Optional[dict[str, Any]] = None,
        agent: str = "",
        intent: str = "",
    ):

        # -------------------------------------------------
        # If structured data exists, keep it available
        # directly under "data".
        # -------------------------------------------------

        message_data = data

        # -------------------------------------------------
        # Store useful metadata inside content only when
        # data is not separately supplied.
        # -------------------------------------------------

        if message_data is not None:

            self.add_message(
                role="assistant",
                content=content,
                data=message_data,
            )

        else:

            self.add_message(
                role="assistant",
                content={
                    "message": content,
                    "agent": agent,
                    "intent": intent,
                },
            )

    # =====================================================
    # Clear
    # =====================================================

    def clear(self):

        self.context = DatasetContext()