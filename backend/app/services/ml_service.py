from __future__ import annotations

import time
import joblib

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import (
    Lasso,
    LinearRegression,
    LogisticRegression,
    Ridge,
)
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.core.ai_engine.response import AIResponse


class MLService:

    MODEL_DIR = Path("models")

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    MODEL_PATH = MODEL_DIR / "latest_model.pkl"

    # =====================================================
    # Regression Models
    # =====================================================

    REGRESSION_MODELS = {

        "Linear Regression": (
            LinearRegression(),
            {}
        ),

        "Ridge": (
            Ridge(),
            {
                "model__alpha": [
                    0.1,
                    1.0,
                    10.0
                ]
            }
        ),

        "Lasso": (
            Lasso(),
            {
                "model__alpha": [
                    0.001,
                    0.01,
                    0.1
                ]
            }
        ),

        "Random Forest": (
            RandomForestRegressor(
                random_state=42
            ),
            {
                "model__n_estimators": [
                    100,
                    200
                ],

                "model__max_depth": [
                    None,
                    10
                ],
            }
        ),

        "Gradient Boosting": (
            GradientBoostingRegressor(
                random_state=42
            ),
            {
                "model__n_estimators": [
                    100,
                    200
                ]
            }
        ),
    }

    # =====================================================
    # Classification Models
    # =====================================================

    CLASSIFICATION_MODELS = {

        "Logistic Regression": (
            LogisticRegression(
                max_iter=1000
            ),
            {}
        ),

        "Random Forest": (
            RandomForestClassifier(
                random_state=42
            ),
            {
                "model__n_estimators": [
                    100,
                    200
                ]
            }
        ),
    }

    # =====================================================
    # Train
    # =====================================================

    @staticmethod
    def train(
        df: pd.DataFrame,
        target: str,
        model: Optional[str] = None,
    ) -> AIResponse:

        try:

            start = time.perf_counter()

            # -------------------------------------------------
            # Validate target
            # -------------------------------------------------

            if target not in df.columns:

                return AIResponse(
                    success=False,
                    message=(
                        f"Target column '{target}' "
                        "not found."
                    ),
                )

            if len(df) < 5:

                return AIResponse(
                    success=False,
                    message=(
                        "At least 5 rows are required "
                        "for model training."
                    ),
                )

            # -------------------------------------------------
            # Remove missing target rows
            # -------------------------------------------------

            data = df.dropna(
                subset=[target]
            ).copy()

            if data.empty:

                return AIResponse(
                    success=False,
                    message=(
                        "No valid rows remain after "
                        "removing missing target values."
                    ),
                )

            # -------------------------------------------------
            # Features / Target
            # -------------------------------------------------

            X = data.drop(
                columns=[target]
            )

            y = data[target]

            # -------------------------------------------------
            # Detect problem
            # -------------------------------------------------

            problem = MLService.detect_problem(
                y
            )

            # -------------------------------------------------
            # Build preprocessing
            # -------------------------------------------------

            preprocessor = (
                MLService.build_preprocessor(X)
            )

            # -------------------------------------------------
            # Train / Test split
            # -------------------------------------------------

            X_train, X_test, y_train, y_test = (
                train_test_split(
                    X,
                    y,
                    test_size=0.2,
                    random_state=42
                )
            )

            # -------------------------------------------------
            # Select models
            # -------------------------------------------------

            if problem == "regression":

                models = (
                    MLService.REGRESSION_MODELS
                )

            else:

                models = (
                    MLService.CLASSIFICATION_MODELS
                )

            # -------------------------------------------------
            # Requested model
            # -------------------------------------------------

            if model:

                if model not in models:

                    return AIResponse(
                        success=False,
                        message=(
                            f"Model '{model}' "
                            "is not available for "
                            f"{problem}."
                        ),
                    )

                models = {
                    model: models[model]
                }

            # -------------------------------------------------
            # Classification validation
            # -------------------------------------------------

            if problem == "classification":

                if y.nunique() < 2:

                    return AIResponse(
                        success=False,
                        message=(
                            "Classification requires "
                            "at least two target classes."
                        ),
                    )

            # -------------------------------------------------
            # Model selection
            # -------------------------------------------------

            best_score = float("-inf")

            best_name = ""

            best_pipeline = None

            results = []

            # =================================================
            # Train Models
            # =================================================

            for name, (
                estimator,
                params
            ) in models.items():

                pipeline = Pipeline(
                    [
                        (
                            "preprocessor",
                            preprocessor
                        ),
                        (
                            "model",
                            estimator
                        ),
                    ]
                )

                # -------------------------------------------------
                # Grid Search
                # -------------------------------------------------

                if params:

                    search = GridSearchCV(
                        pipeline,
                        params,
                        cv=3,
                        n_jobs=-1,
                        scoring=(
                            "r2"
                            if problem == "regression"
                            else "accuracy"
                        ),
                    )

                    trained = search.fit(
                        X_train,
                        y_train
                    ).best_estimator_

                else:

                    trained = pipeline.fit(
                        X_train,
                        y_train
                    )

                # -------------------------------------------------
                # Predictions
                # -------------------------------------------------

                predictions = trained.predict(
                    X_test
                )

                # -------------------------------------------------
                # Regression
                # -------------------------------------------------

                if problem == "regression":

                    score = r2_score(
                        y_test,
                        predictions
                    )

                    metrics = {

                        "r2": round(
                            float(score),
                            4
                        ),

                        "mae": round(
                            float(
                                mean_absolute_error(
                                    y_test,
                                    predictions
                                )
                            ),
                            4
                        ),

                        "rmse": round(
                            float(
                                np.sqrt(
                                    mean_squared_error(
                                        y_test,
                                        predictions
                                    )
                                )
                            ),
                            4
                        ),
                    }

                    cv_folds = min(
                        5,
                        len(data)
                    )

                    cv = cross_val_score(
                        trained,
                        X,
                        y,
                        cv=cv_folds,
                        scoring="r2"
                    ).mean()

                # -------------------------------------------------
                # Classification
                # -------------------------------------------------

                else:

                    score = accuracy_score(
                        y_test,
                        predictions
                    )

                    metrics = {

                        "accuracy": round(
                            float(score),
                            4
                        ),

                        "precision": round(
                            float(
                                precision_score(
                                    y_test,
                                    predictions,
                                    average="weighted",
                                    zero_division=0
                                )
                            ),
                            4
                        ),

                        "recall": round(
                            float(
                                recall_score(
                                    y_test,
                                    predictions,
                                    average="weighted",
                                    zero_division=0
                                )
                            ),
                            4
                        ),

                        "f1": round(
                            float(
                                f1_score(
                                    y_test,
                                    predictions,
                                    average="weighted",
                                    zero_division=0
                                )
                            ),
                            4
                        ),
                    }

                    cv_folds = min(
                        5,
                        len(data)
                    )

                    cv = cross_val_score(
                        trained,
                        X,
                        y,
                        cv=cv_folds,
                        scoring="accuracy"
                    ).mean()

                # -------------------------------------------------
                # Save result
                # -------------------------------------------------

                results.append(
                    {
                        "model": name,
                        **metrics,
                        "cross_validation": round(
                            float(cv),
                            4
                        ),
                    }
                )

                # -------------------------------------------------
                # Best model
                # -------------------------------------------------

                if score > best_score:

                    best_score = float(
                        score
                    )

                    best_name = name

                    best_pipeline = trained

            # =====================================================
            # Save model package
            # =====================================================

            model_package = {

                "model": best_pipeline,

                "target": target,

                "problem_type": problem,

                "features": X.columns.tolist(),
            }

            joblib.dump(
                model_package,
                MLService.MODEL_PATH
            )

            # =====================================================
            # Feature Importance
            # =====================================================

            feature_importance = None

            final_model = (
                best_pipeline
                .named_steps["model"]
            )

            if hasattr(
                final_model,
                "feature_importances_"
            ):

                feature_importance = dict(
                    zip(
                        X.columns,
                        final_model
                        .feature_importances_
                        .tolist()
                    )
                )

            # =====================================================
            # Return
            # =====================================================

            return AIResponse(

                success=True,

                message=(
                    f"Best model: {best_name}"
                ),

                data={

                    "problem_type":
                        problem,

                    "best_model":
                        best_name,

                    "model_path":
                        str(
                            MLService.MODEL_PATH
                        ),

                    "score":
                        round(
                            best_score,
                            4
                        ),

                    "training_time":
                        round(
                            time.perf_counter()
                            - start,
                            2
                        ),

                    "rows":
                        len(data),

                    "features":
                        X.columns.tolist(),

                    "target":
                        target,

                    "feature_importance":
                        feature_importance,

                    "results":
                        results,
                },
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )

    # =====================================================
    # Problem Detection
    # =====================================================

    @staticmethod
    def detect_problem(y):

        if (
            y.dtype == object
            or pd.api.types.is_bool_dtype(y)
        ):

            return "classification"

        if pd.api.types.is_integer_dtype(y):

            if (
                y.nunique() <= 10
                and y.nunique() / len(y) < 0.2
            ):

                return "classification"

        return "regression"

    # =====================================================
    # Preprocessor
    # =====================================================

    @staticmethod
    def build_preprocessor(X):

        numeric = (
            X
            .select_dtypes(
                include=np.number
            )
            .columns
        )

        categorical = (
            X
            .select_dtypes(
                exclude=np.number
            )
            .columns
        )

        transformers = []

        if len(numeric) > 0:

            transformers.append(
                (
                    "numeric",

                    Pipeline(
                        [
                            (
                                "imputer",
                                SimpleImputer(
                                    strategy="median"
                                )
                            ),
                        ]
                    ),

                    numeric,
                )
            )

        if len(categorical) > 0:

            transformers.append(
                (
                    "categorical",

                    Pipeline(
                        [
                            (
                                "imputer",
                                SimpleImputer(
                                    strategy="most_frequent"
                                )
                            ),

                            (
                                "encoder",
                                OneHotEncoder(
                                    handle_unknown="ignore"
                                )
                            ),
                        ]
                    ),

                    categorical,
                )
            )

        return ColumnTransformer(
            transformers
        )