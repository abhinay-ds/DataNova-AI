from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    r2_score,
    mean_absolute_error,
    mean_squared_error,
)

from app.core.ai_engine.response import AIResponse


class EvaluationService:

    MODEL_DIR = Path("models")
    MODEL_PATH = MODEL_DIR / "latest_model.pkl"

    @staticmethod
    def evaluate(
        df: pd.DataFrame,
        target: str,
    ) -> AIResponse:

        try:

            # =================================================
            # Check trained model
            # =================================================

            if not EvaluationService.MODEL_PATH.exists():

                return AIResponse(
                    success=False,
                    message="No trained model found."
                )

            # =================================================
            # Check target
            # =================================================

            if target not in df.columns:

                return AIResponse(
                    success=False,
                    message=(
                        f"Target column '{target}' "
                        "not found."
                    )
                )

            # =================================================
            # Load model package
            # =================================================

            package = joblib.load(
                EvaluationService.MODEL_PATH
            )

            model = package["model"]

            saved_target = package["target"]

            saved_features = package["features"]

            problem_type = package["problem_type"]

            # =================================================
            # Validate target
            # =================================================

            if saved_target != target:

                return AIResponse(
                    success=False,
                    message=(
                        f"Model was trained for target "
                        f"'{saved_target}', "
                        f"not '{target}'."
                    ),
                )

            # =================================================
            # Validate features
            # =================================================

            missing_features = [
                column
                for column in saved_features
                if column not in df.columns
            ]

            if missing_features:

                return AIResponse(
                    success=False,
                    message=(
                        "Missing required features: "
                        + ", ".join(
                            missing_features
                        )
                    ),
                )

            # =================================================
            # Prepare data
            # =================================================

            X = df[
                saved_features
            ].copy()

            y = df[target]

            # =================================================
            # Generate predictions
            # =================================================

            predictions = model.predict(
                X
            )

            # =================================================
            # Classification
            # =================================================

            if problem_type == "classification":

                return AIResponse(

                    success=True,

                    message=(
                        "Classification evaluation "
                        "completed."
                    ),

                    data={

                        "problem_type":
                            "classification",

                        "accuracy":
                            round(
                                accuracy_score(
                                    y,
                                    predictions
                                ),
                                4
                            ),

                        "precision":
                            round(
                                precision_score(
                                    y,
                                    predictions,
                                    average="weighted",
                                    zero_division=0,
                                ),
                                4
                            ),

                        "recall":
                            round(
                                recall_score(
                                    y,
                                    predictions,
                                    average="weighted",
                                    zero_division=0,
                                ),
                                4
                            ),

                        "f1_score":
                            round(
                                f1_score(
                                    y,
                                    predictions,
                                    average="weighted",
                                    zero_division=0,
                                ),
                                4
                            ),

                        "confusion_matrix":
                            confusion_matrix(
                                y,
                                predictions,
                            ).tolist(),
                    },
                )

            # =================================================
            # Regression
            # =================================================

            return AIResponse(

                success=True,

                message=(
                    "Regression evaluation "
                    "completed."
                ),

                data={

                    "problem_type":
                        "regression",

                    "r2_score":
                        round(
                            r2_score(
                                y,
                                predictions,
                            ),
                            4
                        ),

                    "mae":
                        round(
                            mean_absolute_error(
                                y,
                                predictions,
                            ),
                            4
                        ),

                    "rmse":
                        round(
                            np.sqrt(
                                mean_squared_error(
                                    y,
                                    predictions,
                                )
                            ),
                            4
                        ),
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )