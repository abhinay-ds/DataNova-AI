from app.services.dataset_store import get_dataset
from app.services.llm_service import LLMService


class DatasetChatService:

    @classmethod
    def ask(cls, question: str):

        df = get_dataset()

        if df is None:

            return {
                "success": False,
                "message": "Please upload a dataset first."
            }

        prompt = f"""
You are DataNova AI.

Answer ONLY using the uploaded dataset.

Dataset Shape:
{df.shape}

Columns:
{", ".join(df.columns)}

Data Types:
{df.dtypes.to_string()}

Missing Values:
{df.isnull().sum().to_string()}

Statistics:
{df.describe(include='all').to_string()}

User Question:

{question}

Answer professionally.
"""

        response = LLMService.generate(prompt)

        return {
            "success": True,
            "answer": response.data
        }