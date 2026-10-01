import pandas as pd


class ProfileService:

    @staticmethod
    def generate_profile(df: pd.DataFrame):

        return {
            "overview": {
                "rows": len(df),
                "columns": len(df.columns),
                "memory_usage": f"{round(df.memory_usage(deep=True).sum() / 1024, 2)} KB",
            },

            "columns": list(df.columns),

            "data_types": {
                col: str(dtype)
                for col, dtype in df.dtypes.items()
            },

            "missing_values": {
                col: int(count)
                for col, count in df.isnull().sum().items()
            },

            "duplicates": int(df.duplicated().sum()),

            "numeric_columns": list(
                df.select_dtypes(include="number").columns
            ),

            "categorical_columns": list(
                df.select_dtypes(exclude="number").columns
            ),

            "statistics": df.describe(include="all").fillna("").to_dict(),

            "sample_data": df.head(10).to_dict(
                orient="records"
            ),
        }