from __future__ import annotations

from openai import OpenAI, OpenAIError

from app.core.config import settings
from app.core.ai_engine.response import AIResponse


class LLMService:

    MODEL = "openai/gpt-oss-120b"

    @classmethod
    def get_client(cls):

        return OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

    @classmethod
    def generate(
        cls,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> AIResponse:

        try:

            client = cls.get_client()

            response = client.chat.completions.create(
                model=model or cls.MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=temperature,
            )

            content = (
                response.choices[0]
                .message
                .content
            )

            return AIResponse(
                success=True,
                message="LLM response generated successfully.",
                data=content,
            )

        except OpenAIError as e:

            return AIResponse(
                success=False,
                message=str(e),
                data=None,
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
                data=None,
            )

    @classmethod
    def chat(
        cls,
        messages: list,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> AIResponse:

        try:

            client = cls.get_client()

            response = client.chat.completions.create(
                model=model or cls.MODEL,
                messages=messages,
                temperature=temperature,
            )

            content = (
                response.choices[0]
                .message
                .content
            )

            return AIResponse(
                success=True,
                message="LLM response generated successfully.",
                data=content,
            )

        except OpenAIError as e:

            return AIResponse(
                success=False,
                message=str(e),
                data=None,
            )

        except Exception as e:

            return AIResponse(
                success=False,
                message=str(e),
                data=None,
            )