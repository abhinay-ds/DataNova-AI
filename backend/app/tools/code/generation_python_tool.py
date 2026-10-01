from __future__ import annotations

from typing import Any

from app.tools.base_tool import BaseTool
from app.services.code_generation_service import (
    CodeGenerationService,
)


class GeneratePythonTool(BaseTool):

    @property
    def name(self) -> str:
        return "generate_python"

    # =========================================================
    # Execute
    # =========================================================

    def execute(self, **kwargs) -> Any:

        prompt = kwargs.get("prompt")

        if not prompt:
            raise ValueError(
                "Prompt is required for Python code generation."
            )

        # =====================================================
        # Dataset Context
        # =====================================================

        dataset_name = kwargs.get(
            "dataset_name",
            "uploaded_dataset",
        )

        dataset_columns = kwargs.get(
            "dataset_columns",
            [],
        )

        dataset_shape = kwargs.get(
            "dataset_shape",
            {},
        )

        dataset_dtypes = kwargs.get(
            "dataset_dtypes",
            {},
        )

        # =====================================================
        # Analysis Context
        # =====================================================

        analysis_task = kwargs.get(
            "analysis_task"
        )

        analysis_result = kwargs.get(
            "analysis_result"
        )

        # =====================================================
        # If actual analysis information exists,
        # generate reproducible code from it.
        # =====================================================

        if (
            analysis_task
            and isinstance(
                analysis_task,
                dict,
            )
        ):

            return CodeGenerationService.generate_from_analysis(
                question=prompt,
                dataset_columns=[
                    str(column)
                    for column in dataset_columns
                ],
                task=analysis_task,
                result=(
                    analysis_result
                    if isinstance(
                        analysis_result,
                        dict,
                    )
                    else {}
                ),
            )

        # =====================================================
        # Build Enhanced Prompt
        # =====================================================

        enhanced_prompt = f"""
User request:
{prompt}

Dataset information:

Dataset name:
{dataset_name}

Available columns:
{dataset_columns}

Dataset shape:
{dataset_shape}

Column data types:
{dataset_dtypes}

Important instructions:

- If generating code for this dataset, use ONLY the
  available columns listed above.
- Do NOT invent dataset columns.
- Assume the dataset is already available as a pandas
  DataFrame named `df`.
- Do NOT use pd.read_csv() unless the user explicitly
  asks for file-loading code.
- Use pandas for data analysis.
- Use matplotlib for visualizations when appropriate.
- Generate executable Python code.
"""

        # =====================================================
        # Normal Code Generation
        # =====================================================

        return CodeGenerationService.generate(
            prompt=enhanced_prompt
        )