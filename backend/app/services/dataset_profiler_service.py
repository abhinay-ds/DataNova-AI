import pandas as pd

from app.core.ai_engine.response import AIResponse


class DatasetProfilerService:

    @classmethod
    def get_shape(cls, df: pd.DataFrame):
        return {
            "rows": df.shape[0],
            "columns": df.shape[1]
        }

    @classmethod
    def get_columns(cls, df: pd.DataFrame):
        return df.columns.tolist()

    @classmethod
    def get_data_types(cls, df: pd.DataFrame):
        return df.dtypes.astype(str).to_dict()

    @classmethod
    def get_missing_values(cls, df: pd.DataFrame):
        return df.isnull().sum().to_dict()

    @classmethod
    def get_duplicate_count(cls, df: pd.DataFrame):
        return int(df.duplicated().sum())

    @classmethod
    def get_memory_usage(cls, df: pd.DataFrame):
        memory = df.memory_usage(deep=True).sum()

        return {
            "bytes": int(memory),
            "kb": round(memory / 1024, 2),
            "mb": round(memory / (1024 ** 2), 2),
        }

    @classmethod
    def get_unique_values(cls, df: pd.DataFrame):
        return df.nunique().to_dict()

    @classmethod
    def get_numerical_summary(cls, df: pd.DataFrame):
        numeric = df.select_dtypes(include="number")

        if numeric.empty:
            return {}

        return numeric.describe().round(2).to_dict()

    @classmethod
    def get_categorical_summary(cls, df: pd.DataFrame):

        categorical = df.select_dtypes(
            include=["object", "category", "bool"]
        )

        summary = {}

        for column in categorical.columns:

            value_counts = categorical[column].value_counts(dropna=False)

            summary[column] = {
                "unique": int(categorical[column].nunique()),
                "top": (
                    categorical[column].mode().iloc[0]
                    if not categorical[column].mode().empty
                    else None
                ),
                "frequency": (
                    int(value_counts.iloc[0])
                    if not value_counts.empty
                    else 0
                )
            }

        return summary

    @classmethod
    def profile(cls, df: pd.DataFrame):

        try:

            if df is None or df.empty:
                return AIResponse(
                    success=False,
                    message="Dataset is empty."
                )

            profile = {

                "shape": cls.get_shape(df),

                "columns": cls.get_columns(df),

                "data_types": cls.get_data_types(df),

                "missing_values": cls.get_missing_values(df),

                "duplicates": cls.get_duplicate_count(df),

                "memory_usage": cls.get_memory_usage(df),

                "unique_values": cls.get_unique_values(df),

                "numerical_summary": cls.get_numerical_summary(df),

                "categorical_summary": cls.get_categorical_summary(df),
            }

            return AIResponse(
                success=True,
                message="Dataset profile generated successfully.",
                data=profile,
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
            )