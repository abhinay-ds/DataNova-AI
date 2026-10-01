from app.services.visualization_service import VisualizationService


class AnalysisService:

    @staticmethod
    def text(message: str):
        return {
            "type": "text",
            "response": message,
            "url": None,
        }

    @staticmethod
    def image(image_path: str):
        return {
            "type": "image",
            "response": None,
            "url": image_path,
        }

    @staticmethod
    def analyze(df, message: str):

        if df is None:
            return AnalysisService.text(
                "Please upload a dataset first."
            )

        msg = message.lower().strip()

        # ---------------- Greetings ----------------

        if any(word in msg for word in ["hi", "hello", "hey"]):
            return AnalysisService.text(
                "Hello! I'm DataNova AI.\n\n"
                "You can ask things like:\n"
                "• How many rows?\n"
                "• Show column names\n"
                "• Describe dataset\n"
                "• Explain dataset\n"
                "• Give insights\n"
                "• Missing values\n"
                "• Plot histogram of RM\n"
            )

        # ---------------- Explain Dataset ----------------

        elif ("explain" in msg and "dataset" in msg) or \
             ("describe" in msg and "dataset" in msg):

            numeric = df.select_dtypes(include="number").columns.tolist()
            categorical = df.select_dtypes(exclude="number").columns.tolist()

            return AnalysisService.text(
                f"""
Dataset Summary

Rows: {len(df)}
Columns: {len(df.columns)}

Column Names:
{", ".join(df.columns)}

Missing Values:
{df.isnull().sum().sum()}

Duplicate Rows:
{df.duplicated().sum()}

Numeric Columns ({len(numeric)}):
{", ".join(numeric)}

Categorical Columns ({len(categorical)}):
{", ".join(categorical)}

The dataset is ready for analysis.
"""
            )

        # ---------------- Insights ----------------

        elif "insight" in msg or "insights" in msg:

            numeric = df.select_dtypes(include="number").columns.tolist()
            categorical = df.select_dtypes(exclude="number").columns.tolist()

            return AnalysisService.text(
                f"""
Quick Dataset Insights

Shape:
{df.shape[0]} rows × {df.shape[1]} columns

Missing Values:
{df.isnull().sum().sum()}

Duplicate Rows:
{df.duplicated().sum()}

Memory Usage:
{df.memory_usage(deep=True).sum()/1024:.2f} KB

Numeric Features:
{", ".join(numeric)}

Categorical Features:
{", ".join(categorical)}
"""
            )

        # ---------------- Histogram ----------------

        elif "histogram" in msg:

            column_name = (
                msg.replace("plot histogram of", "")
                .replace("histogram of", "")
                .replace("plot histogram", "")
                .replace("histogram", "")
                .strip()
            )

            actual_column = None

            for col in df.columns:
                if col.lower() == column_name.lower():
                    actual_column = col
                    break

            if actual_column is None:
                return AnalysisService.text(
                    f"Column '{column_name}' not found."
                )

            image_path = VisualizationService.histogram(
                df,
                actual_column,
            )

            return AnalysisService.image(image_path)

        # ---------------- Dataset Information ----------------

        elif "rows" in msg:

            return AnalysisService.text(
                f"The dataset contains {len(df)} rows."
            )

        elif "columns" in msg and "numeric" not in msg and "categorical" not in msg:

            return AnalysisService.text(
                f"The dataset has {len(df.columns)} columns.\n\n"
                + ", ".join(df.columns)
            )

        elif "shape" in msg:

            return AnalysisService.text(
                f"{df.shape[0]} rows × {df.shape[1]} columns"
            )

        elif "missing" in msg:

            return AnalysisService.text(
                df.isnull().sum().to_string()
            )

        elif "summary" in msg:

            return AnalysisService.text(
                df.describe(include="all").to_string()
            )

        elif "head" in msg or "first" in msg:

            return AnalysisService.text(
                df.head().to_string()
            )

        elif "tail" in msg:

            return AnalysisService.text(
                df.tail().to_string()
            )

        elif "datatype" in msg or "data type" in msg or "data types" in msg:

            return AnalysisService.text(
                df.dtypes.to_string()
            )

        elif "duplicate" in msg:

            return AnalysisService.text(
                f"Duplicate rows: {df.duplicated().sum()}"
            )

        elif "memory" in msg:

            return AnalysisService.text(
                f"Memory Usage: {df.memory_usage(deep=True).sum()/1024:.2f} KB"
            )

        elif "numeric" in msg:

            return AnalysisService.text(
                "Numeric Columns:\n\n"
                + ", ".join(
                    df.select_dtypes(include="number").columns
                )
            )

        elif "categorical" in msg:

            return AnalysisService.text(
                "Categorical Columns:\n\n"
                + ", ".join(
                    df.select_dtypes(exclude="number").columns
                )
            )

        elif "column names" in msg:

            return AnalysisService.text(
                ", ".join(df.columns)
            )

        elif "preview" in msg:

            return AnalysisService.text(
                df.head(10).to_string()
            )

        return AnalysisService.text(
            "Sorry, I couldn't understand your request."
        )