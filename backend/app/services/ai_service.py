from __future__ import annotations

from app.services.llm_service import LLMService
from app.core.ai_engine.response import AIResponse


class AIService:
    """
    Central AI service for DataNova AI.

    Groq is used as the underlying LLM provider
    through LLMService.

    This class provides a stable interface for
    existing agents and services.
    """

    # =====================================================
    # Generate
    # =====================================================

    @classmethod
    def generate(
        cls,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> AIResponse:

        return LLMService.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
        )


    # =====================================================
    # Ask
    # =====================================================

    @classmethod
    def ask(
        cls,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> AIResponse:
        """
        Backward-compatible single-prompt interface.

        Older DataNova AI services use:

            AIService.ask(prompt)

        Internally this uses the same Groq-powered
        LLMService.generate() method.
        """

        return LLMService.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
        )


    # =====================================================
    # Chat
    # =====================================================

    @classmethod
    def chat(
        cls,
        messages: list,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> AIResponse:

        return LLMService.chat(
            messages=messages,
            model=model,
            temperature=temperature,
        )