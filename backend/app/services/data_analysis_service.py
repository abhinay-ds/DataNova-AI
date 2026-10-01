from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from app.core.ai_engine.response import AIResponse
from app.services.llm_service import LLMService


class DataAnalysisService:
    """
    Flexible dataset analysis service.

    The DataFrame is analyzed locally first.
    The LLM is then used to interpret the calculated
    statistics and produce a natural-language answer.
    """

    # ==============================================================
    # PUBLIC METHOD
    # ==============================================================

    @classmethod
    def answer(
        cls,
        dataset: pd.DataFrame,
        question: str,
        conversation_history: Optional[
            list[dict[str, Any]]
        ] = None,
    ) -> AIResponse:

        # ----------------------------------------------------------
        # Validate dataset
        # ----------------------------------------------------------

        if not isinstance(dataset, pd.DataFrame):

            return AIResponse(
                success=False,
                message="No valid dataset is available.",
                data=None,
                agent="DataAnalysisAgent",
                intent="data_analysis",
            )

        if dataset.empty:

            return AIResponse(
                success=False,
                message="The dataset is empty.",
                data=None,
                agent="DataAnalysisAgent",
                intent="data_analysis",
            )

        # ----------------------------------------------------------
        # Validate question
        # ----------------------------------------------------------

        question = (question or "").strip()

        if not question:

            return AIResponse(
                success=False,
                message="Please ask a question about your dataset.",
                data=None,
                agent="DataAnalysisAgent",
                intent="data_analysis",
            )

        # ----------------------------------------------------------
        # Calculate actual statistics
        # ----------------------------------------------------------

        analysis = cls._analyze_question(
            dataset=dataset,
            question=question,
        )

        # ----------------------------------------------------------
        # Dataset overview
        # ----------------------------------------------------------

        dataset_context = cls._build_dataset_context(
            dataset
        )

        # ----------------------------------------------------------
        # Conversation context
        # ----------------------------------------------------------

        conversation_context = (
            cls._build_conversation_context(
                conversation_history
            )
        )

        # ----------------------------------------------------------
        # Build prompt
        # ----------------------------------------------------------

        prompt = cls._build_prompt(
            question=question,
            dataset_context=dataset_context,
            analysis=analysis,
            conversation_context=conversation_context,
        )

        # ----------------------------------------------------------
        # Ask LLM to interpret calculated results
        # ----------------------------------------------------------

        response = LLMService.generate(
            prompt=prompt,
            temperature=0.2,
        )

        if not response.success:

            return AIResponse(
                success=False,
                message=(
                    "I couldn't analyze the dataset right now: "
                    f"{response.message}"
                ),
                data=None,
                agent="DataAnalysisAgent",
                intent="data_analysis",
            )

        answer = str(
            response.data or ""
        ).strip()

        if not answer:

            return AIResponse(
                success=False,
                message="The analysis service returned an empty response.",
                data=None,
                agent="DataAnalysisAgent",
                intent="data_analysis",
            )

        return AIResponse(
            success=True,
            message=answer,
            data={
                "type": "data_analysis",
                "question": question,
                "answer": answer,
                "analysis": analysis,
            },
            agent="DataAnalysisAgent",
            intent="data_analysis",
        )

    # ==============================================================
    # QUESTION ANALYSIS
    # ==============================================================

    @classmethod
    def _analyze_question(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> dict[str, Any]:

        q = question.lower()

        result: dict[str, Any] = {
            "dataset_shape": {
                "rows": len(dataset),
                "columns": len(dataset.columns),
            },
            "question_type": "general",
        }

        # ----------------------------------------------------------
        # Find mentioned columns
        # ----------------------------------------------------------

        mentioned_columns = []

        for column in dataset.columns:

            column_text = str(
                column
            ).lower()

            if column_text in q:

                mentioned_columns.append(
                    column
                )

        result["mentioned_columns"] = [
            str(column)
            for column in mentioned_columns
        ]

        # ----------------------------------------------------------
        # Detect relationship/comparison questions
        # ----------------------------------------------------------

        relationship_words = [
            "relationship",
            "relation",
            "correlation",
            "affect",
            "impact",
            "difference",
            "compare",
            "comparison",
            "between",
            "versus",
            "vs",
            "varied",
            "variation",
            "performed better",
            "did better",
            "higher",
            "lower",
        ]

        is_relationship = any(
            word in q
            for word in relationship_words
        )

        # ----------------------------------------------------------
        # Survival analysis
        # ----------------------------------------------------------

        survival_column = cls._find_column(
            dataset,
            [
                "survived",
                "survival",
            ],
        )

        if survival_column is not None:

            # Age vs Survival
            age_column = cls._find_column(
                dataset,
                [
                    "age",
                ],
            )

            if (
                age_column is not None
                and (
                    "age" in q
                    or (
                        is_relationship
                        and "survival" in q
                    )
                )
            ):

                result["question_type"] = (
                    "numerical_vs_target"
                )

                result["age_survival"] = (
                    cls._analyze_numeric_vs_binary(
                        dataset=dataset,
                        numeric_column=age_column,
                        target_column=survival_column,
                    )
                )

            # Sex vs Survival
            sex_column = cls._find_column(
                dataset,
                [
                    "sex",
                    "gender",
                ],
            )

            if (
                sex_column is not None
                and (
                    "sex" in q
                    or "gender" in q
                    or (
                        "male" in q
                        or "female" in q
                    )
                )
            ):

                result["question_type"] = (
                    "categorical_vs_target"
                )

                result["sex_survival"] = (
                    cls._analyze_categorical_vs_binary(
                        dataset=dataset,
                        categorical_column=sex_column,
                        target_column=survival_column,
                    )
                )

            # Pclass vs Survival
            pclass_column = cls._find_column(
                dataset,
                [
                    "pclass",
                    "passengerclass",
                    "passenger_class",
                    "class",
                ],
            )

            if (
                pclass_column is not None
                and (
                    "class" in q
                    or "pclass" in q
                )
            ):

                result["question_type"] = (
                    "categorical_vs_target"
                )

                result["class_survival"] = (
                    cls._analyze_categorical_vs_binary(
                        dataset=dataset,
                        categorical_column=pclass_column,
                        target_column=survival_column,
                    )
                )

        # ----------------------------------------------------------
        # Generic numerical correlations
        # ----------------------------------------------------------

        if (
            is_relationship
            and len(mentioned_columns) >= 2
        ):

            numeric_columns = []

            for column in mentioned_columns:

                if pd.api.types.is_numeric_dtype(
                    dataset[column]
                ):

                    numeric_columns.append(
                        column
                    )

            if len(numeric_columns) >= 2:

                result["question_type"] = (
                    "correlation"
                )

                correlations = {}

                for i in range(
                    len(numeric_columns)
                ):

                    for j in range(
                        i + 1,
                        len(numeric_columns),
                    ):

                        col1 = numeric_columns[i]
                        col2 = numeric_columns[j]

                        pair = (
                            dataset[
                                [col1, col2]
                            ]
                            .apply(
                                pd.to_numeric,
                                errors="coerce",
                            )
                            .dropna()
                        )

                        if len(pair) < 2:
                            continue

                        correlation = pair[
                            col1
                        ].corr(
                            pair[col2]
                        )

                        if pd.notna(
                            correlation
                        ):

                            correlations[
                                f"{col1} vs {col2}"
                            ] = round(
                                float(correlation),
                                4,
                            )

                result["correlations"] = (
                    correlations
                )

        # ----------------------------------------------------------
        # General correlations if asked
        # ----------------------------------------------------------

        if (
            "correlation" in q
            or "correlations" in q
        ):

            result["correlation_matrix"] = (
                cls._correlation_matrix(
                    dataset
                )
            )

        # ----------------------------------------------------------
        # General pattern analysis
        # ----------------------------------------------------------

        pattern_words = [
            "pattern",
            "patterns",
            "insight",
            "insights",
            "trend",
            "trends",
            "overall",
            "important",
            "interesting",
        ]

        if any(
            word in q
            for word in pattern_words
        ):

            result["question_type"] = (
                "pattern_analysis"
            )

            result["patterns"] = (
                cls._find_patterns(dataset)
            )

        # ----------------------------------------------------------
        # Missing-data analysis
        # ----------------------------------------------------------

        if (
            "missing" in q
            or "null" in q
            or "empty" in q
        ):

            result["question_type"] = (
                "missing_data"
            )

            result["missing_values"] = (
                cls._missing_analysis(dataset)
            )

        return result

    # ==============================================================
    # FIND COLUMN
    # ==============================================================

    @staticmethod
    def _find_column(
        dataset: pd.DataFrame,
        names: list[str],
    ):

        normalized = {}

        for column in dataset.columns:

            key = (
                str(column)
                .lower()
                .replace("_", "")
                .replace(" ", "")
            )

            normalized[key] = column

        for name in names:

            key = (
                name.lower()
                .replace("_", "")
                .replace(" ", "")
            )

            if key in normalized:

                return normalized[key]

        return None

    # ==============================================================
    # NUMERICAL VS BINARY TARGET
    # ==============================================================

    @classmethod
    def _analyze_numeric_vs_binary(
        cls,
        dataset: pd.DataFrame,
        numeric_column,
        target_column,
    ) -> dict[str, Any]:

        temp = dataset[
            [
                numeric_column,
                target_column,
            ]
        ].copy()

        temp[numeric_column] = pd.to_numeric(
            temp[numeric_column],
            errors="coerce",
        )

        temp[target_column] = pd.to_numeric(
            temp[target_column],
            errors="coerce",
        )

        temp = temp.dropna()

        result = {
            "numeric_column": str(
                numeric_column
            ),
            "target_column": str(
                target_column
            ),
            "groups": {},
        }

        for value in sorted(
            temp[target_column].unique()
        ):

            group = temp[
                temp[target_column] == value
            ][numeric_column]

            if group.empty:
                continue

            result["groups"][str(value)] = {
                "count": int(len(group)),
                "mean": round(
                    float(group.mean()),
                    2,
                ),
                "median": round(
                    float(group.median()),
                    2,
                ),
                "min": round(
                    float(group.min()),
                    2,
                ),
                "max": round(
                    float(group.max()),
                    2,
                ),
            }

        # Correlation
        if len(temp) >= 2:

            correlation = temp[
                numeric_column
            ].corr(
                temp[target_column]
            )

            if pd.notna(correlation):

                result["correlation"] = round(
                    float(correlation),
                    4,
                )

        return result

    # ==============================================================
    # CATEGORICAL VS BINARY TARGET
    # ==============================================================

    @classmethod
    def _analyze_categorical_vs_binary(
        cls,
        dataset: pd.DataFrame,
        categorical_column,
        target_column,
    ) -> dict[str, Any]:

        temp = dataset[
            [
                categorical_column,
                target_column,
            ]
        ].copy()

        temp[target_column] = pd.to_numeric(
            temp[target_column],
            errors="coerce",
        )

        temp = temp.dropna(
            subset=[
                categorical_column,
                target_column,
            ]
        )

        groups = {}

        for value, group in temp.groupby(
            categorical_column,
            dropna=False,
        ):

            total = len(group)

            survived = int(
                (
                    group[target_column] == 1
                ).sum()
            )

            not_survived = int(
                (
                    group[target_column] == 0
                ).sum()
            )

            survival_rate = (
                survived / total * 100
                if total
                else 0
            )

            groups[str(value)] = {
                "total": int(total),
                "survived": survived,
                "not_survived": not_survived,
                "survival_rate": round(
                    survival_rate,
                    2,
                ),
            }

        return {
            "categorical_column": str(
                categorical_column
            ),
            "target_column": str(
                target_column
            ),
            "groups": groups,
        }

    # ==============================================================
    # CORRELATION MATRIX
    # ==============================================================

    @staticmethod
    def _correlation_matrix(
        dataset: pd.DataFrame,
    ) -> dict[str, Any]:

        numeric = dataset.select_dtypes(
            include="number"
        )

        if numeric.empty:

            return {}

        matrix = numeric.corr()

        result = {}

        for column in matrix.columns:

            result[str(column)] = {}

            for other in matrix.columns:

                value = matrix.loc[
                    column,
                    other,
                ]

                if pd.notna(value):

                    result[str(column)][
                        str(other)
                    ] = round(
                        float(value),
                        4,
                    )

        return result

    # ==============================================================
    # PATTERNS
    # ==============================================================

    @classmethod
    def _find_patterns(
        cls,
        dataset: pd.DataFrame,
    ) -> dict[str, Any]:

        result = {}

        # Numeric columns
        numeric = dataset.select_dtypes(
            include="number"
        )

        numeric_summary = {}

        for column in numeric.columns:

            series = pd.to_numeric(
                numeric[column],
                errors="coerce",
            ).dropna()

            if series.empty:
                continue

            numeric_summary[str(column)] = {
                "mean": round(
                    float(series.mean()),
                    2,
                ),
                "median": round(
                    float(series.median()),
                    2,
                ),
                "min": round(
                    float(series.min()),
                    2,
                ),
                "max": round(
                    float(series.max()),
                    2,
                ),
            }

        result["numeric_summary"] = (
            numeric_summary
        )

        # Categorical columns
        categorical_summary = {}

        categorical = dataset.select_dtypes(
            include=[
                "object",
                "category",
                "bool",
            ]
        )

        for column in categorical.columns:

            counts = (
                categorical[column]
                .value_counts(
                    dropna=False
                )
                .head(10)
            )

            categorical_summary[
                str(column)
            ] = {
                str(key): int(value)
                for key, value
                in counts.items()
            }

        result["categorical_summary"] = (
            categorical_summary
        )

        # Missing
        result["missing_values"] = {
            str(column): int(count)
            for column, count
            in dataset.isna().sum().items()
            if count > 0
        }

        return result

    # ==============================================================
    # MISSING DATA
    # ==============================================================

    @staticmethod
    def _missing_analysis(
        dataset: pd.DataFrame,
    ) -> dict[str, Any]:

        rows = len(dataset)

        result = {}

        for column, count in (
            dataset.isna().sum().items()
        ):

            if count > 0:

                result[str(column)] = {
                    "count": int(count),
                    "percentage": round(
                        float(
                            count / rows * 100
                        ),
                        2,
                    ),
                }

        return result

    # ==============================================================
    # DATASET CONTEXT
    # ==============================================================

    @staticmethod
    def _build_dataset_context(
        dataset: pd.DataFrame,
    ) -> str:

        lines = []

        lines.append(
            f"Rows: {len(dataset)}"
        )

        lines.append(
            f"Columns: {len(dataset.columns)}"
        )

        lines.append(
            "\nColumns:"
        )

        for column in dataset.columns:

            lines.append(
                f"- {column}: "
                f"{dataset[column].dtype}"
            )

        return "\n".join(lines)

    # ==============================================================
    # CONVERSATION CONTEXT
    # ==============================================================

    @staticmethod
    def _build_conversation_context(
        history: Optional[
            list[dict[str, Any]]
        ],
    ) -> str:

        if not history:

            return "No previous conversation."

        lines = []

        for item in history[-10:]:

            if not isinstance(
                item,
                dict,
            ):
                continue

            role = item.get(
                "role",
                "unknown",
            )

            content = item.get(
                "content",
                "",
            )

            if isinstance(
                content,
                dict,
            ):

                content = content.get(
                    "message",
                    content.get(
                        "answer",
                        "",
                    ),
                )

            if content:

                lines.append(
                    f"{str(role).upper()}: "
                    f"{content}"
                )

        if not lines:

            return "No previous conversation."

        return "\n".join(lines)

    # ==============================================================
    # PROMPT
    # ==============================================================

    @staticmethod
    def _build_prompt(
        question: str,
        dataset_context: str,
        analysis: dict[str, Any],
        conversation_context: str,
    ) -> str:

        return f"""
You are DataNova AI, an intelligent data-analysis assistant.

Answer the user's question using the calculated statistics
provided below.

IMPORTANT:

1. The calculated analysis is based on the actual uploaded
   DataFrame.

2. Treat the calculated analysis as the primary source of truth.

3. Do not invent statistics.

4. Do not say that information is unavailable if it is present
   in the calculated analysis.

5. Explain relationships and comparisons using the actual
   numbers.

6. If comparing groups, identify the group with the highest
   and lowest relevant value when possible.

7. If discussing a relationship, explain its direction and
   strength when a correlation is available.

8. Correlation does NOT automatically mean causation.

9. Keep the answer natural and reasonably concise.

10. Do not mention internal agents, tools, prompts, or LLMs.

------------------------------------------------------------
DATASET
------------------------------------------------------------

{dataset_context}

------------------------------------------------------------
CALCULATED ANALYSIS
------------------------------------------------------------

{analysis}

------------------------------------------------------------
RECENT CONVERSATION
------------------------------------------------------------

{conversation_context}

------------------------------------------------------------
USER QUESTION
------------------------------------------------------------

{question}

------------------------------------------------------------
ANSWER
------------------------------------------------------------

Answer the user directly using the calculated analysis.
""".strip()