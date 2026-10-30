import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_current_user_for_refresh
from app.core.config import settings
from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    SignupRequest,
    UserResponse,
)
from app.services.jwt_service import create_access_token
from app.services.password_service import (
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db),
):

    existing_user = db.query(User).filter(
        User.email == request.email.lower()
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=request.email.lower(),
        password_hash=hash_password(
            request.password
        ),
        full_name=request.full_name,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_guest=False,
        ),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    user = db.query(User).filter(
        User.email == request.email.lower()
    ).first()

    if user is None or not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    token = create_access_token(user.id)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_guest=False,
        ),
    )


@router.post(
    "/demo",
    response_model=AuthResponse,
)
def demo_login(
    db: Session = Depends(get_db),
):
    """
    Idempotent one-click authentication for demo accounts.
    Creates or retrieves the demo user and preseeds a demo sample project.
    """
    demo_email = settings.DEMO_USER_EMAIL.lower()
    demo_user = db.query(User).filter(
        User.email == demo_email
    ).first()

    if not demo_user:
        demo_user = User(
            email=demo_email,
            password_hash=hash_password(settings.DEMO_USER_PASSWORD),
            full_name=settings.DEMO_USER_NAME,
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

    # Idempotently seed sample project for demo account
    sample_project = db.query(Project).filter(
        Project.owner_id == demo_user.id
    ).first()

    if not sample_project:
        sample_project = Project(
            name="Demo — E-Commerce Sales Insights",
            description="Preloaded portfolio dataset and AI analysis showcase.",
            owner_id=demo_user.id,
        )
        db.add(sample_project)
        db.commit()
        db.refresh(sample_project)

    token = create_access_token(demo_user.id)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=demo_user.id,
            email=demo_user.email,
            full_name=demo_user.full_name,
            is_guest=False,
        ),
    )


@router.post(
    "/guest",
    response_model=AuthResponse,
)
def guest_login():
    """
    Creates an isolated, ephemeral guest session.
    Zero permanent database records are created for guests.
    """
    guest_session_id = str(uuid.uuid4())[:8]
    token = create_access_token(
        user_id=0,
        is_guest=True,
        guest_id=guest_session_id,
    )

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=0,
            email="guest@datanova.ai",
            full_name="Guest Explorer",
            is_guest=True,
        ),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: Any = Depends(get_current_user),
):

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_guest=getattr(current_user, "is_guest", False),
    )


@router.post(
    "/refresh",
    response_model=AuthResponse,
)
def refresh_token(
    current_user: Any = Depends(get_current_user_for_refresh),
):
    """
    Refreshes an active session token or recently expired token within grace period,
    issuing a fresh access token with extended expiration.
    Supports registered, demo, and guest users.
    """
    is_guest = getattr(current_user, "is_guest", False)
    token = create_access_token(
        user_id=current_user.id,
        is_guest=is_guest,
    )
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            is_guest=is_guest,
        ),
    )

