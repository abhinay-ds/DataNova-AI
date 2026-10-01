from __future__ import annotations

import re
from typing import Any

from app.core.ai_engine.response import AIResponse
from app.services.llm_service import LLMService


class CodeGenerationService:
    """
    Generates Python code for DataNova AI.

    Uses the existing Groq-powered LLMService.
    """

    # =========================================================
    # General Code Generation
    # =========================================================

    @staticmethod
    def generate(prompt: str) -> AIResponse:

        if not prompt or not prompt.strip():
            return AIResponse(
                success=False,
                message="Code generation prompt is required.",
                data=None,
            )

        system_prompt = """
You are the Python Code Intelligence engine of DataNova AI.

Generate high-quality, executable Python code based on the
user's request.

IMPORTANT:
Return a short explanation followed by the complete Python
code inside a Python markdown code block.

Rules:
1. Generate Python code unless explicitly asked otherwise.
2. Include necessary imports.
3. Generate practical and correct code.
4. Prefer clear and maintainable code.
5. Never invent dataset columns.
6. If dataset information is supplied, use only available columns.
7. Keep the explanation short.
8. Do not claim that code was executed unless it actually was.
9. Use pandas for tabular data analysis.
10. Use matplotlib for visualizations unless another library
    is explicitly requested.
11. Use the DataFrame named `df` when working with the supplied
    dataset.
12. Do NOT use pd.read_csv() when `df` is already available.
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

        return CodeGenerationService._call_llm(
            messages
        )

    # =========================================================
    # Generate Code From Analysis
    # =========================================================

    @staticmethod
    def generate_from_analysis(
        question: str,
        dataset_columns: list[str],
        task: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
    ) -> AIResponse:

        if not question or not question.strip():
            return AIResponse(
                success=False,
                message="Analysis question is required.",
                data=None,
            )

        task = task or {}
        result = result or {}

        # =====================================================
        # SMART CHART
        # =====================================================
        #
        # Smart-chart code is generated deterministically.
        #
        # DataNova already knows:
        # - grouping column
        # - metric column
        # - aggregation
        # - chart type
        #
        # Therefore we don't need Groq to guess the code.
        #
        # =====================================================

        if task.get("capability") == "smart_chart":

            x = task.get("x")
            y = task.get("y")

            aggregation = task.get(
                "aggregation",
                "mean",
            )

            chart_type = task.get(
                "chart_type",
                "bar_chart",
            )

            # -------------------------------------------------
            # Validate x and y
            # -------------------------------------------------

            if not x or not y:
                return AIResponse(
                    success=False,
                    message=(
                        "Smart chart code generation requires "
                        "both x and y columns."
                    ),
                    data=None,
                )

            # -------------------------------------------------
            # Validate dataset columns
            # -------------------------------------------------

            if dataset_columns:

                if x not in dataset_columns:
                    return AIResponse(
                        success=False,
                        message=f"Column '{x}' is not available.",
                        data=None,
                    )

                if y not in dataset_columns:
                    return AIResponse(
                        success=False,
                        message=f"Column '{y}' is not available.",
                        data=None,
                    )

            # -------------------------------------------------
            # Validate aggregation
            # -------------------------------------------------

            allowed_aggregations = {
                "mean",
                "sum",
                "count",
                "median",
                "min",
                "max",
            }

            aggregation = str(
                aggregation
            ).lower()

            if aggregation not in allowed_aggregations:
                aggregation = "mean"

            # -------------------------------------------------
            # Normalize chart type
            # -------------------------------------------------

            chart_type = str(
                chart_type
            ).lower()

            if chart_type == "bar":
                chart_type = "bar_chart"

            if chart_type == "line":
                chart_type = "line_chart"

            if chart_type not in {
                "bar_chart",
                "line_chart",
            }:
                return AIResponse(
                    success=False,
                    message=(
                        f"Unsupported chart type: "
                        f"{chart_type}"
                    ),
                    data=None,
                )

            # -------------------------------------------------
            # Safe Python variable name
            # -------------------------------------------------

            variable_name = (
                f"{y}_{aggregation}_by_{x}"
            )

            variable_name = re.sub(
                r"[^a-zA-Z0-9_]",
                "_",
                variable_name,
            )

            variable_name = re.sub(
                r"_+",
                "_",
                variable_name,
            ).strip("_").lower()

            # -------------------------------------------------
            # Aggregation expression
            # -------------------------------------------------

            aggregation_expression = (
                f'df.groupby("{x}")["{y}"].{aggregation}()'
            )

            # -------------------------------------------------
            # Chart title
            # -------------------------------------------------

            title = (
                f"{aggregation.capitalize()} "
                f"{y} by {x}"
            )

            # -------------------------------------------------
            # Build Python code
            # -------------------------------------------------

            code_lines = [
                "import matplotlib.pyplot as plt",
                "",
                f"{variable_name} = (",
                f"    {aggregation_expression}",
                "    .sort_index()",
                ")",
                "",
                "plt.figure(figsize=(8, 5))",
            ]

            # -------------------------------------------------
            # Bar chart
            # -------------------------------------------------

            if chart_type == "bar_chart":

                code_lines.extend(
                    [
                        "",
                        "plt.bar(",
                        (
                            f"    {variable_name}"
                            ".index.astype(str),"
                        ),
                        f"    {variable_name}.values",
                        ")",
                    ]
                )

            # -------------------------------------------------
            # Line chart
            # -------------------------------------------------

            elif chart_type == "line_chart":

                code_lines.extend(
                    [
                        "",
                        "plt.plot(",
                        (
                            f"    {variable_name}"
                            ".index.astype(str),"
                        ),
                        f"    {variable_name}.values,",
                        '    marker="o"',
                        ")",
                    ]
                )

            # -------------------------------------------------
            # Labels
            # -------------------------------------------------

            code_lines.extend(
                [
                    "",
                    f'plt.title("{title}")',
                    f'plt.xlabel("{x}")',
                    (
                        f'plt.ylabel('
                        f'"{aggregation.capitalize()} of {y}"'
                        f')'
                    ),
                    "",
                    "plt.tight_layout()",
                    "plt.show()",
                ]
            )

            code = "\n".join(
                code_lines
            )

            # -------------------------------------------------
            # Explanation
            # -------------------------------------------------

            chart_name = (
                "bar"
                if chart_type == "bar_chart"
                else "line"
            )

            explanation = (
                f"This code reproduces the DataNova AI "
                f"analysis by calculating the {aggregation} "
                f"of '{y}' grouped by '{x}' and displaying "
                f"the result as a {chart_name} chart."
            )

            # -------------------------------------------------
            # Response
            # -------------------------------------------------

            return AIResponse(
                success=True,
                message="Python code generated successfully.",
                data={
                    "code": code,
                    "language": "python",
                    "explanation": explanation,
                },
            )

        # =====================================================
        # Other Analysis Types
        # =====================================================

        prompt = f"""
Generate Python code that reproduces this DataNova AI analysis.

User question:
{question}

Available dataset columns:
{dataset_columns}

Analysis task:
{task}

Calculated result:
{result}

IMPORTANT:
- A pandas DataFrame named `df` is already loaded.
- NEVER use pd.read_csv().
- NEVER load the dataset from disk.
- Use only the supplied dataset columns.
- Reproduce the supplied analysis.
- Include required imports.
- Do not invent calculations.
- Do not claim the code was executed.
- Keep the code clear and executable.

Return a short explanation followed by complete Python code
inside a Python markdown code block.
"""

        system_prompt = """
You are the Python Code Intelligence engine of DataNova AI.

Generate reproducible Python code for an analysis already
performed by DataNova AI.

The DataFrame is already loaded as `df`.

NEVER use pd.read_csv() unless the user explicitly asks
for file-loading code.

Never invent dataset columns.
Never change the requested analysis.
Never claim that code was executed.
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

        return CodeGenerationService._call_llm(
            messages
        )

    # =========================================================
    # LLM Call
    # =========================================================

    @staticmethod
    def _call_llm(
        messages: list[dict[str, str]]
    ) -> AIResponse:

        try:

            llm_response = LLMService.chat(
                messages=messages,
                temperature=0.2,
            )

            if not llm_response.success:
                return llm_response

            content = llm_response.data

            # -------------------------------------------------
            # Non-string response
            # -------------------------------------------------

            if not isinstance(
                content,
                str,
            ):

                return AIResponse(
                    success=True,
                    message=(
                        "Python code generated successfully."
                    ),
                    data={
                        "code": str(content),
                        "language": "python",
                        "explanation": "",
                    },
                )

            # -------------------------------------------------
            # Extract Python code block
            # -------------------------------------------------

            match = re.search(
                r"```python\s*(.*?)```",
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

            # -------------------------------------------------
            # Extract explanation
            # -------------------------------------------------

            explanation = content

            if "```" in explanation:

                explanation = (
                    explanation
                    .split("```")[0]
                    .strip()
                )

            # -------------------------------------------------
            # Return
            # -------------------------------------------------

            return AIResponse(
                success=True,
                message=(
                    "Python code generated successfully."
                ),
                data={
                    "code": code,
                    "language": "python",
                    "explanation": explanation,
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
                data=None,
            )