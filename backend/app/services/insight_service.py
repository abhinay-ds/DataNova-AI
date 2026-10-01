from __future__ import annotations

import pandas as pd

from app.core.ai_engine.response import AIResponse


class InsightService:
    """
    Generates intelligent, dataset-specific insights.
    """

    @classmethod
    def analyze(
        cls,
        df: pd.DataFrame,
    ) -> AIResponse:

        return cls.generate(df)

    @classmethod
    def generate(
        cls,
        df: pd.DataFrame,
    ) -> AIResponse:

        try:

            insights = []

            rows, cols = df.shape

            # =================================================
            # DATASET OVERVIEW
            # =================================================

            insights.append(
                f"The dataset contains "
                f"{rows:,} rows and "
                f"{cols} columns."
            )

            # =================================================
            # MISSING VALUES
            # =================================================

            missing_counts = (
                df.isnull()
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            total_missing = int(
                missing_counts.sum()
            )

            if total_missing == 0:

                insights.append(
                    "No missing values were detected."
                )

            else:

                insights.append(
                    f"{total_missing:,} "
                    "missing values were detected."
                )

                for column, count in (
                    missing_counts[
                        missing_counts > 0
                    ].head(5).items()
                ):

                    percentage = (
                        count / rows
                    ) * 100

                    insights.append(
                        f"{column} has "
                        f"{int(count):,} missing values "
                        f"({percentage:.1f}% of rows)."
                    )

            # =================================================
            # DUPLICATES
            # =================================================

            duplicates = int(
                df.duplicated().sum()
            )

            if duplicates == 0:

                insights.append(
                    "No duplicate rows were found."
                )

            else:

                duplicate_percentage = (
                    duplicates / rows
                ) * 100

                insights.append(
                    f"{duplicates:,} duplicate rows "
                    f"were found "
                    f"({duplicate_percentage:.1f}% of rows)."
                )

            # =================================================
            # COLUMN TYPES
            # =================================================

            numeric = df.select_dtypes(
                include="number"
            )

            categorical = df.select_dtypes(
                include=[
                    "object",
                    "category",
                    "bool",
                ]
            )

            if not numeric.empty:

                insights.append(
                    f"{len(numeric.columns)} "
                    "numerical columns detected."
                )

            if not categorical.empty:

                insights.append(
                    f"{len(categorical.columns)} "
                    "categorical columns detected."
                )

            # =================================================
            # CATEGORICAL DISTRIBUTION
            # =================================================

            for column in categorical.columns:

                unique_count = (
                    df[column]
                    .nunique(
                        dropna=True
                    )
                )

                # Only describe reasonably sized
                # categorical variables.

                if 2 <= unique_count <= 10:

                    value_counts = (
                        df[column]
                        .value_counts(
                            dropna=True
                        )
                    )

                    if not value_counts.empty:

                        top_value = (
                            value_counts.index[0]
                        )

                        top_count = int(
                            value_counts.iloc[0]
                        )

                        percentage = (
                            top_count / rows
                        ) * 100

                        insights.append(
                            f"{column} contains "
                            f"{unique_count} categories. "
                            f"'{top_value}' is the most "
                            f"common with "
                            f"{top_count:,} records "
                            f"({percentage:.1f}%)."
                        )

            # =================================================
            # NUMERICAL DISTRIBUTION
            # =================================================

            for column in numeric.columns:

                normalized = (
                    str(column)
                    .lower()
                    .replace("_", "")
                    .replace(" ", "")
                    .replace("-", "")
                )

                # -------------------------------------------------
                # Ignore identifier columns
                # -------------------------------------------------

                if normalized in {
                    "id",
                    "passengerid",
                    "customerid",
                    "userid",
                    "index",
                    "rowid",
                    "recordid",
                }:

                    continue

                series = (
                    df[column]
                    .dropna()
                )

                if series.empty:

                    continue

                unique_count = (
                    series.nunique()
                )

                # -------------------------------------------------
                # Binary numerical variable
                # -------------------------------------------------

                if unique_count == 2:

                    value_counts = (
                        series
                        .value_counts()
                        .sort_index()
                    )

                    distribution = []

                    for value, count in (
                        value_counts.items()
                    ):

                        percentage = (
                            count
                            / len(series)
                        ) * 100

                        distribution.append(
                            f"{value} "
                            f"({percentage:.1f}%)"
                        )

                    insights.append(
                        f"{column} is a binary "
                        f"variable with "
                        f"{', '.join(distribution)}."
                    )

                    continue

                # -------------------------------------------------
                # Low-cardinality discrete variable
                # -------------------------------------------------

                if unique_count <= 10:

                    insights.append(
                        f"{column} contains "
                        f"{unique_count} distinct "
                        "numerical values."
                    )

                    continue

                # -------------------------------------------------
                # Continuous numerical variable
                # -------------------------------------------------

                mean_value = float(
                    series.mean()
                )

                median_value = float(
                    series.median()
                )

                min_value = float(
                    series.min()
                )

                max_value = float(
                    series.max()
                )

                # -------------------------------------------------
                # Skewness
                # -------------------------------------------------

                skewness = float(
                    series.skew()
                )

                if skewness > 1:

                    insights.append(
                        f"{column} is strongly "
                        f"right-skewed "
                        f"(skewness: "
                        f"{skewness:.2f}), "
                        "indicating that higher "
                        "values occur less frequently "
                        "but extend the upper tail."
                    )

                elif skewness < -1:

                    insights.append(
                        f"{column} is strongly "
                        f"left-skewed "
                        f"(skewness: "
                        f"{skewness:.2f}), "
                        "indicating that lower "
                        "values extend the "
                        "distribution's tail."
                    )

                elif abs(skewness) >= 0.5:

                    direction = (
                        "right"
                        if skewness > 0
                        else "left"
                    )

                    insights.append(
                        f"{column} shows moderate "
                        f"{direction} skewness "
                        f"(skewness: "
                        f"{skewness:.2f})."
                    )

                # -------------------------------------------------
                # Range
                # -------------------------------------------------

                if max_value != min_value:

                    insights.append(
                        f"{column} ranges from "
                        f"{min_value:.2f} to "
                        f"{max_value:.2f}, "
                        f"with a median of "
                        f"{median_value:.2f}."
                    )

            # =================================================
            # OUTLIERS
            # =================================================

            outlier_columns = []

            for column in numeric.columns:

                normalized = (
                    str(column)
                    .lower()
                    .replace("_", "")
                    .replace(" ", "")
                    .replace("-", "")
                )

                # Ignore identifiers

                if normalized in {
                    "id",
                    "passengerid",
                    "customerid",
                    "userid",
                    "index",
                    "rowid",
                    "recordid",
                }:

                    continue

                series = (
                    df[column]
                    .dropna()
                )

                if len(series) < 5:

                    continue

                # Do not treat binary/discrete
                # variables as continuous outlier data.

                unique_count = (
                    series.nunique()
                )

                if unique_count <= 10:

                    continue

                q1 = series.quantile(
                    0.25
                )

                q3 = series.quantile(
                    0.75
                )

                iqr = q3 - q1

                if iqr == 0:

                    continue

                lower = (
                    q1
                    - 1.5 * iqr
                )

                upper = (
                    q3
                    + 1.5 * iqr
                )

                outlier_count = int(
                    (
                        (series < lower)
                        |
                        (series > upper)
                    ).sum()
                )

                if outlier_count > 0:

                    percentage = (
                        outlier_count
                        / len(series)
                    ) * 100

                    if percentage >= 5:

                        outlier_columns.append(
                            (
                                column,
                                outlier_count,
                                percentage,
                            )
                        )

            for (
                column,
                count,
                percentage,
            ) in outlier_columns[:5]:

                insights.append(
                    f"{column} contains "
                    f"approximately "
                    f"{count:,} potential "
                    f"outliers "
                    f"({percentage:.1f}% of "
                    "non-missing values)."
                )

            # =================================================
            # CORRELATIONS
            # =================================================

            if len(numeric.columns) >= 2:

                # -------------------------------------------------
                # Remove identifier columns
                # -------------------------------------------------

                correlation_columns = [
                    column
                    for column in numeric.columns
                    if (
                        str(column)
                        .lower()
                        .replace("_", "")
                        .replace(" ", "")
                        .replace("-", "")
                        not in {
                            "id",
                            "passengerid",
                            "customerid",
                            "userid",
                            "index",
                            "rowid",
                            "recordid",
                        }
                    )
                ]

                if len(
                    correlation_columns
                ) >= 2:

                    correlation = (
                        df[
                            correlation_columns
                        ]
                        .corr()
                    )

                    strong_relationships = []

                    for i in range(
                        len(
                            correlation.columns
                        )
                    ):

                        for j in range(
                            i + 1,
                            len(
                                correlation.columns
                            )
                        ):

                            value = (
                                correlation.iloc[
                                    i,
                                    j
                                ]
                            )

                            if pd.isna(value):

                                continue

                            if abs(value) >= 0.5:

                                strong_relationships.append(
                                    (
                                        correlation.columns[
                                            i
                                        ],
                                        correlation.columns[
                                            j
                                        ],
                                        value,
                                    )
                                )

                    strong_relationships.sort(
                        key=lambda item:
                        abs(item[2]),
                        reverse=True,
                    )

                    for (
                        column_a,
                        column_b,
                        value,
                    ) in (
                        strong_relationships[:5]
                    ):

                        relationship = (
                            "positive"
                            if value > 0
                            else "negative"
                        )

                        insights.append(
                            f"{column_a} and "
                            f"{column_b} have a "
                            f"strong "
                            f"{relationship} "
                            f"relationship "
                            f"(correlation: "
                            f"{value:.2f})."
                        )

            # =================================================
            # LARGE DATASET
            # =================================================

            if rows > 100000:

                insights.append(
                    "Large dataset detected. "
                    "Sampling may improve "
                    "analysis speed."
                )

            # =================================================
            # FINAL RESPONSE
            # =================================================

            return AIResponse(
                success=True,
                message=(
                    "Insights generated "
                    "successfully."
                ),
                data=insights,
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=(
                    "Insight generation "
                    f"failed: {str(e)}"
                ),
            )