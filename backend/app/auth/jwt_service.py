from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt


SECRET_KEY = "CHANGE_THIS_TO_A_RANDOM_SECRET"

ALGORITHM = "HS256"

ACCESS_TOKEN_MINUTES = 60

REMEMBER_ME_DAYS = 30


def create_access_token(
    user_id: int,
    remember_me: bool = False,
) -> str:

    if remember_me:
        expires_delta = timedelta(
            days=REMEMBER_ME_DAYS
        )
    else:
        expires_delta = timedelta(
            minutes=ACCESS_TOKEN_MINUTES
        )

    expire = (
        datetime.now(timezone.utc)
        + expires_delta
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> int | None:

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")

        if subject is None:
            return None

        return int(subject)

    except (
        JWTError,
        ValueError,
        TypeError,
    ):
        return None