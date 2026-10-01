class IntentClassifier:

    INTENTS = {

        # =====================================================
        # Dataset Questions
        # =====================================================

        "data_question": [
            "average",
            "mean",
            "median",
            "minimum",
            "maximum",
            "lowest",
            "highest",
            "smallest",
            "largest",
            "unique values",
            "distinct values",
            "distribution",
            "breakdown",
            "count of",
            "how many rows",
            "number of rows",
            "how many records",
            "number of records",
            "how many columns",
            "number of columns",
            "missing values",
            "missing data",
            "null values",
            "nulls",
            "duplicates",
            "duplicate rows",
            "what columns",
            "which columns",
            "column names",

            # Follow-up questions
            "previous result",
            "previous calculation",
            "last result",
            "last calculation",
            "what was the value",
            "what was the result",
            "what did you calculate",
            "what did you just calculate",
            "what was the value you just calculated",
            "the value you calculated",
            "the result you calculated",
        ],

        # =====================================================
        # Dataset Analysis
        # =====================================================

        "analyze_dataset": [
            "analyze",
            "analyse",
            "profile",
            "overview",
            "summary",
        ],

        # =====================================================
        # Machine Learning
        # =====================================================

        "train_model": [
            "train",
            "fit",
            "build model",
        ],

        "predict": [
            "predict",
            "forecast",
        ],

        # =====================================================
        # Visualization
        # =====================================================

        "histogram": [
            "histogram",
        ],

        "scatter": [
            "scatter",
        ],

        "heatmap": [
            "heatmap",
        ],

        "correlation": [
            "correlation",
        ],

        # =====================================================
        # Reports
        # =====================================================

        "generate_report": [
            "report",
            "pdf",
        ],

        # =====================================================
        # SQL
        # =====================================================

        "generate_sql": [
            "sql",
            "query",
        ],

        # =====================================================
        # Code
        # =====================================================

        "generate_code": [
            "python",
            "code",
        ],
    }

    @classmethod
    def classify(cls, message: str):

        if not message:
            return "general_chat"

        message = message.lower().strip()

        # =====================================================
        # IMPORTANT:
        # Data questions must be checked first.
        # This prevents follow-up calculation questions
        # from falling through to general_chat.
        # =====================================================

        data_keywords = cls.INTENTS["data_question"]

        for keyword in data_keywords:

            if keyword in message:
                return "data_question"

        # =====================================================
        # Other intents
        # =====================================================

        for capability, keywords in cls.INTENTS.items():

            if capability == "data_question":
                continue

            for keyword in keywords:

                if keyword in message:
                    return capability

        return "general_chat"