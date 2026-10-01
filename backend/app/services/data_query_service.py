from __future__ import annotations

import re
from typing import Any, Optional

import pandas as pd

from app.core.ai_engine.response import AIResponse


class DataQueryService:
    """
    Deterministic data analysis service for DataNova AI.

    Supports:
    - Total rows / passengers
    - Conditional counts
    - Male / female counts
    - Passenger class counts
    - Survival counts
    - Percentages
    - Averages
    - Medians
    - Minimum / maximum
    - Totals / sums
    - Unique values
    - Distributions
    - Missing values
    - Multiple questions in one message
    - Filtered analysis
    - Basic conversation follow-ups
    """

    # ==============================================================
    # PUBLIC ENTRY POINT
    # ==============================================================

    @classmethod
    def answer(
        cls,
        dataset: pd.DataFrame,
        question: str,
        conversation_history: Optional[list[dict[str, Any]]] = None,
    ) -> AIResponse:

        # ----------------------------------------------------------
        # Validate dataset
        # ----------------------------------------------------------

        if dataset is None or not isinstance(dataset, pd.DataFrame):
            return AIResponse(
                success=False,
                message="No valid dataset is available.",
                agent="DataQueryAgent",
                intent="data_question",
            )

        if dataset.empty:
            return AIResponse(
                success=False,
                message="The dataset is empty.",
                agent="DataQueryAgent",
                intent="data_question",
            )

        if not question or not question.strip():
            return AIResponse(
                success=False,
                message="Please provide a question about the dataset.",
                agent="DataQueryAgent",
                intent="data_question",
            )

        question = question.strip()

        # ----------------------------------------------------------
        # Multiple questions
        # ----------------------------------------------------------

        questions = cls._split_questions(question)

        if len(questions) > 1:
            return cls._handle_multiple_questions(
                dataset=dataset,
                questions=questions,
                conversation_history=conversation_history,
            )

        # ----------------------------------------------------------
        # Previous result / follow-up
        # ----------------------------------------------------------

        previous_result = cls._get_previous_result(
            conversation_history
        )

        if previous_result is not None:

            context_followup = cls._handle_context_followup(
                dataset=dataset,
                question=question,
                previous_result=previous_result,
            )

            if context_followup is not None:
                return context_followup

            follow_up = cls._handle_previous_result_followup(
                question,
                previous_result,
            )

            if follow_up is not None:
                return follow_up

        # ----------------------------------------------------------
        # FILTERED ANALYSIS
        #
        # Must happen before normal average/min/max/etc.
        #
        # Example:
        #
        # average age of passengers who survived
        #
        # First filter:
        #     Survived = 1
        #
        # Then calculate:
        #     mean(Age)
        # ----------------------------------------------------------

        filtered_result = cls._handle_filtered_analysis(
            dataset,
            question,
        )

        if filtered_result is not None:
            return filtered_result

        # ----------------------------------------------------------
        # CONDITIONAL COUNT
        # ----------------------------------------------------------

        result = cls._handle_conditional_count(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # CATEGORICAL COUNT
        # ----------------------------------------------------------

        result = cls._handle_categorical_count(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # TOTAL PASSENGER / ROW COUNT
        # ----------------------------------------------------------

        if cls._is_passenger_count_question(question):
            return cls._passenger_count(dataset)

        # ----------------------------------------------------------
        # PERCENTAGE
        # ----------------------------------------------------------

        result = cls._handle_percentage(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # AVERAGE
        # ----------------------------------------------------------

        result = cls._handle_average(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # MEDIAN
        # ----------------------------------------------------------

        result = cls._handle_median(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # MINIMUM
        # ----------------------------------------------------------

        result = cls._handle_minimum(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # MAXIMUM
        # ----------------------------------------------------------

        result = cls._handle_maximum(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # UNIQUE
        # ----------------------------------------------------------

        result = cls._handle_unique(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # DISTRIBUTION
        # ----------------------------------------------------------

        result = cls._handle_distribution(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # MISSING VALUES
        # ----------------------------------------------------------

        result = cls._handle_missing(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # TOTAL / SUM
        # ----------------------------------------------------------

        result = cls._handle_total(
            dataset,
            question,
        )

        if result is not None:
            return result

        # ----------------------------------------------------------
        # Nothing matched
        # ----------------------------------------------------------

        return AIResponse(
            success=False,
            message=(
                "I couldn't determine the requested data calculation. "
                "Please specify a column or ask a more specific question."
            ),
            data={
                "question": question,
                "available_columns": list(dataset.columns),
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    # ==============================================================
    # MULTI QUESTION
    # ==============================================================

    @classmethod
    def _split_questions(
        cls,
        question: str,
    ) -> list[str]:

        if not question:
            return []

        parts = re.split(
            r"(?<=[?!])\s+|\n+",
            question.strip(),
        )

        questions = []

        for part in parts:

            part = part.strip()

            if not part:
                continue

            part = re.sub(
                r"^\s*\d+\s*[\.\)\-:]\s*",
                "",
                part,
            ).strip()

            if part:
                questions.append(part)

        return questions or [question.strip()]

    @classmethod
    def _handle_multiple_questions(
        cls,
        dataset: pd.DataFrame,
        questions: list[str],
        conversation_history: Optional[list[dict[str, Any]]] = None,
    ) -> Optional[AIResponse]:

        if len(questions) <= 1:
            return None

        responses = []
        local_history = list(conversation_history or [])

        for question in questions:
            result = cls.answer(
                dataset=dataset,
                question=question,
                conversation_history=local_history,
            )

            result_data = getattr(result, 'data', None)

            responses.append({
                'question': question,
                'success': bool(getattr(result, 'success', False)),
                'message': (
                    getattr(result, 'message', None)
                    or "I couldn't answer this question."
                ),
                'data': result_data,
            })

            # Chain this result into the next sub-question so that
            # follow-ups like "What about females?" and "What about
            # males?" can use the immediately preceding calculation.
            if isinstance(result_data, dict) and result_data.get('type'):
                local_history.append({
                    'role': 'assistant',
                    'content': {'data': result_data},
                })

        successful = [
            item for item in responses if item['success']
        ]

        if not successful:
            return AIResponse(
                success=False,
                message=(
                    "I couldn't answer the questions "
                    "from the dataset."
                ),
                data={
                    'type': 'multi_question',
                    'responses': responses,
                },
                agent='DataQueryAgent',
                intent='data_question',
            )

        lines = [
            f"{index}. {item['message']}"
            for index, item in enumerate(responses, start=1)
        ]

        return AIResponse(
            success=True,
            message='\n'.join(lines),
            data={
                'type': 'multi_question',
                'responses': responses,
                'count': len(responses),
                'successful': len(successful),
            },
            agent='DataQueryAgent',
            intent='data_question',
        )

    # FILTERED ANALYSIS
    # ==============================================================

    @classmethod
    def _handle_filtered_analysis(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower().strip()

        # ----------------------------------------------------------
        # Determine whether the question contains a filter.
        # ----------------------------------------------------------

        filter_words = [
            "who survived",
            "who did not survive",
            "who didn't survive",
            "that survived",
            "that did not survive",
            "that didn't survive",
            "female passengers",
            "male passengers",
            "females",
            "males",
            "women",
            "men",
            "over ",
            "above ",
            "under ",
            "below ",
            "older than ",
            "younger than ",
            "at least ",
            "at most ",
            "first class",
            "second class",
            "third class",
            "1st class",
            "2nd class",
            "3rd class",
        ]

        if not any(
            word in q
            for word in filter_words
        ):
            return None

        filtered = dataset.copy()

        filters = []

        survived_column = cls._find_column(
            dataset,
            "Survived",
        )

        sex_column = cls._find_column(
            dataset,
            "Sex",
        )

        pclass_column = cls._find_column(
            dataset,
            "Pclass",
        )

        age_column = cls._find_column(
            dataset,
            "Age",
        )

        # ----------------------------------------------------------
        # Survival filter
        # ----------------------------------------------------------

        if survived_column is not None:

            survival = pd.to_numeric(
                filtered[survived_column],
                errors="coerce",
            )

            if cls._contains_any(
                q,
                [
                    "did not survive",
                    "didn't survive",
                    "not survive",
                    "dead",
                    "died",
                ],
            ):

                filtered = filtered[
                    survival.eq(0)
                ]

                filters.append(
                    "Survived = 0"
                )

            elif (
                "survived" in q
                or "survivor" in q
                or "survivors" in q
            ):

                filtered = filtered[
                    survival.eq(1)
                ]

                filters.append(
                    "Survived = 1"
                )

        # ----------------------------------------------------------
        # Sex filter
        # ----------------------------------------------------------

        sex_value = None

        if sex_column is not None:

            if (
                "female" in q
                or "females" in q
                or "women" in q
            ):

                sex_value = "female"

            elif (
                "male" in q
                or "males" in q
                or "men" in q
            ):

                sex_value = "male"

            if sex_value is not None:

                sex_series = (
                    filtered[sex_column]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                )

                filtered = filtered[
                    sex_series.eq(
                        sex_value
                    )
                ]

                filters.append(
                    f"Sex = {sex_value}"
                )

        # ----------------------------------------------------------
        # Passenger class filter
        # ----------------------------------------------------------

        class_value = None

        if pclass_column is not None:

            if cls._contains_any(
                q,
                [
                    "first class",
                    "1st class",
                    "class 1",
                    "pclass 1",
                ],
            ):

                class_value = 1

            elif cls._contains_any(
                q,
                [
                    "second class",
                    "2nd class",
                    "class 2",
                    "pclass 2",
                ],
            ):

                class_value = 2

            elif cls._contains_any(
                q,
                [
                    "third class",
                    "3rd class",
                    "class 3",
                    "pclass 3",
                ],
            ):

                class_value = 3

            if class_value is not None:

                pclass = pd.to_numeric(
                    filtered[pclass_column],
                    errors="coerce",
                )

                filtered = filtered[
                    pclass.eq(
                        class_value
                    )
                ]

                filters.append(
                    f"Pclass = {class_value}"
                )

        # ----------------------------------------------------------
        # Age filter
        # ----------------------------------------------------------

        age_filter = None

        if age_column is not None:

            age_filter = cls._extract_numeric_filter(
                q,
                "age",
            )

            if age_filter is not None:

                operator, number = age_filter

                age = pd.to_numeric(
                    filtered[age_column],
                    errors="coerce",
                )

                if operator == ">":
                    filtered = filtered[
                        age > number
                    ]

                elif operator == ">=":
                    filtered = filtered[
                        age >= number
                    ]

                elif operator == "<":
                    filtered = filtered[
                        age < number
                    ]

                elif operator == "<=":
                    filtered = filtered[
                        age <= number
                    ]

                elif operator == "==":
                    filtered = filtered[
                        age == number
                    ]

                filters.append(
                    f"Age {operator} {number:g}"
                )

        # ----------------------------------------------------------
        # No records
        # ----------------------------------------------------------

        if filtered.empty:

            return AIResponse(
                success=True,
                message=(
                    "No records match the conditions "
                    "in your question."
                ),
                data={
                    "type": "filtered_analysis",
                    "value": 0,
                    "count": 0,
                    "filters": filters,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        # ----------------------------------------------------------
        # PERCENTAGE
        # ----------------------------------------------------------

        if cls._contains_any(
            q,
            [
                "percentage",
                "percent",
                "proportion",
            ],
        ):

            # ------------------------------------------------------
            # Female / male survival percentage
            #
            # denominator = total females/males
            # ------------------------------------------------------

            if (
                sex_value is not None
                and survived_column is not None
                and (
                    "survived" in q
                    or "surviv" in q
                )
                and class_value is None
                and age_filter is None
            ):

                group_mask = (
                    dataset[sex_column]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .eq(sex_value)
                )

                group_total = int(
                    group_mask.sum()
                )

                if group_total == 0:

                    return AIResponse(
                        success=True,
                        message=(
                            f"There are no {sex_value} "
                            "passengers in the dataset."
                        ),
                        data={
                            "type": "filtered_percentage",
                            "value": 0,
                            "count": 0,
                            "total": 0,
                        },
                        agent="DataQueryAgent",
                        intent="data_question",
                    )

                survival_value = 0 if cls._contains_any(
                    q,
                    [
                        "did not survive",
                        "didn't survive",
                        "not survive",
                    ],
                ) else 1

                survival_mask = (
                    pd.to_numeric(
                        dataset[survived_column],
                        errors="coerce",
                    ).eq(
                        survival_value
                    )
                )

                count = int(
                    (
                        group_mask
                        & survival_mask
                    ).sum()
                )

                percentage = round(
                    (
                        count
                        / group_total
                    )
                    * 100,
                    2,
                )

                survival_text = (
                    "survived"
                    if survival_value == 1
                    else "did not survive"
                )

                return AIResponse(
                    success=True,
                    message=(
                        f"{percentage:.2f}% of "
                        f"{sex_value} passengers "
                        f"{survival_text}."
                    ),
                    data={
                        "type": "filtered_percentage",
                        "column": survived_column,
                        "filter_column": sex_column,
                        "filter": sex_value,
                        "value": percentage,
                        "count": count,
                        "total": group_total,
                        "condition": survival_value,
                        "description": (
                            f"percentage of {sex_value} "
                            f"passengers who {survival_text}"
                        ),
                    },
                    agent="DataQueryAgent",
                    intent="data_question",
                )

            # ------------------------------------------------------
            # Class survival percentage
            # ------------------------------------------------------

            if (
                class_value is not None
                and survived_column is not None
                and "surviv" in q
            ):

                class_mask = (
                    pd.to_numeric(
                        dataset[pclass_column],
                        errors="coerce",
                    ).eq(
                        class_value
                    )
                )

                class_total = int(
                    class_mask.sum()
                )

                if class_total == 0:
                    return None

                survival_mask = (
                    pd.to_numeric(
                        dataset[survived_column],
                        errors="coerce",
                    ).eq(1)
                )

                count = int(
                    (
                        class_mask
                        & survival_mask
                    ).sum()
                )

                percentage = round(
                    (
                        count
                        / class_total
                    )
                    * 100,
                    2,
                )

                ordinal = {
                    1: "first",
                    2: "second",
                    3: "third",
                }[class_value]

                return AIResponse(
                    success=True,
                    message=(
                        f"{percentage:.2f}% of "
                        f"{ordinal} class passengers "
                        "survived."
                    ),
                    data={
                        "type": "filtered_percentage",
                        "column": survived_column,
                        "filter_column": pclass_column,
                        "filter": class_value,
                        "value": percentage,
                        "count": count,
                        "total": class_total,
                        "condition": 1,
                    },
                    agent="DataQueryAgent",
                    intent="data_question",
                )

            # ------------------------------------------------------
            # Generic filtered percentage
            # ------------------------------------------------------

            percentage = round(
                (
                    len(filtered)
                    / len(dataset)
                )
                * 100,
                2,
            )

            return AIResponse(
                success=True,
                message=(
                    f"{percentage:.2f}% of passengers "
                    "match the specified conditions."
                ),
                data={
                    "type": "filtered_percentage",
                    "value": percentage,
                    "count": len(filtered),
                    "total": len(dataset),
                    "filters": filters,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        # ----------------------------------------------------------
        # COUNT
        # ----------------------------------------------------------

        if cls._contains_any(
            q,
            [
                "how many",
                "number of",
                "count of",
            ],
        ):

            filter_text = (
                ", ".join(filters)
                if filters
                else "specified conditions"
            )

            return AIResponse(
                success=True,
                message=(
                    f"{len(filtered)} passengers match "
                    f"the {filter_text}."
                ),
                data={
                    "type": "filtered_count",
                    "value": len(filtered),
                    "count": len(filtered),
                    "filters": filters,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        # ----------------------------------------------------------
        # Determine target column
        # ----------------------------------------------------------

        target_column = cls._extract_analysis_target_column(
            dataset,
            question,
        )

        if target_column is None:
            return None

        values = pd.to_numeric(
            filtered[target_column],
            errors="coerce",
        ).dropna()

        if values.empty:

            return AIResponse(
                success=False,
                message=(
                    f"The {target_column} column has no numeric "
                    "values for the selected records."
                ),
                agent="DataQueryAgent",
                intent="data_question",
            )

        filter_text = (
            " for the filtered passengers"
            if filters
            else ""
        )

        # ----------------------------------------------------------
        # AVERAGE
        # ----------------------------------------------------------

        if cls._contains_any(
            q,
            [
                "average",
                "mean",
            ],
        ):

            value = round(
                float(values.mean()),
                2,
            )

            return AIResponse(
                success=True,
                message=(
                    f"The average {target_column}"
                    f"{filter_text} is {value:.2f}."
                ),
                data={
                    "type": "filtered_average",
                    "column": target_column,
                    "value": value,
                    "count": len(filtered),
                    "filtered_count": len(filtered),
                    "filters": filters,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        # ----------------------------------------------------------
        # MEDIAN
        # ----------------------------------------------------------

        if "median" in q:

            value = round(
                float(values.median()),
                2,
            )

            return AIResponse(
                success=True,
                message=(
                    f"The median {target_column}"
                    f"{filter_text} is {value:.2f}."
                ),
                data={
                    "type": "filtered_median",
                    "column": target_column,
                    "value": value,
                    "count": len(filtered),
                    "filters": filters,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        # ----------------------------------------------------------
        # MINIMUM
        # ----------------------------------------------------------

        if cls._contains_any(
            q,
            [
                "minimum",
                "lowest",
                "smallest",
            ],
        ):

            value = float(
                values.min()
            )

            return AIResponse(
                success=True,
                message=(
                    f"The minimum {target_column}"
                    f"{filter_text} is {value:g}."
                ),
                data={
                    "type": "filtered_minimum",
                    "column": target_column,
                    "value": value,
                    "count": len(filtered),
                    "filters": filters,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        # ----------------------------------------------------------
        # MAXIMUM
        # ----------------------------------------------------------

        if cls._contains_any(
            q,
            [
                "maximum",
                "highest",
                "largest",
            ],
        ):

            value = float(
                values.max()
            )

            return AIResponse(
                success=True,
                message=(
                    f"The maximum {target_column}"
                    f"{filter_text} is {value:g}."
                ),
                data={
                    "type": "filtered_maximum",
                    "column": target_column,
                    "value": value,
                    "count": len(filtered),
                    "filters": filters,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        return None

    # ==============================================================
    # NUMERICAL FILTER
    # ==============================================================

    @classmethod
    def _extract_numeric_filter(
        cls,
        question: str,
        column_name: str,
    ) -> Optional[tuple[str, float]]:

        q = question.lower()

        column = re.escape(
            column_name
        )

        patterns = [
            (
                rf"\b{column}\s*(?:is\s*)?"
                rf"(?:greater than|over|above|older than)\s*"
                rf"(\d+(?:\.\d+)?)",
                ">",
            ),
            (
                rf"\b{column}\s*(?:is\s*)?"
                rf"at least\s*"
                rf"(\d+(?:\.\d+)?)",
                ">=",
            ),
            (
                rf"\b{column}\s*(?:is\s*)?"
                rf"(?:less than|under|below|younger than)\s*"
                rf"(\d+(?:\.\d+)?)",
                "<",
            ),
            (
                rf"\b{column}\s*(?:is\s*)?"
                rf"at most\s*"
                rf"(\d+(?:\.\d+)?)",
                "<=",
            ),
            (
                rf"\b{column}\s*(?:is\s*)?"
                rf"(?:equal to|equals|=)\s*"
                rf"(\d+(?:\.\d+)?)",
                "==",
            ),
        ]

        natural_patterns = [
            (
                r"(?:over|above|older than)\s+"
                r"(?:age\s+)?"
                r"(\d+(?:\.\d+)?)",
                ">",
            ),
            (
                r"at least\s+"
                r"(?:age\s+)?"
                r"(\d+(?:\.\d+)?)",
                ">=",
            ),
            (
                r"(?:under|below|younger than)\s+"
                r"(?:age\s+)?"
                r"(\d+(?:\.\d+)?)",
                "<",
            ),
            (
                r"at most\s+"
                r"(?:age\s+)?"
                r"(\d+(?:\.\d+)?)",
                "<=",
            ),
        ]

        for pattern, operator in patterns:

            match = re.search(
                pattern,
                q,
            )

            if match:
                return (
                    operator,
                    float(
                        match.group(1)
                    ),
                )

        for pattern, operator in natural_patterns:

            match = re.search(
                pattern,
                q,
            )

            if match:
                return (
                    operator,
                    float(
                        match.group(1)
                    ),
                )

        return None

    # ==============================================================
    # ANALYSIS TARGET COLUMN
    # ==============================================================

    @classmethod
    def _extract_analysis_target_column(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[str]:

        q = question.lower()

        # ----------------------------------------------------------
        # Explicit metric aliases
        # ----------------------------------------------------------

        aliases = {
            "Age": [
                "age",
                "ages",
            ],
            "Fare": [
                "fare",
                "ticket fare",
                "price",
                "ticket price",
            ],
            "SibSp": [
                "sibsp",
                "siblings",
                "siblings/spouses",
            ],
            "Parch": [
                "parch",
                "parents",
                "parents/children",
            ],
            "Pclass": [
                "pclass",
                "passenger class",
            ],
        }

        for target, words in aliases.items():

            if any(
                word in q
                for word in words
            ):

                column = cls._find_column(
                    dataset,
                    target,
                )

                if column is not None:
                    return column

        # ----------------------------------------------------------
        # General numeric columns
        #
        # Exclude columns that are normally filters.
        # ----------------------------------------------------------

        excluded = {
            "survived",
            "sex",
            "name",
            "ticket",
            "cabin",
            "embarked",
            "passengerid",
        }

        numeric_columns = []

        for column in dataset.columns:

            normalized = cls._normalize_column_name(
                str(column)
            )

            if normalized in excluded:
                continue

            if pd.api.types.is_numeric_dtype(
                dataset[column]
            ):
                numeric_columns.append(
                    str(column)
                )

        for column in sorted(
            numeric_columns,
            key=len,
            reverse=True,
        ):

            if column.lower() in q:
                return column

        return None

    # ==============================================================
    # CONDITIONAL COUNT
    # ==============================================================

    @classmethod
    def _handle_conditional_count(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower().strip()

        survived_column = cls._find_column(
            dataset,
            "Survived",
        )

        sex_column = cls._find_column(
            dataset,
            "Sex",
        )

        pclass_column = cls._find_column(
            dataset,
            "Pclass",
        )

        # ----------------------------------------------------------
        # Female/male + survival
        # ----------------------------------------------------------

        if (
            sex_column is not None
            and survived_column is not None
            and (
                "female" in q
                or "male" in q
                or "women" in q
                or "men" in q
            )
            and "surviv" in q
        ):

            if (
                "female" in q
                or "women" in q
            ):
                sex_value = "female"
            else:
                sex_value = "male"

            survival_value = (
                0
                if cls._contains_any(
                    q,
                    [
                        "did not survive",
                        "didn't survive",
                        "not survive",
                    ],
                )
                else 1
            )

            sex_mask = (
                dataset[sex_column]
                .astype(str)
                .str.strip()
                .str.lower()
                .eq(sex_value)
            )

            survival_mask = (
                pd.to_numeric(
                    dataset[survived_column],
                    errors="coerce",
                ).eq(
                    survival_value
                )
            )

            count = int(
                (
                    sex_mask
                    & survival_mask
                ).sum()
            )

            survival_text = (
                "survived"
                if survival_value == 1
                else "did not survive"
            )

            return AIResponse(
                success=True,
                message=(
                    f"{count} {sex_value} passengers "
                    f"{survival_text}."
                ),
                data={
                    "type": "conditional_count",
                    "column": survived_column,
                    "filter_column": sex_column,
                    "value": count,
                    "count": count,
                    "condition": survival_value,
                    "filter": sex_value,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        # ----------------------------------------------------------
        # Survival
        # ----------------------------------------------------------

        if survived_column is not None:

            not_survived_phrases = [
                "how many did not survive",
                "how many didn't survive",
                "number did not survive",
                "number didn't survive",
                "how many passengers did not survive",
                "how many passengers didn't survive",
                "number of passengers who did not survive",
                "number of passengers who didn't survive",
                "how many people did not survive",
                "how many people didn't survive",
                "how many died",
                "number of deaths",
            ]

            survived_phrases = [
                "how many survived",
                "number survived",
                "how many passengers survived",
                "number of passengers survived",
                "number of passengers who survived",
                "how many people survived",
                "number of people survived",
                "how many survivors",
                "number of survivors",
            ]

            if cls._contains_any(
                q,
                not_survived_phrases,
            ):

                count = cls._binary_count(
                    dataset[survived_column],
                    0,
                )

                return AIResponse(
                    success=True,
                    message=(
                        f"{count} passengers "
                        "did not survive."
                    ),
                    data={
                        "type": "conditional_count",
                        "column": survived_column,
                        "value": count,
                        "count": count,
                        "condition": 0,
                    },
                    agent="DataQueryAgent",
                    intent="data_question",
                )

            if cls._contains_any(
                q,
                survived_phrases,
            ):

                count = cls._binary_count(
                    dataset[survived_column],
                    1,
                )

                return AIResponse(
                    success=True,
                    message=(
                        f"{count} passengers survived."
                    ),
                    data={
                        "type": "conditional_count",
                        "column": survived_column,
                        "value": count,
                        "count": count,
                        "condition": 1,
                    },
                    agent="DataQueryAgent",
                    intent="data_question",
                )

        # ----------------------------------------------------------
        # Female count
        # ----------------------------------------------------------

        if sex_column is not None:

            if cls._contains_any(
                q,
                [
                    "how many female",
                    "how many females",
                    "number of female",
                    "number of females",
                    "how many women",
                    "number of women",
                    "how many female passengers",
                    "number of female passengers",
                ],
            ):

                count = int(
                    dataset[sex_column]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .eq("female")
                    .sum()
                )

                return AIResponse(
                    success=True,
                    message=(
                        f"{count} passengers were female."
                    ),
                    data={
                        "type": "conditional_count",
                        "column": sex_column,
                        "value": count,
                        "count": count,
                        "condition": "female",
                    },
                    agent="DataQueryAgent",
                    intent="data_question",
                )

            # ------------------------------------------------------
            # Male count
            # ------------------------------------------------------

            if cls._contains_any(
                q,
                [
                    "how many male",
                    "how many males",
                    "number of male",
                    "number of males",
                    "how many men",
                    "number of men",
                    "how many male passengers",
                    "number of male passengers",
                ],
            ):

                count = int(
                    dataset[sex_column]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .eq("male")
                    .sum()
                )

                return AIResponse(
                    success=True,
                    message=(
                        f"{count} passengers were male."
                    ),
                    data={
                        "type": "conditional_count",
                        "column": sex_column,
                        "value": count,
                        "count": count,
                        "condition": "male",
                    },
                    agent="DataQueryAgent",
                    intent="data_question",
                )

        # ----------------------------------------------------------
        # Passenger class
        # ----------------------------------------------------------

        if pclass_column is not None:

            classes = [
                (
                    1,
                    [
                        "first class",
                        "1st class",
                        "class 1",
                        "pclass 1",
                    ],
                    "first",
                ),
                (
                    2,
                    [
                        "second class",
                        "2nd class",
                        "class 2",
                        "pclass 2",
                    ],
                    "second",
                ),
                (
                    3,
                    [
                        "third class",
                        "3rd class",
                        "class 3",
                        "pclass 3",
                    ],
                    "third",
                ),
            ]

            if cls._contains_any(
                q,
                [
                    "how many",
                    "number of",
                    "count of",
                ],
            ):

                for value, words, ordinal in classes:

                    if cls._contains_any(
                        q,
                        words,
                    ):

                        pclass = pd.to_numeric(
                            dataset[pclass_column],
                            errors="coerce",
                        )

                        count = int(
                            pclass.eq(value).sum()
                        )

                        return AIResponse(
                            success=True,
                            message=(
                                f"{count} passengers were "
                                f"in {ordinal} class."
                            ),
                            data={
                                "type": "conditional_count",
                                "column": pclass_column,
                                "value": count,
                                "count": count,
                                "condition": value,
                            },
                            agent="DataQueryAgent",
                            intent="data_question",
                        )

        return None

    # ==============================================================
    # CATEGORICAL COUNT
    # ==============================================================

    @classmethod
    def _handle_categorical_count(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower().strip()

        if not cls._contains_any(
            q,
            [
                "how many",
                "number of",
                "count of",
            ],
        ):
            return None

        if "surviv" in q:
            return None

        if cls._is_passenger_count_question(q):
            return None

        column = cls._extract_column_from_question(
            dataset,
            question,
        )

        if column is None:
            return None

        values = (
            dataset[column]
            .dropna()
            .unique()
        )

        if len(values) > 20:
            return None

        for value in values:

            value_text = (
                str(value)
                .strip()
                .lower()
            )

            if len(value_text) < 2:
                continue

            if value_text in q:

                mask = (
                    dataset[column]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .eq(value_text)
                )

                count = int(
                    mask.sum()
                )

                return AIResponse(
                    success=True,
                    message=(
                        f"There are {count} records where "
                        f"{column} = {value}."
                    ),
                    data={
                        "type": "conditional_count",
                        "column": column,
                        "value": count,
                        "count": count,
                        "condition": value,
                    },
                    agent="DataQueryAgent",
                    intent="data_question",
                )

        return None

    # ==============================================================
    # TOTAL PASSENGER COUNT
    # ==============================================================

    @classmethod
    def _is_passenger_count_question(
        cls,
        question: str,
    ) -> bool:

        q = question.lower().strip()

        phrases = [
            "how many passengers",
            "number of passengers",
            "total passengers",
            "total number of passengers",
            "how many people",
            "number of people",
            "total people",
            "how many records",
            "number of records",
            "total records",
            "how many rows",
            "number of rows",
            "total rows",
        ]

        if cls._is_count_followup(
            question
        ):
            return False

        conditional_words = [
            "survived",
            "did not survive",
            "didn't survive",
            "female",
            "females",
            "male",
            "males",
            "women",
            "men",
            "pclass",
            "passenger class",
            "first class",
            "second class",
            "third class",
        ]

        if any(
            word in q
            for word in conditional_words
        ):
            return False

        return any(
            phrase in q
            for phrase in phrases
        )

    @classmethod
    def _passenger_count(
        cls,
        dataset: pd.DataFrame,
    ) -> AIResponse:

        count = len(dataset)

        return AIResponse(
            success=True,
            message=(
                f"There are {count} passengers "
                "in the dataset."
            ),
            data={
                "type": "count",
                "value": count,
                "count": count,
                "description": (
                    "total number of passengers"
                ),
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    # ==============================================================
    # PERCENTAGE
    # ==============================================================

    @classmethod
    def _handle_percentage(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower().strip()

        if not cls._contains_any(
            q,
            [
                "percentage",
                "percent",
                "proportion",
                "share",
            ],
        ):
            return None

        total = len(dataset)

        if total == 0:
            return None

        survived_column = cls._find_column(
            dataset,
            "Survived",
        )

        # ----------------------------------------------------------
        # Survival percentage
        # ----------------------------------------------------------

        if (
            survived_column is not None
            and "survived" in q
        ):

            if cls._contains_any(
                q,
                [
                    "did not survive",
                    "didn't survive",
                    "not survive",
                    "dead",
                    "died",
                ],
            ):

                condition = 0

            else:

                condition = 1

            count = cls._binary_count(
                dataset[survived_column],
                condition,
            )

            percentage = round(
                (
                    count
                    / total
                )
                * 100,
                2,
            )

            if condition == 1:

                message = (
                    f"{percentage:.2f}% of passengers survived."
                )

            else:

                message = (
                    f"{percentage:.2f}% of passengers "
                    "did not survive."
                )

            return AIResponse(
                success=True,
                message=message,
                data={
                    "type": "percentage",
                    "column": survived_column,
                    "value": percentage,
                    "count": count,
                    "total": total,
                    "condition": condition,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        # ----------------------------------------------------------
        # Female / male percentage of whole dataset
        # ----------------------------------------------------------

        sex_column = cls._find_column(
            dataset,
            "Sex",
        )

        if (
            sex_column is not None
            and (
                "female" in q
                or "male" in q
            )
        ):

            value = (
                "female"
                if "female" in q
                else "male"
            )

            count = int(
                dataset[sex_column]
                .astype(str)
                .str.strip()
                .str.lower()
                .eq(value)
                .sum()
            )

            percentage = round(
                (
                    count
                    / total
                )
                * 100,
                2,
            )

            return AIResponse(
                success=True,
                message=(
                    f"{percentage:.2f}% of passengers "
                    f"were {value}."
                ),
                data={
                    "type": "percentage",
                    "column": sex_column,
                    "value": percentage,
                    "count": count,
                    "total": total,
                    "condition": value,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        return None

    # ==============================================================
    # AVERAGE
    # ==============================================================

    @classmethod
    def _handle_average(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower()

        if not cls._contains_any(
            q,
            [
                "average",
                "mean",
            ],
        ):
            return None

        column = cls._extract_column_from_question(
            dataset,
            question,
            numerical_only=True,
        )

        if column is None:
            return None

        series = pd.to_numeric(
            dataset[column],
            errors="coerce",
        ).dropna()

        if series.empty:
            return None

        value = round(
            float(series.mean()),
            2,
        )

        return AIResponse(
            success=True,
            message=(
                f"The average {column} "
                f"is {value:.2f}."
            ),
            data={
                "type": "average",
                "column": column,
                "value": value,
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    # ==============================================================
    # MEDIAN
    # ==============================================================

    @classmethod
    def _handle_median(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        if "median" not in question.lower():
            return None

        column = cls._extract_column_from_question(
            dataset,
            question,
            numerical_only=True,
        )

        if column is None:
            return None

        series = pd.to_numeric(
            dataset[column],
            errors="coerce",
        ).dropna()

        if series.empty:
            return None

        value = round(
            float(series.median()),
            2,
        )

        return AIResponse(
            success=True,
            message=(
                f"The median {column} "
                f"is {value:.2f}."
            ),
            data={
                "type": "median",
                "column": column,
                "value": value,
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    # ==============================================================
    # MINIMUM
    # ==============================================================

    @classmethod
    def _handle_minimum(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower()

        if not (
            cls._contains_any(
                q,
                [
                    "minimum",
                    "lowest",
                    "smallest",
                ],
            )
            or q.startswith("min ")
        ):
            return None

        column = cls._extract_column_from_question(
            dataset,
            question,
            numerical_only=True,
        )

        if column is None:
            return None

        series = pd.to_numeric(
            dataset[column],
            errors="coerce",
        ).dropna()

        if series.empty:
            return None

        value = float(
            series.min()
        )

        display = (
            str(int(value))
            if value.is_integer()
            else f"{value:.2f}"
        )

        return AIResponse(
            success=True,
            message=(
                f"The minimum {column} "
                f"is {display}."
            ),
            data={
                "type": "minimum",
                "column": column,
                "value": value,
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    # ==============================================================
    # MAXIMUM
    # ==============================================================

    @classmethod
    def _handle_maximum(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower()

        if not (
            cls._contains_any(
                q,
                [
                    "maximum",
                    "highest",
                    "largest",
                ],
            )
            or q.startswith("max ")
        ):
            return None

        column = cls._extract_column_from_question(
            dataset,
            question,
            numerical_only=True,
        )

        if column is None:
            return None

        series = pd.to_numeric(
            dataset[column],
            errors="coerce",
        ).dropna()

        if series.empty:
            return None

        value = float(
            series.max()
        )

        display = (
            str(int(value))
            if value.is_integer()
            else f"{value:.2f}"
        )

        return AIResponse(
            success=True,
            message=(
                f"The maximum {column} "
                f"is {display}."
            ),
            data={
                "type": "maximum",
                "column": column,
                "value": value,
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    # ==============================================================
    # UNIQUE
    # ==============================================================

    @classmethod
    def _handle_unique(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower()

        if not cls._contains_any(
            q,
            [
                "unique",
                "distinct",
            ],
        ):
            return None

        column = cls._extract_column_from_question(
            dataset,
            question,
        )

        if column is None:
            return None

        count = int(
            dataset[column].nunique(
                dropna=True
            )
        )

        return AIResponse(
            success=True,
            message=(
                f"The {column} column has "
                f"{count} unique values."
            ),
            data={
                "type": "unique",
                "column": column,
                "value": count,
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    # ==============================================================
    # DISTRIBUTION
    # ==============================================================

    @classmethod
    def _handle_distribution(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower()

        if not cls._contains_any(
            q,
            [
                "distribution",
                "frequency",
                "frequencies",
                "breakdown",
            ],
        ):
            return None

        column = cls._extract_column_from_question(
            dataset,
            question,
        )

        if column is None:
            return None

        values = (
            dataset[column]
            .value_counts(
                dropna=False
            )
            .to_dict()
        )

        cleaned = {}

        for key, value in values.items():

            if pd.isna(key):
                key = "Missing"

            cleaned[str(key)] = int(value)

        return AIResponse(
            success=True,
            message=(
                f"Here is the distribution "
                f"of the {column} column."
            ),
            data={
                "type": "distribution",
                "column": column,
                "value": cleaned,
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    # ==============================================================
    # MISSING VALUES
    # ==============================================================

    @classmethod
    def _handle_missing(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower()

        if not cls._contains_any(
            q,
            [
                "missing",
                "null",
                "empty",
                "na values",
                "nan",
            ],
        ):
            return None

        column = cls._extract_column_from_question(
            dataset,
            question,
        )

        if column is not None:

            count = int(
                dataset[column]
                .isna()
                .sum()
            )

            percentage = round(
                (
                    count
                    / len(dataset)
                )
                * 100,
                2,
            )

            return AIResponse(
                success=True,
                message=(
                    f"The {column} column has "
                    f"{count} missing values "
                    f"({percentage:.2f}%)."
                ),
                data={
                    "type": "missing",
                    "column": column,
                    "value": count,
                    "percentage": percentage,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        missing = {
            str(column): int(value)
            for column, value in (
                dataset.isna()
                .sum()
                .to_dict()
                .items()
            )
        }

        return AIResponse(
            success=True,
            message=(
                "Here are the missing values by column."
            ),
            data={
                "type": "missing",
                "value": missing,
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    # ==============================================================
    # TOTAL / SUM
    # ==============================================================

    @classmethod
    def _handle_total(
        cls,
        dataset: pd.DataFrame,
        question: str,
    ) -> Optional[AIResponse]:

        q = question.lower()

        if not cls._contains_any(
            q,
            [
                "total",
                "sum",
            ],
        ):
            return None

        if cls._contains_any(
            q,
            [
                "total passengers",
                "total number of passengers",
                "total people",
                "total records",
                "total rows",
            ],
        ):
            return None

        column = cls._extract_column_from_question(
            dataset,
            question,
            numerical_only=True,
        )

        if column is None:
            return None

        series = pd.to_numeric(
            dataset[column],
            errors="coerce",
        ).dropna()

        if series.empty:
            return None

        value = float(
            series.sum()
        )

        display = (
            str(int(value))
            if value.is_integer()
            else f"{value:.2f}"
        )

        return AIResponse(
            success=True,
            message=(
                f"The total {column} "
                f"is {display}."
            ),
            data={
                "type": "total",
                "column": column,
                "value": value,
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    # ==============================================================
    # FOLLOW-UP HANDLING
    # ==============================================================

    @classmethod
    def _handle_context_followup(
        cls,
        dataset: pd.DataFrame,
        question: str,
        previous_result: dict[str, Any],
    ) -> Optional[AIResponse]:
        """Handle female/male follow-ups using the previous calculation."""

        if dataset is None or not isinstance(dataset, pd.DataFrame):
            return None

        q = question.lower().strip()
        if not q:
            return None

        reference_phrases = [
            "what about", "how about",
            "and females", "and males",
            "and women", "and men",
            "for females", "for males",
            "for women", "for men",
        ]

        if not cls._contains_any(q, reference_phrases):
            return None

        base_result = previous_result
        visited = set()

        while isinstance(base_result, dict):
            source_result = base_result.get("source_result")
            if not isinstance(source_result, dict):
                break
            object_id = id(base_result)
            if object_id in visited:
                break
            visited.add(object_id)
            base_result = source_result

        if not isinstance(base_result, dict):
            return None

        result_type = base_result.get("type")

        if cls._contains_any(q, ["female", "females", "woman", "women"]):
            sex_value = "female"
        elif cls._contains_any(q, ["male", "males", "man", "men"]):
            sex_value = "male"
        else:
            return None

        sex_column = cls._find_column(dataset, "Sex")
        if sex_column is None:
            return None

        sex_mask = (
            dataset[sex_column]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq(sex_value)
        )
        filtered = dataset.loc[sex_mask].copy()

        if filtered.empty:
            return AIResponse(
                success=True,
                message=f"There are no {sex_value} passengers in the dataset.",
                data={
                    "type": "filtered_analysis",
                    "value": 0,
                    "count": 0,
                    "filters": [f"Sex = {sex_value}"],
                    "source_result": base_result,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        column = (
            base_result.get("column")
            or base_result.get("y")
            or base_result.get("metric")
        )

        if (
            result_type in {
                "conditional_count", "count", "filtered_count",
                "previous_result_count",
            }
            and column is not None
            and cls._normalize_column_name(str(column))
            == cls._normalize_column_name("Survived")
        ):
            survived_column = cls._find_column(dataset, "Survived")
            if survived_column is None:
                return None

            condition = base_result.get("condition")
            if condition not in {0, 1}:
                return None

            survival = pd.to_numeric(
                filtered[survived_column], errors="coerce"
            )
            count = int(survival.eq(condition).sum())
            survival_text = "survived" if condition == 1 else "did not survive"

            return AIResponse(
                success=True,
                message=f"{count} {sex_value} passengers {survival_text}.",
                data={
                    "type": "conditional_count",
                    "column": survived_column,
                    "filter_column": sex_column,
                    "value": count,
                    "count": count,
                    "condition": condition,
                    "filter": sex_value,
                    "source_result": base_result,
                },
                agent="DataQueryAgent",
                intent="data_question",
            )

        numerical_types = {
            "average", "median", "minimum", "maximum", "total",
            "filtered_average", "filtered_median",
            "filtered_minimum", "filtered_maximum",
        }

        if result_type not in numerical_types or column is None:
            return None

        actual_column = cls._find_column(dataset, str(column))
        if actual_column is None:
            return None

        values = pd.to_numeric(
            filtered[actual_column], errors="coerce"
        ).dropna()

        if values.empty:
            return AIResponse(
                success=False,
                message=(
                    f"The {actual_column} column has no numeric "
                    f"values for {sex_value} passengers."
                ),
                agent="DataQueryAgent",
                intent="data_question",
            )

        if result_type in {"average", "filtered_average"}:
            value = round(float(values.mean()), 2)
            response_type = "filtered_average"
            message = f"The average {actual_column} for {sex_value} passengers is {value:.2f}."
        elif result_type in {"median", "filtered_median"}:
            value = round(float(values.median()), 2)
            response_type = "filtered_median"
            message = f"The median {actual_column} for {sex_value} passengers is {value:.2f}."
        elif result_type in {"minimum", "filtered_minimum"}:
            value = float(values.min())
            response_type = "filtered_minimum"
            display = str(int(value)) if value.is_integer() else f"{value:.2f}"
            message = f"The minimum {actual_column} for {sex_value} passengers is {display}."
        elif result_type in {"maximum", "filtered_maximum"}:
            value = float(values.max())
            response_type = "filtered_maximum"
            display = str(int(value)) if value.is_integer() else f"{value:.2f}"
            message = f"The maximum {actual_column} for {sex_value} passengers is {display}."
        else:
            value = float(values.sum())
            response_type = "filtered_total"
            display = str(int(value)) if value.is_integer() else f"{value:.2f}"
            message = f"The total {actual_column} for {sex_value} passengers is {display}."

        return AIResponse(
            success=True,
            message=message,
            data={
                "type": response_type,
                "column": actual_column,
                "value": value,
                "count": len(filtered),
                "filtered_count": len(filtered),
                "filters": [f"Sex = {sex_value}"],
                "source_result": base_result,
            },
            agent="DataQueryAgent",
            intent="data_question",
        )

    @classmethod
    def _handle_previous_result_followup(
        cls,
        question: str,
        previous_result: dict[str, Any],
    ) -> Optional[AIResponse]:

        base = previous_result
        visited = set()

        while isinstance(base, dict):

            source = base.get(
                "source_result"
            )

            if not isinstance(
                source,
                dict,
            ):
                break

            if id(base) in visited:
                break

            visited.add(
                id(base)
            )

            base = source

        result_type = base.get(
            "type"
        )

        # ----------------------------------------------------------
        # Count follow-up
        # ----------------------------------------------------------

        if cls._is_count_followup(
            question
        ):

            if result_type in {
                "percentage",
                "filtered_percentage",
            }:

                count = base.get(
                    "count"
                )

                if count is not None:

                    column = base.get(
                        "column"
                    )

                    condition = base.get(
                        "condition"
                    )

                    if (
                        column == "Survived"
                        and condition == 1
                    ):
                        message = (
                            f"{count} passengers survived."
                        )

                    elif (
                        column == "Survived"
                        and condition == 0
                    ):
                        message = (
                            f"{count} passengers "
                            "did not survive."
                        )

                    elif (
                        column == "Sex"
                        and str(
                            condition
                        ).lower()
                        == "female"
                    ):
                        message = (
                            f"{count} passengers were female."
                        )

                    elif (
                        column == "Sex"
                        and str(
                            condition
                        ).lower()
                        == "male"
                    ):
                        message = (
                            f"{count} passengers were male."
                        )

                    else:
                        message = (
                            f"{count} matching records."
                        )

                    return AIResponse(
                        success=True,
                        message=message,
                        data={
                            "type": (
                                "previous_result_count"
                            ),
                            "column": column,
                            "value": count,
                            "count": count,
                            "percentage": base.get(
                                "value"
                            ),
                            "condition": condition,
                            "source_result": base,
                        },
                        agent="DataQueryAgent",
                        intent="data_question",
                    )

            if result_type in {
                "count",
                "conditional_count",
                "filtered_count",
                "previous_result_count",
            }:

                value = base.get(
                    "value"
                )

                if value is not None:

                    return AIResponse(
                        success=True,
                        message=(
                            f"The count was {value}."
                        ),
                        data={
                            "type": "previous_count",
                            "value": value,
                            "column": base.get(
                                "column"
                            ),
                            "condition": base.get(
                                "condition"
                            ),
                            "source_result": base,
                        },
                        agent="DataQueryAgent",
                        intent="data_question",
                    )

        # ----------------------------------------------------------
        # Column follow-up
        # ----------------------------------------------------------

        if cls._is_column_followup(
            question
        ):

            column = base.get(
                "column"
            )

            if column:

                return AIResponse(
                    success=True,
                    message=(
                        f"It was based on the "
                        f"{column} column."
                    ),
                    data={
                        "type": (
                            "previous_result_column"
                        ),
                        "column": column,
                        "value": column,
                        "source_result": base,
                    },
                    agent="DataQueryAgent",
                    intent="data_question",
                )

        # ----------------------------------------------------------
        # Condition follow-up
        # ----------------------------------------------------------

        if cls._is_condition_followup(
            question
        ):

            condition = base.get(
                "condition"
            )

            column = base.get(
                "column"
            )

            if condition is not None:

                if (
                    column == "Survived"
                    and condition == 1
                ):
                    text = (
                        "Survived = 1 (survived)"
                    )

                elif (
                    column == "Survived"
                    and condition == 0
                ):
                    text = (
                        "Survived = 0 "
                        "(did not survive)"
                    )

                elif (
                    column == "Sex"
                    and str(
                        condition
                    ).lower()
                    == "female"
                ):
                    text = "Sex = female"

                elif (
                    column == "Sex"
                    and str(
                        condition
                    ).lower()
                    == "male"
                ):
                    text = "Sex = male"

                else:
                    text = str(
                        condition
                    )

                return AIResponse(
                    success=True,
                    message=(
                        f"The condition was {text}."
                    ),
                    data={
                        "type": (
                            "previous_result_condition"
                        ),
                        "column": column,
                        "condition": condition,
                        "source_result": base,
                    },
                    agent="DataQueryAgent",
                    intent="data_question",
                )

        # ----------------------------------------------------------
        # Percentage follow-up
        # ----------------------------------------------------------

        if cls._is_percentage_followup(
            question
        ):

            value = base.get(
                "value"
            )

            if (
                value is not None
                and result_type in {
                    "percentage",
                    "filtered_percentage",
                }
            ):

                return AIResponse(
                    success=True,
                    message=(
                        f"The percentage was "
                        f"{float(value):.2f}%."
                    ),
                    data={
                        "type": "previous_percentage",
                        "column": base.get(
                            "column"
                        ),
                        "value": value,
                        "count": base.get(
                            "count"
                        ),
                        "total": base.get(
                            "total"
                        ),
                        "source_result": base,
                    },
                    agent="DataQueryAgent",
                    intent="data_question",
                )

        # ----------------------------------------------------------
        # Numerical result follow-up
        # ----------------------------------------------------------

        if result_type in {
            "average",
            "median",
            "minimum",
            "maximum",
            "total",
            "filtered_average",
            "filtered_median",
            "filtered_minimum",
            "filtered_maximum",
        }:

            if cls._is_value_followup(
                question
            ):

                value = base.get(
                    "value"
                )

                column = base.get(
                    "column"
                )

                if value is not None:

                    return AIResponse(
                        success=True,
                        message=(
                            f"The previous value for "
                            f"{column} was {value}."
                        ),
                        data={
                            "type": "previous_value",
                            "column": column,
                            "value": value,
                            "source_type": result_type,
                            "source_result": base,
                        },
                        agent="DataQueryAgent",
                        intent="data_question",
                    )

        return None

    # ==============================================================
    # FOLLOW-UP DETECTORS
    # ==============================================================

    @classmethod
    def _is_count_followup(
        cls,
        question: str,
    ) -> bool:

        q = question.lower()

        phrases = [
            "how many passengers was that",
            "how many passengers were that",
            "how many passengers was it",
            "how many passengers were it",
            "how many people was that",
            "how many people were that",
            "how many were there",
            "how many was that",
            "how many was it",
            "what was the count",
            "what was that count",
            "what is the count",
            "what's the count",
            "what was the number",
            "what was that number",
        ]

        return any(
            phrase in q
            for phrase in phrases
        )

    @classmethod
    def _is_column_followup(
        cls,
        question: str,
    ) -> bool:

        q = question.lower()

        phrases = [
            "which column was that based on",
            "what column was that based on",
            "which column was it based on",
            "what column was it based on",
            "which column was used",
            "what column was used",
            "which column did you use",
            "what column did you use",
            "which column was that",
            "what column was that",
        ]

        return any(
            phrase in q
            for phrase in phrases
        )

    @classmethod
    def _is_condition_followup(
        cls,
        question: str,
    ) -> bool:

        q = question.lower()

        phrases = [
            "what condition did you use",
            "which condition did you use",
            "what condition was used",
            "which condition was used",
            "what was the condition",
            "which was the condition",
        ]

        return any(
            phrase in q
            for phrase in phrases
        )

    @classmethod
    def _is_percentage_followup(
        cls,
        question: str,
    ) -> bool:

        q = question.lower()

        phrases = [
            "what was that percentage",
            "what was the percentage",
            "what was that percent",
            "what was the percent",
            "what percentage was that",
            "what percent was that",
        ]

        return any(
            phrase in q
            for phrase in phrases
        )

    @classmethod
    def _is_value_followup(
        cls,
        question: str,
    ) -> bool:

        q = question.lower()

        phrases = [
            "what was that value",
            "what was the value",
            "what was that result",
            "what was the result",
            "what was that number",
            "what was the number",
            "what did you calculate",
            "what did you just calculate",
            "what was the answer",
            "what was that answer",
            "what was it",
            "what was that",
        ]

        return any(
            phrase in q
            for phrase in phrases
        )

    # ==============================================================
    # CONVERSATION MEMORY
    # ==============================================================

    @classmethod
    def _get_previous_result(
        cls,
        conversation_history: Optional[
            list[dict[str, Any]]
        ],
    ) -> Optional[dict[str, Any]]:

        if not conversation_history:
            return None

        for message in reversed(
            conversation_history
        ):

            if not isinstance(
                message,
                dict,
            ):
                continue

            if message.get(
                "role"
            ) != "assistant":
                continue

            content = message.get(
                "content"
            )

            if isinstance(
                content,
                dict,
            ):

                data = content.get(
                    "data"
                )

                if (
                    isinstance(
                        data,
                        dict,
                    )
                    and data.get(
                        "type"
                    )
                ):
                    return data

                if content.get(
                    "type"
                ):
                    return content

            data = message.get(
                "data"
            )

            if (
                isinstance(
                    data,
                    dict,
                )
                and data.get(
                    "type"
                )
            ):
                return data

        return None

    # ==============================================================
    # COLUMN HELPERS
    # ==============================================================

    @classmethod
    def _find_column(
        cls,
        dataset: pd.DataFrame,
        target: str,
    ) -> Optional[str]:

        target = cls._normalize_column_name(
            target
        )

        for column in dataset.columns:

            if (
                cls._normalize_column_name(
                    str(column)
                )
                == target
            ):
                return str(column)

        return None

    @classmethod
    def _extract_column_from_question(
        cls,
        dataset: pd.DataFrame,
        question: str,
        numerical_only: bool = False,
    ) -> Optional[str]:

        q = question.lower()

        candidates = []

        for column in dataset.columns:

            column_name = str(column)

            if (
                numerical_only
                and not pd.api.types.is_numeric_dtype(
                    dataset[column]
                )
            ):
                continue

            candidates.append(
                column_name
            )

        # ----------------------------------------------------------
        # Exact column names
        # ----------------------------------------------------------

        for column in sorted(
            candidates,
            key=len,
            reverse=True,
        ):

            if column.lower() in q:
                return column

        # ----------------------------------------------------------
        # Aliases
        # ----------------------------------------------------------

        aliases = {
            "passengerid": [
                "passenger id",
                "passengerid",
                "id",
            ],
            "survived": [
                "survived",
                "survival",
                "survival status",
            ],
            "pclass": [
                "pclass",
                "passenger class",
                "class",
            ],
            "name": [
                "name",
                "passenger name",
            ],
            "sex": [
                "sex",
                "gender",
            ],
            "age": [
                "age",
                "ages",
            ],
            "sibsp": [
                "sibsp",
                "siblings",
                "siblings/spouses",
                "siblings and spouses",
            ],
            "parch": [
                "parch",
                "parents",
                "parents/children",
                "parents and children",
            ],
            "ticket": [
                "ticket",
                "ticket number",
            ],
            "fare": [
                "fare",
                "ticket fare",
                "price",
            ],
            "cabin": [
                "cabin",
            ],
            "embarked": [
                "embarked",
                "embarkation",
                "port",
            ],
        }

        for column in candidates:

            normalized = cls._normalize_column_name(
                column
            )

            if normalized not in aliases:
                continue

            for alias in aliases[
                normalized
            ]:

                if alias in q:
                    return column

        return None

    @classmethod
    def _normalize_column_name(
        cls,
        column: str,
    ) -> str:

        return re.sub(
            r"[^a-z0-9]",
            "",
            str(column).lower(),
        )

    # ==============================================================
    # GENERAL HELPERS
    # ==============================================================

    @classmethod
    def _contains_any(
        cls,
        text: str,
        phrases: list[str],
    ) -> bool:

        text = text.lower()

        return any(
            phrase.lower() in text
            for phrase in phrases
        )

    @classmethod
    def _binary_count(
        cls,
        series: pd.Series,
        target: int,
    ) -> int:

        values = pd.to_numeric(
            series,
            errors="coerce",
        )

        return int(
            values.eq(
                target
            ).sum()
        )