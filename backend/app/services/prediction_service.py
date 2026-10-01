from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from app.core.ai_engine.response import AIResponse


class PredictionService:

    MODEL_DIR = Path("models")

    MODEL_PATH = (
        MODEL_DIR / "latest_model.pkl"
    )

    @staticmethod
    def predict(
        df: pd.DataFrame
    ) -> AIResponse:

        try:

            # =================================================
            # Check model
            # =================================================

            if not PredictionService.MODEL_PATH.exists():

                return AIResponse(
                    success=False,
                    message="No trained model found."
                )

            # =================================================
            # Load model package
            # =================================================

            package = joblib.load(
                PredictionService.MODEL_PATH
            )

            model = package["model"]

            target = package["target"]

            features = package["features"]

            # =================================================
            # Validate features
            # =================================================

            missing_features = [
                column
                for column in features
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
            # Prepare input
            # =================================================

            X = df[
                features
            ].copy()

            # =================================================
            # Predict
            # =================================================

            predictions = model.predict(
                X
            )

            return AIResponse(

                success=True,

                message=(
                    "Prediction completed successfully."
                ),

                data={

                    "rows":
                        len(X),

                    "target":
                        target,

                    "predictions":
                        predictions.tolist(),
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e)
            )