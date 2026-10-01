from __future__ import annotations

from app.tools.base_tool import BaseTool
from app.services.llm_service import LLMService
from app.core.ai_engine.response import AIResponse


class ExplainCodeTool(BaseTool):

    @property
    def name(self) -> str:
        return "explain_code"

    def execute(self, **kwargs):

        code = kwargs.get("code")

        if not code:
            raise ValueError(
                "Code is required."
            )

        messages = [
            {
                "role": "system",
                "content": """
You are a programming instructor.

Explain the supplied code clearly and concisely.

Cover when relevant:

1. Overall purpose
2. Important components
3. Execution flow
4. Important functions or classes
5. Potential issues
6. Complexity

Keep the explanation understandable.

Do not rewrite the complete code unless necessary.
Do not claim that the code was executed.
""",
            },
            {
                "role": "user",
                "content": code,
            },
        ]

        llm_response = LLMService.chat(
            messages=messages,
            temperature=0.2,
        )

        if not llm_response.success:
            return llm_response

        content = llm_response.data

        if not isinstance(content, str):
            content = str(content)

        return AIResponse(
            success=True,
            message="Code explained successfully.",
            data={
                "explanation": content,
            },
        )