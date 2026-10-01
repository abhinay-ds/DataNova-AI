import re

from app.tools.base_tool import BaseTool
from app.services.llm_service import LLMService
from app.core.ai_engine.response import AIResponse


class GenerateSQLTool(BaseTool):

    @property
    def name(self) -> str:
        return "generate_sql"

    def execute(self, **kwargs):

        prompt = kwargs.get("prompt")

        if not prompt:
            raise ValueError(
                "Prompt is required for SQL generation."
            )

        system_prompt = """
You are the SQL generation engine of DataNova AI.

Generate correct and practical SQL based on the user's request.

IMPORTANT:
Return a short explanation followed by the complete SQL query
inside a SQL markdown code block.

Rules:
1. Return valid SQL.
2. Do not invent columns when dataset information is provided.
3. Use only available table and column names when provided.
4. Prefer standard SQL unless a database dialect is specified.
5. Keep the explanation short.
6. Always put the complete SQL query inside one SQL markdown code block.
"""

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        llm_response = LLMService.chat(
            messages=messages,
            temperature=0.1,
        )

        if not llm_response.success:
            return llm_response

        content = llm_response.data

        if not isinstance(content, str):
            return AIResponse(
                success=True,
                message="SQL generated successfully.",
                data={
                    "code": str(content),
                    "language": "sql",
                    "explanation": "",
                },
            )

        match = re.search(
            r"```sql\s*(.*?)```",
            content,
            re.DOTALL | re.IGNORECASE,
        )

        if match:
            code = match.group(1).strip()

        else:
            match = re.search(
                r"```\s*(.*?)```",
                content,
                re.DOTALL,
            )

            if match:
                code = match.group(1).strip()
            else:
                code = content.strip()

        explanation = content

        if "```" in explanation:
            explanation = explanation.split("```")[0].strip()

        return AIResponse(
            success=True,
            message="SQL generated successfully.",
            data={
                "code": code,
                "language": "sql",
                "explanation": explanation,
            },
        )