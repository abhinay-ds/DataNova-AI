from fastapi import APIRouter

from app.services.llm_service import LLMService

router = APIRouter()


@router.get("/test-llm")
async def test_llm():

    messages = [
        {
            "role": "system",
            "content": "You are DataNova AI."
        },
        {
            "role": "user",
            "content": "Say hello."
        }
    ]

    response = LLMService.chat(messages)

    return response