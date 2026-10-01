from __future__ import annotations

import re

from app.tools.base_tool import BaseTool
from app.services.llm_service import LLMService
from app.core.ai_engine.response import AIResponse


class DebugCodeTool(BaseTool):

    @property
    def name(self) -> str:
        return "debug_code"

    def execute(self, **kwargs):

        code = kwargs.get("code")

        if not code:
            raise ValueError(
                "Code is required."
            )

        prompt = f"""
Debug the following code.

SOURCE CODE:

{code}

IMPORTANT RESPONSE FORMAT:

First provide a short explanation of the problem
and the fix.

Then provide the complete corrected code inside
one markdown code block.

Requirements:

1. Identify the actual bug or issue.
2. Preserve the intended functionality.
3. Fix the code correctly.
4. Do not add unnecessary complexity.
5. Keep the explanation short.
6. Do not claim that the code was executed.
"""

        llm_response = LLMService.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert software debugger. "
                        "Find bugs and provide correct fixes."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
        )

        if not llm_response.success:
            return llm_response

        content = llm_response.data

        if not isinstance(content, str):
            return AIResponse(
                success=True,
                message="Code debugged successfully.",
                data={
                    "code": str(content),
                    "language": "python",
                    "explanation": "",
                },
            )

        match = re.search(
            r"```(?:[A-Za-z0-9+#._-]+)?\s*(.*?)```",
            content,
            re.DOTALL,
        )

        if match:
            corrected_code = match.group(1).strip()
        else:
            corrected_code = content.strip()

        explanation = content

        if "```" in explanation:
            explanation = explanation.split("```")[0].strip()

        explanation = re.sub(
            r"^\s*(?:\*\*)?(?:EXPLANATION|Explanation|Debugged Code|Corrected Code)(?:\*\*)?\s*:?\s*",
            "",
            explanation,
            flags=re.IGNORECASE,
        ).strip()

        return AIResponse(
            success=True,
            message="Code debugged successfully.",
            data={
                "code": corrected_code,
                "language": "python",
                "explanation": explanation,
            },
        )