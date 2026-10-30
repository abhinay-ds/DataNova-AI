import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, ExpiredSignatureError, jwt

from app.core.config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(
    user_id: int | str,
    is_guest: bool = False,
    guest_id: str | None = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload = {
        "sub": str(user_id),
        "is_guest": is_guest,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    if guest_id:
        payload["guest_id"] = guest_id

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_token_payload_with_status(token: str) -> tuple[dict | None, str]:
    """
    Decodes the JWT token and returns a tuple:
    - (payload_dict, "valid") if verified and unexpired.
    - (None, "expired") if signature is valid but has expired.
    - (None, "invalid") if malformed, corrupted, or signature verification failed.
    """
    if not token or not isinstance(token, str):
        return None, "invalid"

    token = token.strip()
    if not token:
        return None, "invalid"

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload, "valid"
    except ExpiredSignatureError:
        return None, "expired"
    except (JWTError, ValueError, TypeError):
        return None, "invalid"


def get_token_payload_for_refresh(token: str, max_age_days: int = 7) -> tuple[dict | None, str]:
    """
    Decodes the JWT token for refresh purposes.
    Accepts:
    1. Valid, unexpired tokens.
    2. Expired tokens if their signature is valid and expiration was within max_age_days.
    Returns:
    - (payload, "valid" | "expired") or (None, "invalid" | "too_old")
    """
    if not token or not isinstance(token, str):
        return None, "invalid"

    token = token.strip()
    if not token:
        return None, "invalid"

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload, "valid"
    except ExpiredSignatureError:
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"verify_exp": False},
            )
            exp = payload.get("exp")
            if exp:
                exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc)
                if datetime.now(timezone.utc) - exp_dt > timedelta(days=max_age_days):
                    return None, "too_old"
            return payload, "expired"
        except (JWTError, ValueError, TypeError):
            return None, "invalid"
    except (JWTError, ValueError, TypeError):
        return None, "invalid"


def decode_access_token_payload(token: str) -> dict | None:
    payload, _ = get_token_payload_with_status(token)
    return payload


def decode_access_token(token: str) -> int | None:
    payload = decode_access_token_payload(token)
    if not payload:
        return None

    subject = payload.get("sub")
    if subject is None:
        return None

    try:
        return int(subject)
    except (ValueError, TypeError):
        return None
