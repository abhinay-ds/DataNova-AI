from __future__ import annotations

import json
import logging

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

                target = (
                    task.input_data.get("target")
                    or task.input_data.get("target_column")
                )

                # ---------------------------------------------
                # Try extracting target from user message
                # ---------------------------------------------

                if not target:

                    target = self.extract_target(
                        context.message,
                        context.dataset.columns.tolist(),
                    )

                # ---------------------------------------------
                # Ask Groq if target is still unknown
                # ---------------------------------------------

                if not target:

                    target = self.ask_llm_for_target(
                        context.message,
                        context.dataset.columns.tolist(),
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

                target = (
                    task.input_data.get("target")
                    or task.input_data.get("target_column")
                )

                # ---------------------------------------------
                # Extract target from message
                # ---------------------------------------------

                if not target:

                    target = self.extract_target(
                        context.message,
                        context.dataset.columns.tolist(),
                    )

                # ---------------------------------------------
                # Ask Groq if needed
                # ---------------------------------------------

                if not target:

                    target = self.ask_llm_for_target(
                        context.message,
                        context.dataset.columns.tolist(),
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
    # EXTRACT TARGET DIRECTLY
    # =========================================================

    @staticmethod
    def extract_target(
        message: str,
        columns: list[str],
    ) -> str | None:

        message_lower = message.lower()

        # Prefer exact longer column names first.
        sorted_columns = sorted(
            columns,
            key=len,
            reverse=True,
        )

        for column in sorted_columns:

            if column.lower() in message_lower:

                return column

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