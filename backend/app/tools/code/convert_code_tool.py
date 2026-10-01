from __future__ import annotations

import re

from app.tools.base_tool import BaseTool
from app.services.llm_service import LLMService
from app.core.ai_engine.response import AIResponse


class ConvertCodeTool(BaseTool):

    @property
    def name(self) -> str:
        return "convert_code"

    def execute(self, **kwargs):

        code = kwargs.get("code")

        target_language = kwargs.get("target_language")

        if not code:
            raise ValueError(
                "Code is required."
            )

        if not target_language:
            raise ValueError(
                "Target language is required."
            )

        prompt = f"""
Convert the following code to {target_language}.

SOURCE CODE:

{code}

IMPORTANT RESPONSE FORMAT:

First provide a short explanation.

Then provide the complete converted code inside
one markdown code block.

Requirements:

1. Preserve the original functionality.
2. Use idiomatic {target_language}.
3. Include necessary imports if required.
4. Keep the explanation short.
5. Do not claim that the converted code was executed.
6. Do not add unnecessary functionality.
"""

        llm_response = LLMService.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert multi-language programmer. "
                        "Convert code accurately and clearly."
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
                message="Code converted successfully.",
                data={
                    "code": str(content),
                    "language": target_language.lower(),
                    "explanation": "",
                },
            )

        match = re.search(
            r"```(?:[A-Za-z0-9+#._-]+)?\s*(.*?)```",
            content,
            re.DOTALL,
        )

        if match:
            converted_code = match.group(1).strip()
        else:
            converted_code = content.strip()

        explanation = content

        if "```" in explanation:
            explanation = explanation.split("```")[0].strip()

        explanation = re.sub(
            r"^\s*(?:\*\*)?(?:EXPLANATION|Explanation|Converted Code)(?:\*\*)?\s*:?\s*",
            "",
            explanation,
            flags=re.IGNORECASE,
        ).strip()

        return AIResponse(
            success=True,
            message="Code converted successfully.",
            data={
                "code": converted_code,
                "language": target_language.lower(),
                "explanation": explanation,
            },
        )