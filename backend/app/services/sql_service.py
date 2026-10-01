import pandas as pd


class SQLService:

    @staticmethod
    def execute_query(df: pd.DataFrame, query: str):

        try:
            result = df.query(query)

            return {
                "rows": len(result),
                "data": result.head(20).to_dict(orient="records")
            }

        except Exception as e:
            raise Exception(f"Invalid query: {e}")