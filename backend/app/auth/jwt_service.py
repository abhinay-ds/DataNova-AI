"""
DataNova AI Authentication — JWT Service Re-export
Guarantees consistent secret key, algorithm, expiration, and validation logic.
"""

from app.services.jwt_service import (
    ALGORITHM,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_access_token,
    decode_access_token_payload,
    get_token_payload_with_status,
)

__all__ = [
    "ALGORITHM",
    "SECRET_KEY",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "create_access_token",
    "decode_access_token",
    "decode_access_token_payload",
    "get_token_payload_with_status",
]
