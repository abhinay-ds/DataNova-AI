from email.mime import message
import json
import re

from app.prompts.planner_prompt import (
    PLANNER_SYSTEM_PROMPT,
)

from app.schemas.planner import PlannerResponse

from app.services.llm_service import LLMService


class PlannerService:

    # =========================================================
    # Code extraction helper
    # =========================================================

    @classmethod
    def _extract_code_from_message(
        cls,
        message: str,
    ) -> str:
        """
        Extract code from a user message.
        Supports markdown code blocks and plain code.
        """

        if not message:
            return ""

        # Extract code inside markdown code blocks
        match = re.search(
            r"```(?:python|sql|java|javascript|cpp|c\+\+)?\s*(.*?)```",
            message,
            re.DOTALL | re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

        # Remove common instruction prefixes
        cleaned = re.sub(
            r"^(explain|debug|optimize|fix|convert)\s+(this\s+)?code\s*:?\s*",
            "",
            message.strip(),
            flags=re.IGNORECASE,
        )

        return cleaned.strip()

    # =========================================================
    # Deterministic planner
    # =========================================================

    @classmethod
    def _deterministic_plan(
        cls,
        message: str,
    ):

        text = message.strip().lower()

        # -----------------------------------------------------
        # Dataset analysis
        # -----------------------------------------------------

        analysis_phrases = [
            "analyze the uploaded dataset",
            "analyze uploaded dataset",
            "analyze this dataset",
            "analyze the dataset",
            "analyse the uploaded dataset",
            "analyse uploaded dataset",
            "analyse this dataset",
            "analyse the dataset",
            "perform eda",
            "explore the dataset",
            "dataset analysis",
        ]

        if any(
            phrase in text
            for phrase in analysis_phrases
        ):

            explicit_extra = any(
                keyword in text
                for keyword in [
                    "visualization",
                    "visualisations",
                    "visualizations",
                    "chart",
                    "plot",
                    "model",
                    "predict",
                    "report",
                    "python",
                    "sql",
                ]
            )

            if not explicit_extra:

                return {
                    "objective": "Analyze the uploaded dataset",
                    "tasks": [
                        {
                            "capability": "analyze_dataset",
                            "action": "Perform complete dataset analysis",
                            "priority": "HIGH",
                            "input_data": {},
                        }
                    ],
                }

        # -----------------------------------------------------
        # Scatter
        # -----------------------------------------------------

        if "scatter plot" in text:

            x, y = cls._extract_two_columns(
                message
            )

            return {
                "objective": "Create a scatter plot",
                "tasks": [
                    {
                        "capability": "scatter",
                        "action": "Create scatter plot",
                        "priority": "HIGH",
                        "input_data": {
                            "x": x,
                            "y": y,
                        },
                    }
                ],
            }

        # -----------------------------------------------------
        # Histogram
        # -----------------------------------------------------

        if "histogram" in text:

            column = cls._extract_single_column(
                message
            )

            return {
                "objective": "Create a histogram",
                "tasks": [
                    {
                        "capability": "histogram",
                        "action": "Create histogram",
                        "priority": "HIGH",
                        "input_data": {
                            "column": column,
                        },
                    }
                ],
            }

        # -----------------------------------------------------
        # Boxplot
        # -----------------------------------------------------

        if (
            "boxplot" in text
            or "box plot" in text
        ):

            x, y = cls._extract_two_columns(
                message
            )

            input_data = {}

            if x:
                input_data["column"] = x

            if y:
                input_data["group_by"] = y

            return {
                "objective": "Create a boxplot",
                "tasks": [
                    {
                        "capability": "boxplot",
                        "action": "Create boxplot",
                        "priority": "HIGH",
                        "input_data": input_data,
                    }
                ],
            }

        # -----------------------------------------------------
        # Correlation heatmap
        # -----------------------------------------------------

        if (
            "correlation heatmap" in text
            or "correlation matrix" in text
            or (
                "correlation" in text
                and "heatmap" in text
            )
        ):

            return {
                "objective": "Create a correlation heatmap",
                "tasks": [
                    {
                        "capability": "correlation",
                        "action": "Calculate correlation matrix",
                        "priority": "HIGH",
                        "input_data": {},
                    },
                    {
                        "capability": "heatmap",
                        "action": "Create correlation heatmap",
                        "priority": "HIGH",
                        "input_data": {},
                    },
                ],
            }

        # -----------------------------------------------------
        # Bar chart
        # -----------------------------------------------------

        if "bar chart" in text:

            x, y = cls._extract_two_columns(
                message
            )

            return {
                "objective": "Create a bar chart",
                "tasks": [
                    {
                        "capability": "bar_chart",
                        "action": "Create bar chart",
                        "priority": "HIGH",
                        "input_data": {
                            "x": x,
                            "y": y,
                        },
                    }
                ],
            }

        # -----------------------------------------------------
        # Line chart
        # -----------------------------------------------------

        if (
            "line chart" in text
            or "line graph" in text
        ):

            x, y = cls._extract_two_columns(
                message
            )

            return {
                "objective": "Create a line chart",
                "tasks": [
                    {
                        "capability": "line_chart",
                        "action": "Create line chart",
                        "priority": "HIGH",
                        "input_data": {
                            "x": x,
                            "y": y,
                        },
                    }
                ],
            }

        # -----------------------------------------------------
        # Pie chart
        # -----------------------------------------------------

        if "pie chart" in text:

            column = cls._extract_single_column(
                message
            )

            return {
                "objective": "Create a pie chart",
                "tasks": [
                    {
                        "capability": "pie_chart",
                        "action": "Create pie chart",
                        "priority": "HIGH",
                        "input_data": {
                            "column": column,
                        },
                    }
                ],
            }

        # -----------------------------------------------------
        # ML training
        # -----------------------------------------------------

        if (
            "train a machine learning model"
            in text
            or "train a model"
            in text
            or "build a machine learning model"
            in text
            or "build a model"
            in text
        ):

            target = cls._extract_target(
                message
            )

            return {
                "objective": "Train a machine learning model",
                "tasks": [
                    {
                        "capability": "train_model",
                        "action": "Train machine learning model",
                        "priority": "HIGH",
                        "input_data": {
                            "target": target,
                        },
                    }
                ],
            }

        # -----------------------------------------------------
        # Evaluation
        # -----------------------------------------------------

        if (
            "evaluate the model" in text
            or "evaluate model" in text
            or "model performance" in text
            or "model metrics" in text
        ):

            return {
                "objective": "Evaluate the trained model",
                "tasks": [
                    {
                        "capability": "evaluate_model",
                        "action": "Evaluate model performance",
                        "priority": "HIGH",
                        "input_data": {},
                    }
                ],
            }

        # -----------------------------------------------------
        # Report
        # -----------------------------------------------------

        if (
            "generate a report" in text
            or "generate report" in text
            or "create a report" in text
            or "create report" in text
        ):

            return {
                "objective": "Generate a report",
                "tasks": [
                    {
                        "capability": "generate_report",
                        "action": "Generate report",
                        "priority": "HIGH",
                        "input_data": {},
                    }
                ],
            }

        # -----------------------------------------------------
        # SQL Code Generation
        # -----------------------------------------------------

        sql_phrases = [
            "generate sql",
            "generate sql code",
            "write sql",
            "create sql",
            "sql query",
            "sql code",
            "select all",
            "retrieve all",
            "retrieve",
            "select passengers",
        ]

        if any(
            phrase in text
            for phrase in sql_phrases
        ):

            return {
                "objective": "Generate SQL code",
                "tasks": [
                    {
                        "capability": "generate_sql",
                        "action": "Generate SQL query",
                        "priority": "HIGH",
                        "input_data": {
                            "prompt": message,
                        },
                    }
                ],
            }

        # -----------------------------------------------------
        # Python Code Generation
        # -----------------------------------------------------

        python_phrases = [
            "generate python",
            "generate python code",
            "write python",
            "write python code",
            "create python code",
            "python code",
            "python script",
        ]

        if any(
            phrase in text
            for phrase in python_phrases
        ):

            return {
                "objective": "Generate Python code",
                "tasks": [
                    {
                        "capability": "generate_python",
                        "action": "Generate Python code",
                        "priority": "HIGH",
                        "input_data": {
                            "prompt": message,
                        },
                    }
                ],
            }

        # -----------------------------------------------------
        # Explain Code
        # -----------------------------------------------------

        explain_phrases = [
            "explain this code",
            "explain the code",
            "explain code",
            "what does this code do",
            "how does this code work",
        ]

        if any(
            phrase in text
            for phrase in explain_phrases
        ):

            return {
                "objective": "Explain code",
                "tasks": [
                    {
                        "capability": "explain_code",
                        "action": "Explain the supplied code",
                        "priority": "HIGH",
                        "input_data": {
                            "code": cls._extract_code_from_message(
                                message
                            ),
                        },
                    }
                ],
            }

        # -----------------------------------------------------
        # Optimize Code
        # -----------------------------------------------------

        optimize_phrases = [
            "optimize this code",
            "optimize code",
            "improve this code",
            "make this code faster",
            "make the code faster",
        ]

        if any(
            phrase in text
            for phrase in optimize_phrases
        ):

            return {
                "objective": "Optimize code",
                "tasks": [
                    {
                        "capability": "optimize_code",
                        "action": "Optimize the supplied code",
                        "priority": "HIGH",
                        "input_data": {
                            "code": cls._extract_code_from_message(
                                message
                            ),
                        },
                    }
                ],
            }

        # -----------------------------------------------------
        # Debug Code
        # -----------------------------------------------------

        debug_phrases = [
            "debug this code",
            "debug code",
            "fix this code",
            "find the error",
            "find errors",
            "fix the error",
            "fix errors",
        ]

        if any(
            phrase in text
            for phrase in debug_phrases
        ):

            return {
                "objective": "Debug code",
                "tasks": [
                    {
                        "capability": "debug_code",
                        "action": "Debug the supplied code",
                        "priority": "HIGH",
                        "input_data": {
                            "code": cls._extract_code_from_message(
                                message
                            ),
                        },
                    }
                ],
            }

                # -----------------------------------------------------
        # Convert Code
        # -----------------------------------------------------

        convert_phrases = [
            "convert this code",
            "convert code",
            "convert python to java",
            "convert python to c++",
            "convert java to python",
            "convert c++ to python",
        ]

        if any(
            phrase in text
            for phrase in convert_phrases
        ):

            target_language = None

            # Detect target language
            match = re.search(
                r"\bto\s+(python|java|javascript|c\+\+|cpp|c#|sql)\b",
                message,
                re.IGNORECASE,
            )

            if match:

                target_language = (
                    match.group(1)
                    .strip()
                    .lower()
                )

                if target_language == "cpp":
                    target_language = "c++"

            return {
                "objective": "Convert code",
                "tasks": [
                    {
                        "capability": "convert_code",
                        "action": "Convert the supplied code",
                        "priority": "HIGH",
                        "input_data": {
                            "code": cls._extract_code_from_message(
                                message
                            ),
                            "target_language": target_language,
                        },
                    }
                ],
            }
        # -----------------------------------------------------
        # Nothing deterministic
        # -----------------------------------------------------

        return None

    # =========================================================
    # Helpers
    # =========================================================

    @staticmethod
    def _extract_two_columns(
        message: str,
    ):

        match = re.search(
            r"(?:using|between|of)\s+([A-Za-z_][\w]*)\s+(?:and|vs\.?|versus)\s+([A-Za-z_][\w]*)",
            message,
            re.IGNORECASE,
        )

        if match:
            return (
                match.group(1),
                match.group(2),
            )

        return (
            None,
            None,
        )

    @staticmethod
    def _extract_single_column(
        message: str,
    ):

        patterns = [
            r"(?:of|using|for)\s+([A-Za-z_][\w]*)",
            r"(?:column)\s+([A-Za-z_][\w]*)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                message,
                re.IGNORECASE,
            )

            if match:
                return match.group(1)

        return None

    @staticmethod
    def _extract_target(
        message: str,
    ):

        patterns = [
            r"predict\s+([A-Za-z_][\w]*)",
            r"target\s+(?:is|=)?\s*([A-Za-z_][\w]*)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                message,
                re.IGNORECASE,
            )

            if match:
                return match.group(1)

        return None

    # =========================================================
    # Groq fallback planner
    # =========================================================

    @classmethod
    def _llm_plan(
        cls,
        message: str,
    ):

        prompt = f"""
{PLANNER_SYSTEM_PROMPT}

USER REQUEST:

{message}

IMPORTANT:

Return ONLY valid JSON.

Create the smallest possible task list.

Do not add tasks that were not requested.

Do not automatically add visualizations.

Do not automatically add analysis.

Do not automatically add evaluation.

Do not automatically add reports.
"""

        response = LLMService.generate(
            prompt
        )

        if not response.success:

            raise Exception(
                response.message
            )

        raw = (
            response.data
            .strip()
        )

        # Remove accidental markdown fences
        if raw.startswith("```"):

            raw = (
                raw
                .replace(
                    "```json",
                    "",
                )
                .replace(
                    "```",
                    "",
                )
                .strip()
            )

        try:

            data = json.loads(
                raw
            )

        except json.JSONDecodeError as e:

            raise ValueError(
                "Planner returned invalid JSON: "
                f"{e}"
            )

        return data

    # =========================================================
    # Public planner
    # =========================================================

    @classmethod
    def create_plan(
        cls,
        message: str,
    ) -> PlannerResponse:

        # -----------------------------------------------------
        # First try deterministic planning
        # -----------------------------------------------------

        deterministic = (
            cls._deterministic_plan(
                message
            )
        )

        if deterministic is not None:

            return PlannerResponse.model_validate(
                deterministic
            )

        # -----------------------------------------------------
        # Otherwise use Groq
        # -----------------------------------------------------

        llm_plan = cls._llm_plan(
            message
        )

        return PlannerResponse.model_validate(
            llm_plan
        )