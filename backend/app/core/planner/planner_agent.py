from __future__ import annotations

import json
import re
import uuid

import pandas as pd

from app.services.agents.base_agent import BaseAgent

from app.core.ai_engine.context import AIContext
from app.core.execution.ai_task import AITask
from app.core.execution.task_priority import TaskPriority
from app.core.execution.task_status import TaskStatus
from app.core.planner.execution_plan import ExecutionPlan

from app.schemas.planner import (
    PlannerResponse,
    PlannedTask,
)

from app.services.llm_service import LLMService


class PlannerAgent(BaseAgent):
    """
    Converts a user request into an executable DataNova AI plan.

    Important:
    Conversational follow-up questions are detected locally instead
    of relying entirely on the LLM planner. This guarantees that
    questions referring to the previous calculation are routed to
    DataQueryAgent.
    """

    # =========================================================
    # BASIC AGENT INFORMATION
    # =========================================================

    @property
    def name(self) -> str:
        return "PlannerAgent"

    @property
    def capabilities(self) -> list[str]:
        return ["planning"]

    # =========================================================
    # MAIN EXECUTION
    # =========================================================

    async def execute(
        self,
        context: AIContext,
    ) -> ExecutionPlan:

        # =====================================================
        # CAPABILITY REGISTRY
        # =====================================================

        if context.capability_registry is None:
            from app.core.registry.capability_loader import load_capabilities
            context.capability_registry = load_capabilities()

        capabilities = (
            context.capability_registry.list_capabilities()
        )

        # =====================================================
        # DATASET INFORMATION
        # =====================================================

        dataset_info = "No dataset uploaded."

        if context.dataset is not None:

            dataset_info = f"""
Dataset columns:

{", ".join(
    str(column)
    for column in context.dataset.columns
)}

Rows: {len(context.dataset)}

Columns: {len(context.dataset.columns)}
"""

        # =====================================================
        # MESSAGE
        # =====================================================

        message = (
            context.message or ""
        ).strip()

        normalized_message = (
            re.sub(
                r"\s+",
                " ",
                message.lower()
            )
            .strip()
        )

        # =====================================================
        # REQUEST CLASSIFICATION
        # =====================================================

        previous_result_requested = (
            self._is_previous_result_question(
                normalized_message
            )
        )

        data_question_requested = (
            self._is_data_question(
                normalized_message
            )
            or previous_result_requested
        )

        analysis_requested = (
            self._is_analysis_question(
                normalized_message
            )
        )

        ml_requested = (
            self._is_ml_question(
                normalized_message
            )
        )

        visualization_requested = (
            self._is_visualization_question(
                normalized_message
            )
        )

        report_requested = (
            self._is_report_question(
                normalized_message
            )
        )

        # =====================================================
        # IMPORTANT:
        # DETERMINISTIC FOLLOW-UP ROUTING
        # =====================================================
        #
        # If the user refers to something calculated previously,
        # DO NOT let the LLM decide whether this is a data question.
        #
        # Always create exactly one data_question task.
        #
        # Examples:
        #
        #   What was that value?
        #   What did you calculate?
        #   Which column was that based on?
        #   What condition did you use?
        #   How many were there?
        #
        # DataQueryService will use conversation history to recover
        # the previous result.

        if previous_result_requested:

            return self._build_data_question_plan(
                context=context,
                objective=(
                    "Answer the user's follow-up "
                    "using the previous dataset calculation"
                ),
            )

        # =====================================================
        # DETERMINISTIC SMART VISUALIZATION ROUTING
        # =====================================================
        # Requests such as:
        #
        #   Show survival across passenger classes
        #   Compare survival by gender
        #   Show average fare by passenger class
        #
        # are handled locally so the LLM is not required to
        # infer chart columns and aggregation.
        # =====================================================

        if self._is_smart_visualization_question(
            normalized_message
        ):
            return self._build_smart_visualization_plan(
                context=context
            )

        # =====================================================
        # DETERMINISTIC PURE CODE GENERATION ROUTING
        # =====================================================
        # SQL, conversion, explanation, debugging, and optimization
        # requests do not require a dataset and must bypass data_question.

        pure_code = self._detect_pure_code_request(
            normalized_message,
            context.message,
        )
        if pure_code is not None:
            code_cap, code_action, code_input = pure_code
            if context.capability_registry.has_capability(code_cap):
                return ExecutionPlan(
                    objective=code_action,
                    tasks=[
                        AITask(
                            id=str(uuid.uuid4()),
                            capability=code_cap,
                            action=code_action,
                            priority=TaskPriority.HIGH,
                            status=TaskStatus.PENDING,
                            input_data=code_input,
                        )
                    ],
                )

        # =====================================================
        # DETERMINISTIC CODE GENERATION ROUTING
        # =====================================================
        # Code-generation requests must bypass the general LLM
        # planner. This prevents unrelated tasks such as
        # analyze_dataset from being added.

        if self._is_code_request(normalized_message):

            if not context.capability_registry.has_capability(
                "generate_python"
            ):
                raise ValueError(
                    "Python code generation capability "
                    "'generate_python' is not registered."
                )

            return self._build_code_generation_plan(
                context=context,
                dataset_info=dataset_info,
            )

        # =====================================================
        # DETERMINISTIC DATA QUESTION ROUTING
        # =====================================================
        # Pure dataset questions must never call the LLM.
        # This includes percentages, counts, averages, medians,
        # minimum/maximum, unique values, distributions, etc.
        # DataQueryService performs the actual calculation.
        # Follow-up questions are handled above by the same path.

        if (
            data_question_requested
            and not analysis_requested
            and not ml_requested
            and not visualization_requested
            and not report_requested
        ):
            return self._build_data_question_plan(
                context=context,
                objective=(
                    "Answer the user's dataset question directly"
                ),
            )

        # =====================================================
        # DETERMINISTIC DATASET ANALYSIS ROUTING
        # =====================================================
        # When user asks to analyze, explore, summarize, or conduct
        # EDA on the dataset without requesting ML models, charts,
        # or reports:
        # Build an analysis plan with analyze_dataset and data_analysis.
        # Guarantees:
        # 1. Grounded calculation (profiling, missing values, quality).
        # 2. Rich, intelligent data science answer answering the prompt.
        # 3. Completely bypasses LLM planner token explosion / TPM limits.

        if (
            analysis_requested
            and not ml_requested
            and not visualization_requested
            and not report_requested
        ):
            return self._build_analysis_plan(
                context=context,
                objective=(
                    "Perform comprehensive dataset analysis and answer questions"
                ),
            )

        # =====================================================
        # PLANNER PROMPT
        # =====================================================

        # Compact conversation history to prevent Groq TPM limit exhaustion
        compact_history = []
        for item in (context.conversation_history or [])[-5:]:
            if isinstance(item, dict):
                role = item.get("role", "user")
                content = item.get("content", "")
                if isinstance(content, dict):
                    content = content.get("message") or content.get("answer") or ""
                content_str = str(content).strip()
                if len(content_str) > 250:
                    content_str = content_str[:250] + "..."
                if content_str:
                    compact_history.append({"role": role, "content": content_str})

        prompt = f"""
You are the planning engine of DataNova AI.

Your job is to convert the user's request into a sequence
of executable tasks.

AVAILABLE CAPABILITIES:

{json.dumps(
    capabilities,
    indent=2,
    default=str
)}

DATASET INFORMATION:

{dataset_info}

USER REQUEST:

{context.message}

CONVERSATION HISTORY:

{json.dumps(
    compact_history,
    indent=2,
    default=str
)}

RULES:

1. Only use capabilities from the available capability list.

2. Never invent a capability.

3. Create only the tasks necessary to satisfy the request.

4. Put tasks in logical execution order.

5. Use HIGH priority for core analysis and machine learning tasks.

6. Use MEDIUM priority for visualization and report tasks.

7. Use LOW priority for optional tasks.

8. If a dataset is required but unavailable,
   still create the appropriate task.

9. If the user asks to explain, describe, summarize,
   analyze, explore, or give an overview of an uploaded
   dataset, use analyze_dataset.

10. If train_model is selected, evaluate_model MUST
    be executed after training.

11. Do NOT add analyze_dataset before train_model unless
    the user explicitly asks for dataset analysis.

12. Do NOT add analyze_dataset before visualization tasks
    unless the user explicitly asks for dataset analysis.

13. Do NOT add generate_report unless the user explicitly
    asks for a report.

14. For histogram and boxplot, identify the requested column.

15. For scatter, identify x and y columns when possible.

16. For bar_chart, identify x and y columns when possible.

17. For line_chart, identify x and y columns when possible.

18. For pie_chart, identify the requested categorical column.

19. For correlation and heatmap, use numerical columns
    when appropriate.

20. For percentage, proportion, or share requests involving
    one categorical column, use pie_chart and use that column
    as the pie chart column. Do NOT invent a numerical y-axis.

21. Requests asking for distribution, count, or frequency
    as TEXT are DATA QUESTIONS.

    Examples:

    "What is the distribution of Sex?"
    -> data_question

    "Give me the frequency of Sex"
    -> data_question

    "Create a bar chart showing the distribution of Sex"
    -> bar_chart

    "Plot the distribution of Sex"
    -> bar_chart

22. Requests asking about a relationship between two numerical
    columns should use scatter.

    Example:

    "What is the relationship between Age and Fare?"
    -> scatter

    Use Age as x and Fare as y.

    Do NOT add correlation unless the user explicitly asks
    for correlation or a correlation matrix.

23. Requests asking for a previous calculation, previous result,
    recently calculated value, or a value calculated immediately
    before are DATA QUESTIONS.

    Examples:

    "What was the value you just calculated?"
    -> data_question

    "What was the previous result?"
    -> data_question

    "What did you calculate?"
    -> data_question

    "What did you just calculate?"
    -> data_question

    "What was that value?"
    -> data_question

    "What was that?"
    -> data_question

    "What was the result?"
    -> data_question

    "What column did you calculate it for?"
    -> data_question

    "Which column was that based on?"
    -> data_question

    "What condition did you use?"
    -> data_question

    "How many were there?"
    -> data_question

24. For generate_python, input_data MUST contain:

{{
    "prompt": "complete description of the Python code to generate"
}}

25. For generate_sql, input_data MUST contain:

{{
    "prompt": "complete description of the SQL to generate"
}}

26. Every task MUST contain an action.

27. Return ONLY valid JSON.

The response MUST have this structure:

{{
    "objective": "string",
    "tasks": [
        {{
            "capability": "string",
            "action": "string",
            "priority": "HIGH",
            "input_data": {{}}
        }}
    ]
}}

Return ONLY JSON.
"""

        # =====================================================
        # CALL LLM
        # =====================================================

        response = LLMService.generate(
            prompt
        )

        if not response.success:
            raise RuntimeError(
                response.message
            )

        # =====================================================
        # PARSE JSON
        # =====================================================

        raw = (
            response.data or ""
        ).strip()

        # Remove markdown code fences if present.

        if raw.startswith("```"):

            raw = re.sub(
                r"^```(?:json)?\s*",
                "",
                raw,
                flags=re.IGNORECASE
            )

            raw = re.sub(
                r"\s*```$",
                "",
                raw
            ).strip()

        try:

            planner_data = json.loads(
                raw
            )

        except json.JSONDecodeError as e:

            raise ValueError(
                f"Planner returned invalid JSON: {e}\n"
                f"Response: {raw}"
            )

        # =====================================================
        # VALIDATE PLANNER RESPONSE
        # =====================================================

        try:

            planner_response = PlannerResponse(
                **planner_data
            )

        except Exception as e:

            raise ValueError(
                f"Invalid planner response: {e}"
            )

        # =====================================================
        # SAFETY:
        # DATA QUESTION OVERRIDE
        # =====================================================
        #
        # Non-follow-up data questions can still be corrected
        # if the LLM forgets to create a data_question task.
        #
        # This is especially useful for:
        #
        #   How many passengers are there?
        #   What is the average Age?
        #   What is the distribution of Sex?
        #
        # We do NOT override analysis/ML/visualization/report
        # requests.

        has_data_question_task = any(
            (
                task.capability or ""
            ).strip() == "data_question"
            for task in planner_response.tasks
        )

        if (
            data_question_requested
            and not analysis_requested
            and not ml_requested
            and not visualization_requested
            and not report_requested
            and not has_data_question_task
        ):

            planner_response.tasks.insert(
                0,
                PlannedTask(
                    capability="data_question",
                    action=(
                        "Answer the user's question "
                        "using the uploaded dataset"
                    ),
                    priority="HIGH",
                    input_data={
                        "question": context.message
                    },
                )
            )

        # =====================================================
        # FORCE DATASET ANALYSIS
        # =====================================================

        has_analysis_task = any(
            (
                task.capability or ""
            ).strip() == "analyze_dataset"
            for task in planner_response.tasks
        )

        if (
            analysis_requested
            and not has_analysis_task
        ):

            planner_response.tasks.insert(
                0,
                PlannedTask(
                    capability="analyze_dataset",
                    action=(
                        "Analyze and explain "
                        "the uploaded dataset"
                    ),
                    priority="HIGH",
                    input_data={},
                )
            )

        # =====================================================
        # FORCE MODEL EVALUATION
        # =====================================================

        has_train_task = any(
            (
                task.capability or ""
            ).strip() == "train_model"
            for task in planner_response.tasks
        )

        has_evaluation_task = any(
            (
                task.capability or ""
            ).strip() == "evaluate_model"
            for task in planner_response.tasks
        )

        if (
            has_train_task
            and not has_evaluation_task
        ):

            planner_response.tasks.append(
                PlannedTask(
                    capability="evaluate_model",
                    action=(
                        "Evaluate the trained "
                        "machine learning model"
                    ),
                    priority="HIGH",
                    input_data={},
                )
            )

        # =====================================================
        # REMOVE UNREQUESTED ANALYSIS
        # =====================================================

        if (
            not analysis_requested
            and (
                data_question_requested
                or ml_requested
                or visualization_requested
                or report_requested
            )
        ):

            planner_response.tasks = [
                task
                for task in planner_response.tasks
                if (
                    task.capability or ""
                ).strip()
                != "analyze_dataset"
            ]

        # =====================================================
        # ENSURE DATA QUESTION INPUT
        # =====================================================

        for task in planner_response.tasks:

            if (
                task.capability or ""
            ).strip() == "data_question":

                existing_input = (
                    task.input_data
                    if isinstance(
                        task.input_data,
                        dict
                    )
                    else {}
                )

                task.input_data = {
                    **existing_input,
                    "question": context.message,
                }

        # =====================================================
        # CONVERT PlannedTask -> AITask
        # =====================================================

        final_tasks = []

        for task in planner_response.tasks:

            capability = (
                task.capability
                if task.capability
                else ""
            ).strip()

            if not capability:
                continue

            action = (
                task.action
                if task.action
                else self.default_action(
                    capability
                )
            )

            priority = self.get_priority(
                task.priority
            )

            input_data = (
                task.input_data
                if isinstance(
                    task.input_data,
                    dict
                )
                else {}
            )

            final_tasks.append(
                AITask(
                    id=str(
                        uuid.uuid4()
                    ),
                    capability=capability,
                    action=action,
                    status=TaskStatus.PENDING,
                    priority=priority,
                    dependencies=[],
                    input_data=input_data,
                    output_data={},
                )
            )

        # =====================================================
        # RETURN EXECUTION PLAN
        # =====================================================

        return ExecutionPlan(
            objective=(
                planner_response.objective
                or "Execute the user's request"
            ),
            tasks=final_tasks,
        )

    # =========================================================
    # PURE CODE REQUEST DETECTION
    # =========================================================

    @staticmethod
    def _detect_pure_code_request(
        normalized_message: str,
        original_message: str | None = None,
    ) -> tuple[str, str, dict] | None:
        """
        Detect pure code-generation requests that do not require a dataset:
        Returns (capability, action, input_data) or None.
        """
        raw = original_message or normalized_message or ""
        lower = (normalized_message or "").lower().strip()

        # 1. SQL Generation
        sql_keywords = [
            "generate sql", "write sql", "create sql", "give me sql",
            "show me sql", "sql to calculate", "sql query", "sql code",
        ]
        if any(kw in lower for kw in sql_keywords) or lower.startswith("select ") or re.search(r"\bgenerate\s+sql\b", lower):
            return (
                "generate_sql",
                "Generate SQL query based on user request",
                {"prompt": raw, "query": raw},
            )

        # 2. Code Conversion
        if (
            "convert this python code to" in lower
            or "convert python code to" in lower
            or "convert this code to" in lower
            or "convert to javascript" in lower
            or "convert to python" in lower
            or lower.startswith("convert this")
            or re.search(r"\bconvert\s+(?:this\s+)?(?:.+?\s+)?code\s+to\s+([a-zA-Z\+#]+)", lower)
        ):
            target_lang = "JavaScript"
            lang_match = re.search(r"\bto\s+([a-zA-Z\+#]+)", lower)
            if lang_match:
                matched = lang_match.group(1).lower()
                lang_names = {
                    "javascript": "JavaScript", "js": "JavaScript", "python": "Python",
                    "py": "Python", "typescript": "TypeScript", "ts": "TypeScript",
                    "c++": "C++", "cpp": "C++", "java": "Java", "c#": "C#", "go": "Go",
                    "rust": "Rust", "sql": "SQL", "r": "R"
                }
                target_lang = lang_names.get(matched, matched.title())
            return (
                "convert_code",
                f"Convert code to {target_lang}",
                {"code": raw, "target_language": target_lang},
            )

        # 3. Explain Code
        explain_keywords = [
            "explain this python code", "explain this code", "explain the code",
            "explain python code", "break down this code",
        ]
        if any(kw in lower for kw in explain_keywords) or lower.startswith("explain this"):
            return (
                "explain_code",
                "Explain the provided code",
                {"code": raw},
            )

        # 4. Debug Code
        debug_keywords = [
            "debug this python code", "debug this code", "debug the code",
            "debug python code", "fix this python code", "fix this code",
            "the error is:", "indexerror:", "syntaxerror:", "typeerror:",
            "fix the error",
        ]
        if any(kw in lower for kw in debug_keywords) or lower.startswith("debug this"):
            return (
                "debug_code",
                "Debug and fix the provided code",
                {"code": raw},
            )

        # 5. Optimize Code
        optimize_keywords = [
            "optimize this python code", "optimize this code", "optimize the code",
            "speed up this code", "improve this python code", "optimize code",
        ]
        if any(kw in lower for kw in optimize_keywords) or lower.startswith("optimize this"):
            return (
                "optimize_code",
                "Optimize the provided code",
                {"code": raw},
            )

        return None

    # =========================================================
    # CODE REQUEST DETECTION
    # =========================================================

    @staticmethod
    def _is_code_request(
        message: str,
    ) -> bool:
        """Detect explicit requests for Python code generation."""

        text = (message or "").lower().strip()

        if not text:
            return False

        code_phrases = [
            "generate python code",
            "generate python",
            "write python code",
            "write python",
            "show python code",
            "show me python code",
            "give me python code",
            "give me the python code",
            "python code for",
            "python code used",
            "code used for this analysis",
            "code used for this",
            "code for this analysis",
            "show me the code",
            "show the code",
            "give me the code",
        ]

        return any(
            phrase in text
            for phrase in code_phrases
        )

    # =========================================================
    # CODE GENERATION PLAN
    # =========================================================

    @staticmethod
    def _build_code_generation_plan(
        context: AIContext,
        dataset_info: str,
    ) -> ExecutionPlan:
        """Build exactly one generate_python task."""

        history = context.conversation_history or []

        history_text = json.dumps(
            history,
            indent=2,
            default=str,
        )

        prompt = f"""
Generate Python code for the user's request.

USER REQUEST:
{context.message}

DATASET INFORMATION:
{dataset_info}

RECENT CONVERSATION HISTORY:
{history_text}

IMPORTANT:

1. Generate code for the EXACT operation requested.

2. If the user asks for the Python code used for a previous
   analysis, calculation, or chart, identify the immediately
   preceding operation from the conversation history and
   generate code that reproduces THAT operation.

3. Do NOT generate a generic exploratory data analysis script
   unless the user explicitly asks for EDA.

4. Do NOT generate machine-learning code unless the user
   explicitly asks for machine learning.

5. Do NOT generate unrelated histograms, boxplots, regression
   models, classification models, or heatmaps.

6. Use only actual dataset columns supplied above or explicitly
   present in the conversation history. Never invent columns.

7. Assume the uploaded dataset is already available as a
   pandas DataFrame named `df`.

8. Include only imports required for the requested operation.

9. Return executable Python code focused on the requested task.

10. If the previous operation was an average, count, median,
    minimum, maximum, total, filter, or grouped calculation,
    reproduce that exact calculation rather than performing
    a full dataset analysis.
"""

        task = AITask(
            id=str(uuid.uuid4()),
            capability="generate_python",
            action=(
                "Generate Python code for the user's "
                "requested operation"
            ),
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            dependencies=[],
            input_data={
                "prompt": prompt,
            },
            output_data={},
        )

        return ExecutionPlan(
            objective="Generate Python code for the requested analysis",
            tasks=[task],
        )

    # =========================================================
    # NEGATION HANDLING HELPER
    # =========================================================

    @staticmethod
    def _strip_negated_clauses(message: str) -> str:
        """
        Removes negated/exclusion clauses from the message so that phrases
        like 'do not train models, generate charts, or create reports'
        do not falsely trigger ML, chart, or report flags.
        """
        pattern = r"\b(?:do\s+not|don'?t|no|never|without|stop|skip|avoid)\b[^.?!;]*"
        return re.sub(pattern, "", message or "", flags=re.IGNORECASE)

    # =========================================================
    # SMART VISUALIZATION DETECTION
    # =========================================================

    @classmethod
    def _is_smart_visualization_question(
        cls,
        message: str,
    ) -> bool:
        """
        Detect natural-language visualization requests that require
        grouping and aggregation rather than a raw chart.

        Examples:
            Show survival across passenger classes
            Compare survival by gender
            Show average fare by passenger class
            Display passenger count by embarked port
        """

        message = (
            message or ""
        ).lower().strip()

        positive_message = cls._strip_negated_clauses(message)

        visualization_phrases = [
            "show",
            "display",
            "visualize",
            "plot",
            "graph",
            "chart",
            "compare",
        ]

        grouping_phrases = [
            " by ",
            " across ",
            " per ",
            " for each ",
            "for every ",
            "among ",
        ]

        aggregation_phrases = [
            "average",
            "avg",
            "mean",
            "total",
            "sum",
            "median",
            "count",
            "number",
            "rate",
            "percentage",
            "percent",
            "proportion",
        ]

        has_visualization = any(
            phrase in positive_message
            for phrase in visualization_phrases
        )

        has_grouping = any(
            phrase in f" {positive_message} "
            for phrase in grouping_phrases
        )

        has_aggregation = any(
            phrase in positive_message
            for phrase in aggregation_phrases
        )

        # "Show survival across passenger classes" does not
        # explicitly say "rate", but the binary Survived metric
        # should still be aggregated by the requested group.
        if (
            has_visualization
            and has_grouping
        ):
            return True

        return (
            has_visualization
            and has_aggregation
            and has_grouping
        )

    # =========================================================
    # SMART VISUALIZATION PLAN
    # =========================================================

    def _build_smart_visualization_plan(
        self,
        context: AIContext,
    ) -> ExecutionPlan:
        """
        Build a deterministic smart_chart task.

        The planner identifies:
            x            -> grouping column
            y            -> metric column
            aggregation  -> mean/sum/count/median/min/max
            chart_type   -> bar/line
        """

        dataset = context.dataset

        if dataset is None:
            task = AITask(
                id=str(uuid.uuid4()),
                capability="smart_chart",
                action="Generate a smart chart from the uploaded dataset",
                status=TaskStatus.PENDING,
                priority=TaskPriority.HIGH,
                dependencies=[],
                input_data={},
                output_data={},
            )

            return ExecutionPlan(
                objective="Generate the requested smart visualization",
                tasks=[task],
            )

        question = (
            context.message or ""
        ).lower().strip()

        columns = list(dataset.columns)

        x = self._find_smart_chart_column(
            question=question,
            columns=columns,
            role="group",
        )

        y = self._find_smart_chart_column(
            question=question,
            columns=columns,
            role="metric",
        )

        # -----------------------------------------------------
        # Fallback grouping column
        # -----------------------------------------------------

        if x is None:
            categorical_columns = (
                dataset.select_dtypes(
                    include=[
                        "object",
                        "category",
                        "bool",
                    ]
                ).columns.tolist()
            )

            if categorical_columns:
                x = categorical_columns[0]
            else:
                numeric_columns = (
                    dataset.select_dtypes(
                        include="number"
                    ).columns.tolist()
                )

                if numeric_columns:
                    x = numeric_columns[0]

        # -----------------------------------------------------
        # Fallback metric column
        # -----------------------------------------------------

        if y is None:
            numeric_columns = (
                dataset.select_dtypes(
                    include="number"
                ).columns.tolist()
            )

            if numeric_columns:
                # Prefer a binary outcome column when present.
                binary_candidates = []

                for column in numeric_columns:
                    try:
                        values = (
                            dataset[column]
                            .dropna()
                            .unique()
                        )

                        if len(values) > 0 and set(
                            float(value)
                            for value in values
                        ).issubset({0.0, 1.0}):
                            binary_candidates.append(column)
                    except Exception:
                        continue

                if binary_candidates:
                    y = binary_candidates[0]
                else:
                    y = next(
                        (
                            column
                            for column in numeric_columns
                            if column != x
                        ),
                        numeric_columns[0],
                    )

        # -----------------------------------------------------
        # Count requests can use the grouping column itself.
        # smart_chart() performs groupby(x)[y].count().
        # -----------------------------------------------------

        aggregation = self._select_smart_aggregation(
            question=question,
            dataset=dataset,
            y=y,
        )

        if aggregation == "count" and y is None and x is not None:
            y = x

        chart_type = self._select_smart_chart_type(
            question=question,
        )

        input_data = {
            "x": x,
            "y": y,
            "aggregation": aggregation,
            "chart_type": chart_type,
        }

        task = AITask(
            id=str(uuid.uuid4()),
            capability="smart_chart",
            action=(
                f"Generate a {chart_type} chart showing "
                f"{aggregation} of {y} by {x}"
            ),
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            dependencies=[],
            input_data=input_data,
            output_data={},
        )

        return ExecutionPlan(
            objective=(
                f"Generate a {chart_type} chart showing "
                f"{aggregation} of {y} by {x}"
            ),
            tasks=[task],
        )

    # =========================================================
    # SMART CHART COLUMN SELECTION
    # =========================================================

    @staticmethod
    def _find_smart_chart_column(
        question: str,
        columns,
        role: str,
    ):
        """Find the most likely dataset column for a smart chart."""

        normalized_question = (
            re.sub(r"[^a-z0-9]+", " ", question.lower())
            .strip()
        )

        compact_question = normalized_question.replace(
            " ", ""
        )

        normalized_columns = {}

        for column in columns:
            normalized = re.sub(
                r"[^a-z0-9]+",
                "",
                str(column).lower(),
            )
            normalized_columns[normalized] = column

        # Exact dataset-column mention gets highest priority.
        exact_matches = []

        for normalized, original in normalized_columns.items():
            if normalized and normalized in compact_question:
                exact_matches.append(original)

        # Role-specific aliases.
        if role == "group":
            aliases = {
                "pclass": [
                    "pclass",
                    "passengerclass",
                    "passengerclasses",
                    "class",
                    "classes",
                ],
                "sex": [
                    "sex",
                    "gender",
                ],
                "embarked": [
                    "embarked",
                    "embarkation",
                    "embarkationport",
                    "port",
                ],
                "age": ["age", "ages"],
                "fare": [
                    "fare",
                    "fares",
                    "price",
                    "ticketprice",
                ],
                "sibsp": [
                    "sibsp",
                    "siblings",
                    "siblingsspouses",
                ],
                "parch": [
                    "parch",
                    "parents",
                    "children",
                    "parentschildren",
                ],
            }
        else:
            aliases = {
                "survived": [
                    "survived",
                    "survival",
                    "survivalrate",
                    "survivalpercentage",
                    "survivalpercent",
                ],
                "fare": [
                    "fare",
                    "fares",
                    "price",
                    "ticketprice",
                ],
                "age": ["age", "ages"],
                "pclass": [
                    "pclass",
                    "passengerclass",
                    "class",
                ],
                "sibsp": ["sibsp", "siblings"],
                "parch": [
                    "parch",
                    "parents",
                    "children",
                ],
            }

        # Prefer semantic aliases before generic exact matches such
        # as "class", because "passenger classes" should resolve to
        # Pclass on the Titanic dataset.
        for canonical, alias_list in aliases.items():
            if canonical not in normalized_columns:
                continue

            for alias in alias_list:
                normalized_alias = re.sub(
                    r"[^a-z0-9]+",
                    "",
                    alias.lower(),
                )

                if normalized_alias in compact_question:
                    return normalized_columns[canonical]

        # Exact dataset column mention fallback.
        if exact_matches:
            return exact_matches[0]

        return None

    # =========================================================
    # SMART AGGREGATION
    # =========================================================

    @staticmethod
    def _select_smart_aggregation(
        question: str,
        dataset: pd.DataFrame,
        y,
    ) -> str:

        if any(
            phrase in question
            for phrase in [
                "average",
                "avg",
                "mean",
            ]
        ):
            return "mean"

        if any(
            phrase in question
            for phrase in [
                "total",
                "sum",
            ]
        ):
            return "sum"

        if "median" in question:
            return "median"

        if any(
            phrase in question
            for phrase in [
                "minimum",
                "lowest",
                "min",
            ]
        ):
            return "min"

        if any(
            phrase in question
            for phrase in [
                "maximum",
                "highest",
                "max",
            ]
        ):
            return "max"

        if any(
            phrase in question
            for phrase in [
                "count",
                "number of",
                "number",
                "how many",
            ]
        ):
            return "count"

        # A binary metric such as Survived is naturally interpreted
        # as a rate when grouped and averaged.
        if y is not None and y in dataset.columns:
            try:
                values = (
                    dataset[y]
                    .dropna()
                    .unique()
                )

                if len(values) > 0:
                    numeric_values = set(
                        float(value)
                        for value in values
                    )

                    if numeric_values.issubset({0.0, 1.0}):
                        return "mean"
            except Exception:
                pass

        return "mean"

    # =========================================================
    # SMART CHART TYPE
    # =========================================================

    @staticmethod
    def _select_smart_chart_type(
        question: str,
    ) -> str:

        if any(
            phrase in question
            for phrase in [
                "line chart",
                "line graph",
                "trend",
                "over time",
            ]
        ):
            return "line"

        return "bar"

    # =========================================================
    # BUILD DATASET ANALYSIS PLAN
    # =========================================================

    @staticmethod
    def _build_analysis_plan(
        context: AIContext,
        objective: str = "Perform comprehensive dataset analysis and answer questions",
    ) -> ExecutionPlan:
        """
        Creates a deterministic analysis plan combining:
        1. analyze_dataset: produces structured profiling, quality metrics, and UI overview.
        2. data_analysis: produces grounded statistical insights and answers the user's prompt.
        """
        tasks = [
            AITask(
                id=str(uuid.uuid4()),
                capability="analyze_dataset",
                action="Analyze dataset structure, data types, missing values, and descriptive statistics",
                priority=TaskPriority.HIGH,
                status=TaskStatus.PENDING,
                input_data={},
            ),
            AITask(
                id=str(uuid.uuid4()),
                capability="data_analysis",
                action="Conduct exploratory analysis, investigate key questions, and derive statistically supported insights",
                priority=TaskPriority.HIGH,
                status=TaskStatus.PENDING,
                input_data={"question": context.message},
            ),
        ]

        return ExecutionPlan(
            objective=objective,
            tasks=tasks,
        )

    # =========================================================
    # BUILD DATA QUESTION PLAN
    # =========================================================

    @staticmethod
    def _build_data_question_plan(
        context: AIContext,
        objective: str,
    ) -> ExecutionPlan:
        """
        Create a deterministic data_question plan.

        This is intentionally independent of the LLM.
        It guarantees that conversational follow-ups reach
        DataQueryAgent, where conversation history can be used.
        """

        task = AITask(
            id=str(
                uuid.uuid4()
            ),
            capability="data_question",
            action=(
                "Answer the user's question using "
                "the uploaded dataset and conversation history"
            ),
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            dependencies=[],
            input_data={
                "question": context.message,
                "use_conversation_history": True,
            },
            output_data={},
        )

        return ExecutionPlan(
            objective=objective,
            tasks=[task],
        )

    # =========================================================
    # PREVIOUS RESULT / FOLLOW-UP DETECTION
    # =========================================================

    @staticmethod
    def _is_previous_result_question(
        message: str,
    ) -> bool:
        """
        Detect questions that refer to a previous result.

        This intentionally covers:
        - previous values
        - previous results
        - previous calculations
        - 'that' references
        - column follow-ups
        - condition follow-ups
        - conversational count follow-ups
        """

        message = (
            message or ""
        ).lower().strip()

        # -----------------------------------------------------
        # Exact / phrase-based references
        # -----------------------------------------------------

        phrases = [

            # Previous result
            "previous result",
            "previous calculation",
            "previous value",
            "previous answer",
            "previous calculation result",

            "last result",
            "last calculation",
            "last value",
            "last answer",

            # Just calculated
            "just calculated",
            "just calculate",
            "just calculated value",
            "just calculated result",

            "what did you calculate",
            "what did you just calculate",
            "what have you calculated",
            "what have you just calculated",

            "what did you get",
            "what did you get just now",
            "what did you find",

            # Value references
            "the value you calculated",
            "the value you just calculated",

            "the result you calculated",
            "the result you just calculated",

            "what was the value",
            "what was that value",
            "what is that value",
            "what's that value",

            "what was that",
            "what is that",

            "what was it",
            "what is it",
            "what's it",

            "that value",
            "that result",
            "that number",

            # Result references
            "what was the result",
            "what was that result",
            "what is the result",
            "what's the result",

            # Number references
            "what was the number",
            "what was that number",
            "what is that number",
            "what's that number",

            "what was the number again",
            "what was that number again",

            "what is the number again",
            "what's the number again",

            # Conversational count references
            "how many were there",
            "how many was that",
            "how many was it",

            "how much was that",
            "how much was it",

            "how many did you get",
            "how much did you get",

            # Column follow-ups
            "what column did you calculate",
            "which column did you calculate",

            "what column was calculated",
            "which column was calculated",

            "what did you calculate it for",
            "which did you calculate it for",

            "which column did you calculate it for",
            "what column did you calculate it for",

            "what was calculated for",

            "which column was that",
            "what column was that",

            "what column was that calculated for",
            "which column was that calculated for",

            "what column was used",
            "which column was used",

            "which column was that based on",
            "what column was that based on",

            "which column was that based upon",
            "what column was that based upon",

            "what was that based on",
            "what was that based upon",

            "which field was that based on",
            "what field was that based on",

            "which field was used",
            "what field was used",

            # Condition follow-ups
            "what condition did you use",
            "which condition did you use",

            "what condition was used",
            "which condition was used",

            "what was the condition",
            "what was that condition",

            "what condition did you calculate with",
            "which condition did you calculate with",

            "what condition was that based on",
            "which condition was that based on",

            "what condition was used for that",
            "which condition was used for that",
        ]

        if any(
            phrase in message
            for phrase in phrases
        ):
            return True

        # -----------------------------------------------------
        # Regex references
        # -----------------------------------------------------

        patterns = [

            # Previous/last result
            r"\bwhat\s+was\s+(?:the\s+)?"
            r"(?:previous|last)\s+"
            r"(?:value|result|calculation|number)\b",

            # What did you calculate?
            r"\bwhat\s+did\s+you\s+"
            r"(?:just\s+)?calculate\b",

            # What was that value/result/number?
            r"\bwhat\s+was\s+that\s+"
            r"(?:number|result|value)\b",

            r"\bwhat\s+is\s+that\s+"
            r"(?:number|result|value)\b",

            # Value/result calculated
            r"\bwhat\s+was\s+the\s+"
            r"(?:value|result|number)\s+"
            r"you\s+"
            r"(?:just\s+)?"
            r"(?:calculated|got|found)\b",

            # Column references
            r"\bwhat\s+column\b",

            r"\bwhich\s+column\b",

            r"\bwhat\s+field\b",

            r"\bwhich\s+field\b",

            # Based-on references
            r"\bwhat\s+was\s+that\s+based\s+on\b",

            r"\bwhich\s+column\s+was\s+that\s+based\s+on\b",

            r"\bwhat\s+column\s+was\s+that\s+based\s+on\b",

            # Condition references
            r"\bwhat\s+condition\b",

            r"\bwhich\s+condition\b",
        ]

        return any(
            re.search(
                pattern,
                message
            )
            for pattern in patterns
        )

    # =========================================================
    # DATA QUESTION DETECTION
    # =========================================================

    @staticmethod
    def _is_data_question(
        message: str,
    ) -> bool:

        message = (
            message or ""
        ).lower().strip()

        phrases = [

            "how many",
            "how much",

            "what is",
            "what are",
            "what was",

            "which",

            "average",
            "mean",

            "median",

            "minimum",
            "maximum",

            "min",
            "max",

            "sum",
            "total",

            "count",
            "number of",

            "percentage",
            "percent",

            "proportion",
            "share",

            "distribution",
            "frequency",

            "unique",
            "distinct",

            "missing",
            "null",
            "na",
            "n/a",

            "value",
            "values",

            "column",
            "columns",

            "condition",
            "conditions",

            "based on",
            "based upon",
        ]

        return any(
            phrase in message
            for phrase in phrases
        )

    # =========================================================
    # ANALYSIS DETECTION
    # =========================================================

    @staticmethod
    def _is_analysis_question(
        message: str,
    ) -> bool:

        message = (
            message or ""
        ).lower().strip()

        phrases = [

            "analyze",
            "analysis",
            "analyse",

            "overview",

            "profile",
            "profiling",

            "summary",
            "summarize",

            "describe",

            "explore",

            "explain the dataset",
            "explain this dataset",

            "dataset insights",
            "insights",

        ]

        return any(
            phrase in message
            for phrase in phrases
        )

    # =========================================================
    # MACHINE LEARNING DETECTION
    # =========================================================

    @classmethod
    def _is_ml_question(
        cls,
        message: str,
    ) -> bool:

        message = (
            message or ""
        ).lower().strip()

        phrases = [
            "train",
            "training",
            "machine learning",
            "machine-learning",
            "model",
            "fit model",
            "build model",
            "classification",
            "regression",
            "predict",
            "prediction",
            "forecast",
            "evaluate model",
        ]

        positive_message = cls._strip_negated_clauses(message)

        return any(
            phrase in positive_message
            for phrase in phrases
        )

    # =========================================================
    # VISUALIZATION DETECTION
    # =========================================================

    @classmethod
    def _is_visualization_question(
        cls,
        message: str,
    ) -> bool:

        message = (
            message or ""
        ).lower().strip()

        phrases = [
            "plot",
            "chart",
            "graph",
            "histogram",
            "scatter",
            "scatter plot",
            "bar chart",
            "bar graph",
            "line chart",
            "line graph",
            "pie chart",
            "boxplot",
            "box plot",
            "heatmap",
            "heat map",
            "visualize",
            "visualization",
            "visualisation",
        ]

        positive_message = cls._strip_negated_clauses(message)

        return any(
            phrase in positive_message
            for phrase in phrases
        )

    # =========================================================
    # REPORT DETECTION
    # =========================================================

    @classmethod
    def _is_report_question(
        cls,
        message: str,
    ) -> bool:

        message = (
            message or ""
        ).lower().strip()

        phrases = [
            "generate a report",
            "generate report",
            "create a report",
            "create report",
            "make a report",
            "dataset report",
            "data report",
            "export report",
        ]

        positive_message = cls._strip_negated_clauses(message)

        return any(
            phrase in positive_message
            for phrase in phrases
        )

    # =========================================================
    # PRIORITY CONVERSION
    # =========================================================

    @staticmethod
    def get_priority(
        priority: str,
    ) -> TaskPriority:

        if not priority:
            return TaskPriority.MEDIUM

        if isinstance(
            priority,
            TaskPriority
        ):
            return priority

        priority = (
            str(priority)
            .upper()
            .strip()
        )

        if priority == "HIGH":
            return TaskPriority.HIGH

        if priority == "LOW":
            return TaskPriority.LOW

        return TaskPriority.MEDIUM

    # =========================================================
    # DEFAULT ACTION
    # =========================================================

    @staticmethod
    def default_action(
        capability: str,
    ) -> str:

        actions = {

            "analyze_dataset":
                "Analyze and explain the uploaded dataset",

            "data_question":
                "Answer the user's question using the uploaded dataset",

            "profile_dataset":
                "Profile the uploaded dataset",

            "quality_score":
                "Evaluate dataset quality",

            "insight":
                "Generate insights from the dataset",

            "recommendation":
                "Generate recommendations from the dataset",

            "train_model":
                "Train a machine learning model",

            "predict":
                "Generate predictions using the trained model",

            "evaluate_model":
                "Evaluate the machine learning model",

            "histogram":
                "Generate a histogram",

            "scatter":
                "Generate a scatter plot",

            "line_chart":
                "Generate a line chart",

            "bar_chart":
                "Generate a bar chart",

            "smart_chart":
                "Generate an intelligent aggregated chart",

            "pie_chart":
                "Generate a pie chart",

            "boxplot":
                "Generate a box plot",

            "heatmap":
                "Generate a heatmap",

            "correlation":
                "Calculate correlations between numerical columns",

            "generate_report":
                "Generate a dataset report",

            "generate_sql":
                "Generate SQL for the requested operation",

            "generate_python":
                "Generate Python code for the requested operation",
        }

        return actions.get(
            capability,
            f"Execute {capability}"
        )
