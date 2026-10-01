from app.services.ai_service import AIService


class CodeService:

    @staticmethod
    def generate_code(prompt: str):

        system_prompt = f"""
You are an expert Python, SQL, Machine Learning and Data Analysis developer.

Generate only the requested code.

User Request:
{prompt}
"""

        return AIService.ask(system_prompt)