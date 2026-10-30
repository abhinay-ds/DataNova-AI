from __future__ import annotations

import json
import logging
from pathlib import Path
import re

import pandas as pd

from app.core.ai_engine.context import AIContext
from app.core.ai_engine.response import AIResponse
from app.services.agents.base_agent import BaseAgent
from app.services.ai_service import AIService


logger = logging.getLogger(__name__)


class MLAgent(BaseAgent):
    """
    Machine Learning Agent.

    Responsibilities
    ----------------
    - Train ML models
    - Predict using trained models
    - Evaluate trained models
    - Store results in memory
    - Use Groq LLM for target/input extraction when required
    """

    @property
    def name(self) -> str:
        return "MLAgent"

    @property
    def capabilities(self) -> list[str]:
        return [
            "train_model",
            "predict",
            "evaluate_model",
        ]

    async def execute(
        self,
        context: AIContext,
    ) -> AIResponse:

        logger.info("MLAgent started")

        # =====================================================
        # Validate Dataset
        # =====================================================

        if context.dataset is None:

            return AIResponse(
                success=False,
                message="Please upload a dataset first.",
                agent=self.name,
                intent=context.intent or "ml",
            )

        task = context.current_task

        if task is None:

            return AIResponse(
                success=False,
                message="No task available.",
                agent=self.name,
                intent=context.intent or "ml",
            )

        try:

            response = None

            # =================================================
            # TRAIN MODEL
            # =================================================

            if task.capability == "train_model":

                target = self.resolve_target(
                    task=task,
                    context=context,
                    columns=context.dataset.columns.tolist() if context.dataset is not None else [],
                )

                # ---------------------------------------------
                # Target still unknown
                # ---------------------------------------------

                if not target:

                    return AIResponse(
                        success=False,
                        message=(
                            "Unable to determine the target "
                            "column."
                        ),
                        agent=self.name,
                        intent="train_model",
                    )

                # ---------------------------------------------
                # Validate target
                # ---------------------------------------------

                if target not in context.dataset.columns:

                    return AIResponse(
                        success=False,
                        message=(
                            f"Target column '{target}' "
                            "not found."
                        ),
                        agent=self.name,
                        intent="train_model",
                    )

                # ---------------------------------------------
                # Execute training tool
                # ---------------------------------------------

                tool = context.tool_registry.get(
                    "train_model"
                )

                if tool is None:

                    return AIResponse(
                        success=False,
                        message="Training tool is not available.",
                        agent=self.name,
                        intent="train_model",
                    )

                response = tool.execute(
                    dataset=context.dataset,
                    target=target,
                )

                task.output_data = (
                    response.data
                    if hasattr(response, "data")
                    else {}
                )

                # ---------------------------------------------
                # Save memory
                # ---------------------------------------------

                self._save_memory(
                    context,
                    task,
                    response,
                )

                # ---------------------------------------------
                # Normalize response metadata
                # ---------------------------------------------

                return self._normalize_response(
                    response=response,
                    intent="train_model",
                )

            # =================================================
            # PREDICT
            # =================================================

            elif task.capability == "predict":

                import joblib

                # ---------------------------------------------
                # Load trained model
                # ---------------------------------------------

                package = joblib.load(
                    "models/latest_model.pkl"
                )

                features = package["features"]

                # ---------------------------------------------
                # Check planner supplied prediction data
                # ---------------------------------------------

                prediction_data = (
                    task.input_data.get("data")
                )

                # ---------------------------------------------
                # Ask Groq to extract prediction values
                # ---------------------------------------------

                if not prediction_data:

                    prediction_data = (
                        self.extract_prediction_data(
                            context.message,
                            features,
                        )
                    )

                # ---------------------------------------------
                # Prediction data unavailable
                # ---------------------------------------------

                if not prediction_data:

                    return AIResponse(
                        success=False,
                        message=(
                            "I could not determine the "
                            "prediction values from your request."
                        ),
                        agent=self.name,
                        intent="predict",
                    )

                # ---------------------------------------------
                # Convert to DataFrame
                # ---------------------------------------------

                prediction_df = pd.DataFrame(
                    prediction_data
                )

                # ---------------------------------------------
                # Validate required features
                # ---------------------------------------------

                missing_features = [
                    feature
                    for feature in features
                    if feature not in prediction_df.columns
                ]

                if missing_features:

                    return AIResponse(
                        success=False,
                        message=(
                            "Missing prediction features: "
                            + ", ".join(missing_features)
                        ),
                        agent=self.name,
                        intent="predict",
                    )

                # ---------------------------------------------
                # Keep only model features
                # ---------------------------------------------

                prediction_df = prediction_df[
                    features
                ]

                # ---------------------------------------------
                # Execute prediction tool
                # ---------------------------------------------

                tool = context.tool_registry.get(
                    "predict"
                )

                if tool is None:

                    return AIResponse(
                        success=False,
                        message="Prediction tool is not available.",
                        agent=self.name,
                        intent="predict",
                    )

                response = tool.execute(
                    dataset=prediction_df
                )

                task.output_data = (
                    response.data
                    if hasattr(response, "data")
                    else {}
                )

                self._save_memory(
                    context,
                    task,
                    response,
                )

                return self._normalize_response(
                    response=response,
                    intent="predict",
                )

            # =================================================
            # EVALUATE MODEL
            # =================================================

            elif task.capability == "evaluate_model":

                target = self.resolve_target(
                    task=task,
                    context=context,
                    columns=context.dataset.columns.tolist() if context.dataset is not None else [],
                )

                # ---------------------------------------------
                # Target unavailable
                # ---------------------------------------------

                if not target:

                    return AIResponse(
                        success=False,
                        message=(
                            "Unable to determine the target "
                            "column."
                        ),
                        agent=self.name,
                        intent="evaluate_model",
                    )

                # ---------------------------------------------
                # Validate target
                # ---------------------------------------------

                if target not in context.dataset.columns:

                    return AIResponse(
                        success=False,
                        message=(
                            f"Target column '{target}' "
                            "not found."
                        ),
                        agent=self.name,
                        intent="evaluate_model",
                    )

                # ---------------------------------------------
                # Execute evaluation tool
                # ---------------------------------------------

                tool = context.tool_registry.get(
                    "evaluate_model"
                )

                if tool is None:

                    return AIResponse(
                        success=False,
                        message="Evaluation tool is not available.",
                        agent=self.name,
                        intent="evaluate_model",
                    )

                response = tool.execute(
                    dataset=context.dataset,
                    target=target,
                )

                task.output_data = (
                    response.data
                    if hasattr(response, "data")
                    else {}
                )

                self._save_memory(
                    context,
                    task,
                    response,
                )

                return self._normalize_response(
                    response=response,
                    intent="evaluate_model",
                )

            # =================================================
            # UNKNOWN CAPABILITY
            # =================================================

            else:

                return AIResponse(
                    success=False,
                    message=(
                        f"Unsupported capability: "
                        f"{task.capability}"
                    ),
                    agent=self.name,
                    intent=task.capability,
                )

        except Exception as e:

            logger.exception(
                "MLAgent failed."
            )

            return AIResponse(
                success=False,
                message=str(e),
                agent=self.name,
                intent=task.capability,
            )

    # =========================================================
    # NORMALIZE TOOL RESPONSE
    # =========================================================

    def _normalize_response(
        self,
        response: AIResponse,
        intent: str,
    ) -> AIResponse:
        """
        Preserve the tool result while ensuring that the
        response contains MLAgent metadata.
        """

        if not isinstance(response, AIResponse):

            return AIResponse(
                success=True,
                message=str(response),
                data={},
                agent=self.name,
                intent=intent,
            )

        return AIResponse(
            success=response.success,
            message=response.message,
            data=response.data,
            agent=self.name,
            intent=intent,
            execution_time=response.execution_time,
        )

    # =========================================================
    # SAVE MEMORY
    # =========================================================

    @staticmethod
    def _save_memory(
        context: AIContext,
        task,
        response: AIResponse,
    ) -> None:

        if not hasattr(context, "memory"):
            return

        try:

            context.memory.task.last_task = task

            if hasattr(response, "data"):

                context.memory.task.last_result = (
                    response.data
                )

        except AttributeError:

            pass

    # =========================================================
    # ASK GROQ FOR TARGET
    # =========================================================

    @staticmethod
    def ask_llm_for_target(
        message: str,
        columns: list[str],
    ) -> str | None:

        prompt = f"""
You are DataNova AI.

Dataset Columns:
{", ".join(columns)}

User Request:
{message}

Determine which column is the prediction target.

Return ONLY the exact column name.

Do not explain.
"""

        try:

            result = AIService.generate(
                prompt=prompt,
                temperature=0,
            )

            if not result.success:
                return None

            response = result.data

            if not response:
                return None

            response = str(response).strip()

            # ---------------------------------------------
            # Remove accidental markdown formatting
            # ---------------------------------------------

            response = (
                response
                .replace("`", "")
                .strip()
            )

            # ---------------------------------------------
            # Match exact column
            # ---------------------------------------------

            for column in columns:

                if column.lower() == response.lower():

                    return column

            return None

        except Exception:

            logger.exception(
                "Failed to determine target using Groq."
            )

            return None

    # =========================================================
    # RESOLVE TARGET WITH STRICT PRIORITY
    # =========================================================

    def resolve_target(
        self,
        task,
        context,
        columns: list[str],
    ) -> str | None:
        """
        Implement strict target resolution priority:
        A. Explicit target supplied in task.input_data
        B. Target supplied by previous task/result context or saved model
        C. Explicit target language in the user request
        D. Dataset target inference only as a final fallback
        """
        if not columns:
            return None

        col_lower_map = {c.lower(): c for c in columns}

        # Priority A: Explicit target supplied in task.input_data
        explicit_target = (
            task.input_data.get("target")
            or task.input_data.get("target_column")
        )
        if explicit_target and str(explicit_target).strip().lower() in col_lower_map:
            return col_lower_map[str(explicit_target).strip().lower()]

        # Priority B: Target supplied by previous task/result context or saved model
        prev_results = task.input_data.get("_previous_results", {})
        if isinstance(prev_results, dict):
            train_res = prev_results.get("train_model")
            if isinstance(train_res, dict) and train_res.get("target"):
                candidate = str(train_res.get("target")).strip().lower()
                if candidate in col_lower_map:
                    return col_lower_map[candidate]

            for _, res in prev_results.items():
                if isinstance(res, dict) and res.get("target"):
                    candidate = str(res.get("target")).strip().lower()
                    if candidate in col_lower_map:
                        return col_lower_map[candidate]

        # For evaluate_model or predict, check saved trained model package
        if task.capability in ("evaluate_model", "predict"):
            try:
                model_path = Path("models/latest_model.pkl")
                if model_path.exists():
                    import joblib
                    pkg = joblib.load(model_path)
                    saved_target = pkg.get("target")
                    if saved_target and str(saved_target).strip().lower() in col_lower_map:
                        return col_lower_map[str(saved_target).strip().lower()]
            except Exception:
                pass

        # Priority C: Explicit target language in the user request
        if context.message:
            target_from_msg = self.extract_target(context.message, columns)
            if target_from_msg:
                return target_from_msg

        # Priority D: Dataset target inference only as a final fallback
        if context.message:
            llm_target = self.ask_llm_for_target(context.message, columns)
            if llm_target and str(llm_target).strip().lower() in col_lower_map:
                return col_lower_map[str(llm_target).strip().lower()]

        return None

    # =========================================================
    # EXTRACT TARGET DIRECTLY
    # =========================================================

    @staticmethod
    def extract_target(
        message: str,
        columns: list[str],
    ) -> str | None:
        """
        Extract explicit target column from user request using intent language.
        Never select a target merely because its column name is longer.
        """
        if not message or not columns:
            return None

        message_lower = message.lower()
        col_lower_map = {c.lower(): c for c in columns}

        # Explicit target phrases (e.g., "predict salary", "predict the salary for Age 29...")
        target_patterns = [
            r"(?:predict|estimate|forecast|calculate|determine)\s+(?:the\s+|a\s+|an\s+)?([a-zA-Z0-9_]+)",
            r"(?:predicting|estimating|forecasting)\s+(?:the\s+|a\s+|an\s+)?([a-zA-Z0-9_]+)",
            r"(?:target|dependent\s+variable|label)\s*(?:is|column|variable)?\s*[:=]?\s*['\"]?([a-zA-Z0-9_]+)['\"]?",
            r"to\s+predict\s+(?:the\s+|a\s+|an\s+)?([a-zA-Z0-9_]+)",
            r"model\s+for\s+(?:the\s+)?([a-zA-Z0-9_]+)",
        ]

        for pat in target_patterns:
            match = re.search(pat, message_lower)
            if match:
                candidate = match.group(1).strip()
                if candidate in col_lower_map:
                    return col_lower_map[candidate]

        # Check if message explicitly says "<col> as target" or "<col> is the target"
        for col in columns:
            col_l = col.lower()
            if re.search(rf"\b{re.escape(col_l)}\b\s+(?:as|is)\s+(?:the\s+)?target", message_lower):
                return col

        # If exactly one column is mentioned in the entire request
        mentioned = [
            col for col in columns
            if re.search(rf"\b{re.escape(col.lower())}\b", message_lower)
        ]
        if len(mentioned) == 1:
            return mentioned[0]

        return None

    # =========================================================
    # EXTRACT PREDICTION DATA USING GROQ
    # =========================================================

    @staticmethod
    def extract_prediction_data(
        message: str,
        features: list[str],
    ) -> dict | None:

        prompt = f"""
You are DataNova AI.

The trained machine learning model requires
these input features:

{json.dumps(features, indent=2)}

The user wants to make a prediction.

USER REQUEST:
{message}

Extract the values supplied by the user
for the required model features.

Return ONLY valid JSON.

The JSON must have this structure:

{{
    "FeatureName1": [value],
    "FeatureName2": [value]
}}

Rules:

1. Use the exact feature names.
2. Put each value inside a list.
3. Do not include the prediction target.
4. Do not invent missing values.
5. Return ONLY JSON.
"""

        try:

            result = AIService.generate(
                prompt=prompt,
                temperature=0,
            )

            if not result.success:
                return None

            response = result.data

            if not response:
                return None

            raw = str(response).strip()

            # ---------------------------------------------
            # Remove Markdown code fences
            # ---------------------------------------------

            if raw.startswith("```"):

                raw = (
                    raw
                    .replace("```json", "")
                    .replace("```JSON", "")
                    .replace("```", "")
                    .strip()
                )

            # ---------------------------------------------
            # Parse JSON
            # ---------------------------------------------

            try:

                data = json.loads(raw)

            except json.JSONDecodeError:

                return None

            if not isinstance(data, dict):
                return None

            # ---------------------------------------------
            # Validate requested features
            # ---------------------------------------------

            for feature in features:

                if feature not in data:

                    return None

            return data

        except Exception:

            logger.exception(
                "Failed to extract prediction data using Groq."
            )

            return None