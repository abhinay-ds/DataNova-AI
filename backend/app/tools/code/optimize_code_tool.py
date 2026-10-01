from __future__ import annotations

import re

from app.tools.base_tool import BaseTool
from app.services.llm_service import LLMService
from app.core.ai_engine.response import AIResponse


class OptimizeCodeTool(BaseTool):

    @property
    def name(self) -> str:
        return "optimize_code"

    def execute(self, **kwargs):

        code = kwargs.get("code")

        if not code:
            raise ValueError(
                "Code is required."
            )

        prompt = f"""
Optimize the following code.

SOURCE CODE:

{code}

IMPORTANT RESPONSE FORMAT:

First provide a short explanation of the improvements.

Then provide the complete optimized code inside
one markdown code block.

Requirements:

1. Preserve the original functionality.
2. Improve performance only when appropriate.
3. Improve readability and maintainability.
4. Do not add unnecessary complexity.
5. Keep the explanation short.
6. Do not claim that the code was executed.
"""

        llm_response = LLMService.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert software engineer. "
                        "Optimize code while preserving its functionality."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
        )

        if not llm_response.success:
            return llm_response

        content = llm_response.data

        if not isinstance(content, str):
            return AIResponse(
                success=True,
                message="Code optimized successfully.",
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
            optimized_code = match.group(1).strip()
        else:
            optimized_code = content.strip()

        explanation = content

        if "```" in explanation:
            explanation = explanation.split("```")[0].strip()

        explanation = re.sub(
            r"^\s*(?:\*\*)?(?:EXPLANATION|Explanation|Optimized Code)(?:\*\*)?\s*:?\s*",
            "",
            explanation,
            flags=re.IGNORECASE,
        ).strip()

        return AIResponse(
            success=True,
            message="Code optimized successfully.",
            data={
                "code": optimized_code,
                "language": "python",
                "explanation": explanation,
            },
        )