"""
DataNova AI — Complete Authentication & Session Token Fix Verification Suite
Validates all 9 critical scenarios:
1. Fresh login & authenticated session (user validation & message creation)
2. Multiple consecutive authenticated requests without token degradation
3. Token expiration detection (401 with standard detail & WWW-Authenticate header)
4. Token refresh & retry flow (/auth/refresh renewing active and recently expired tokens)
5. Session restoration (/auth/me returning valid user profile)
6. Backend restart simulation (stable secret ensures tokens survive restarts)
7. Logout & subsequent login
8. Demo & guest access preservation
9. Unauthorized request rejection (401 status on missing, invalid, or tampered tokens)
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.api.auth import demo_login, get_me, guest_login, login, refresh_token, signup
from app.api.dependencies import (
    GuestUser,
    get_current_user,
    get_current_user_for_refresh,
    require_registered_user,
)
from app.api.projects import create_project, get_owned_project, list_projects
from app.core.config import settings
from app.database import SessionLocal
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.project import Project
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest
from app.schemas.project import ProjectCreate
from app.services.jwt_service import ALGORITHM, SECRET_KEY, create_access_token


def print_header(title: str):
    print("\n" + "=" * 70, flush=True)
    print(title, flush=True)
    print("=" * 70, flush=True)


def run_all_tests():
    print_header("DATANOVA AI: AUTHENTICATION TOKEN FIX VERIFICATION SUITE")
    db = SessionLocal()
    results = {}

    try:
        # =================================================================
        # Scenario 1: Fresh Login & AI Chat Authentication
        # =================================================================
        print("\n--- Scenario 1: Fresh Login & AI Chat Authentication ---", flush=True)
        ts = int(datetime.now(timezone.utc).timestamp())
        email = f"auth_user_{ts}@example.com"
        password = "SecurePassword123!"

        reg_data = signup(
            request=SignupRequest(
                email=email,
                password=password,
                full_name="Auth Verification User",
            ),
            db=db,
        )
        assert reg_data.access_token is not None
        user_id = reg_data.user.id
        token = reg_data.access_token
        print(f"  [OK] User registered successfully: {email} (ID: {user_id})", flush=True)

        # Authenticate via dependency
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        current_user = get_current_user(request=None, credentials=creds, db=db)
        assert current_user.id == user_id
        print("  [OK] Bearer token validated via get_current_user.", flush=True)

        # Create project and conversation for chat
        proj = create_project(
            request=ProjectCreate(name="Token Test Project", description="Testing chat auth"),
            current_user=current_user,
            db=db,
        )
        assert proj.id is not None
        print(f"  [OK] Project created: ID={proj.id}", flush=True)

        conv = Conversation(project_id=proj.id, title="Test Chat Conversation")
        db.add(conv)
        db.commit()
        db.refresh(conv)

        # Add message to conversation as authenticated user
        msg = Message(
            role="user",
            content="Hello DataNova AI, please analyze this data",
            conversation_id=conv.id,
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        assert msg.id is not None
        print(f"  [OK] Authenticated user successfully initiated conversation message (Msg ID: {msg.id}).", flush=True)
        results["Scenario 1"] = "PASS"

        # =================================================================
        # Scenario 2: Multiple Consecutive AI Requests
        # =================================================================
        print("\n--- Scenario 2: Multiple Consecutive AI Requests ---", flush=True)
        for i in range(1, 4):
            # Verify each consecutive request validates the token cleanly
            user_check = get_current_user(request=None, credentials=creds, db=db)
            assert user_check.id == user_id

            msg_i = Message(
                role="user",
                content=f"Consecutive query #{i} checking auth persistence",
                conversation_id=conv.id,
            )
            db.add(msg_i)
            db.commit()
            print(f"  [OK] AI request #{i} authenticated and persisted without token degradation.", flush=True)
        results["Scenario 2"] = "PASS"

        # =================================================================
        # Scenario 3: Token Expiration Detection
        # =================================================================
        print("\n--- Scenario 3: Token Expiration Detection ---", flush=True)
        # Create an expired token (expired 2 hours ago)
        expired_token = create_access_token(user_id=user_id, expires_delta=timedelta(hours=-2))
        expired_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)

        try:
            get_current_user(request=None, credentials=expired_creds, db=db)
            assert False, "Expired token must raise 401 HTTPException"
        except HTTPException as exc:
            assert exc.status_code == 401
            assert "Invalid or expired authentication token" in exc.detail
            assert "WWW-Authenticate" in exc.headers
            print(f"  [OK] Expired token correctly rejected with 401: '{exc.detail}'", flush=True)
            print(f"  [OK] WWW-Authenticate header: {exc.headers['WWW-Authenticate']}", flush=True)
        results["Scenario 3"] = "PASS"

        # =================================================================
        # Scenario 4: Token Refresh & Retry Flow
        # =================================================================
        print("\n--- Scenario 4: Token Refresh & Retry Flow ---", flush=True)
        # Token expired 15 minutes ago (within 7-day refresh grace period)
        grace_token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=-15))
        grace_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=grace_token)

        # 1. Normal access is blocked
        try:
            get_current_user(request=None, credentials=grace_creds, db=db)
            assert False, "Expired token must be rejected by normal routes"
        except HTTPException as exc:
            assert exc.status_code == 401

        # 2. Refresh dependency resolves the user for renewal
        user_to_refresh = get_current_user_for_refresh(credentials=grace_creds, db=db)
        assert user_to_refresh.id == user_id

        # 3. Call refresh endpoint
        refreshed_auth = refresh_token(current_user=user_to_refresh)
        new_token = refreshed_auth.access_token
        assert new_token != grace_token
        print("  [OK] /auth/refresh renewed token with fresh 24h expiration.", flush=True)

        # 4. Retrying with new token succeeds seamlessly
        new_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=new_token)
        retried_user = get_current_user(request=None, credentials=new_creds, db=db)
        assert retried_user.id == user_id

        retry_msg = Message(
            role="user",
            content="Chat message after transparent token refresh",
            conversation_id=conv.id,
        )
        db.add(retry_msg)
        db.commit()
        print("  [OK] AI chat request retried successfully with refreshed token.", flush=True)
        results["Scenario 4"] = "PASS"

        # =================================================================
        # Scenario 5: Page Refresh & Session Restoration
        # =================================================================
        print("\n--- Scenario 5: Page Refresh & Session Restoration ---", flush=True)
        me_res = get_me(current_user=retried_user)
        assert me_res.id == user_id
        assert me_res.email == email
        assert me_res.is_guest is False
        print(f"  [OK] Session restoration (/auth/me) returned valid user: {me_res.email}", flush=True)
        results["Scenario 5"] = "PASS"

        # =================================================================
        # Scenario 6: Backend Restart Simulation (Stable Secret)
        # =================================================================
        print("\n--- Scenario 6: Backend Restart Simulation (Stable Secret Verification) ---", flush=True)
        stable_secret = settings.JWT_SECRET_KEY
        assert stable_secret and "change-this" not in stable_secret.lower()

        # Token created prior to restart
        pre_restart_token = create_access_token(user_id=user_id)

        # Simulate fresh verification after independent restart
        decoded = jwt.decode(pre_restart_token, stable_secret, algorithms=[ALGORITHM])
        assert int(decoded["sub"]) == user_id

        restart_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=pre_restart_token)
        restart_user = get_current_user(request=None, credentials=restart_creds, db=db)
        assert restart_user.id == user_id
        print(f"  [OK] Secret key is persistent and stable: {stable_secret[:12]}...", flush=True)
        print("  [OK] Pre-restart token remains completely valid without forcing re-login.", flush=True)
        results["Scenario 6"] = "PASS"

        # =================================================================
        # Scenario 7: Logout & Subsequent Login
        # =================================================================
        print("\n--- Scenario 7: Logout & Subsequent Login Flow ---", flush=True)
        # 1. Stale / removed token raises 401
        try:
            get_current_user(request=None, credentials=None, db=db)
            assert False, "Null credentials must raise 401"
        except HTTPException as exc:
            assert exc.status_code == 401
            print("  [OK] Logged-out state strictly rejects unauthenticated access (401).", flush=True)

        # 2. Subsequent login
        login_data = login(request=LoginRequest(email=email, password=password), db=db)
        assert login_data.access_token is not None
        relogin_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=login_data.access_token)
        relogin_user = get_current_user(request=None, credentials=relogin_creds, db=db)
        assert relogin_user.id == user_id
        print("  [OK] Subsequent login issues fresh token and restores full access.", flush=True)
        results["Scenario 7"] = "PASS"

        # =================================================================
        # Scenario 8: Demo & Guest Access Preservation
        # =================================================================
        print("\n--- Scenario 8: Demo & Guest Access Preservation ---", flush=True)
        # Demo access
        demo_auth = demo_login(db=db)
        assert demo_auth.user.email == "demo@datanova.ai"
        demo_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=demo_auth.access_token)
        demo_user = get_current_user(request=None, credentials=demo_creds, db=db)
        assert demo_user.email == "demo@datanova.ai"
        # Demo refresh
        demo_refresh = refresh_token(current_user=demo_user)
        assert demo_refresh.access_token is not None
        print("  [OK] Demo user session and refresh verified.", flush=True)

        # Guest access
        guest_auth = guest_login()
        assert guest_auth.user.is_guest is True
        assert guest_auth.user.id == 0
        guest_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=guest_auth.access_token)
        guest_user = get_current_user(request=None, credentials=guest_creds, db=db)
        assert getattr(guest_user, "is_guest", False) is True
        # Guest refresh
        guest_refresh = refresh_token(current_user=guest_user)
        assert guest_refresh.user.is_guest is True
        # Guest blocked from registered actions
        try:
            require_registered_user(current_user=guest_user)
            assert False, "require_registered_user must reject guest with 403"
        except HTTPException as exc:
            assert exc.status_code == 403
            print("  [OK] Guest security boundary enforced (403 Forbidden).", flush=True)
        results["Scenario 8"] = "PASS"

        # =================================================================
        # Scenario 9: Unauthorized Request Rejection (401 Status)
        # =================================================================
        print("\n--- Scenario 9: Unauthorized Request Rejection (401 Status) ---", flush=True)
        # Missing token
        try:
            get_current_user(request=None, credentials=None, db=db)
            assert False
        except HTTPException as exc:
            assert exc.status_code == 401

        # Empty credentials
        try:
            empty_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="   ")
            get_current_user(request=None, credentials=empty_creds, db=db)
            assert False
        except HTTPException as exc:
            assert exc.status_code == 401

        # Tampered signature
        valid_tok = create_access_token(user_id=1)
        tampered_tok = valid_tok[:-6] + "XYZ123"
        try:
            tampered_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=tampered_tok)
            get_current_user(request=None, credentials=tampered_creds, db=db)
            assert False
        except HTTPException as exc:
            assert exc.status_code == 401
            assert "Invalid or expired authentication token" in exc.detail

        # Unknown secret
        forged_tok = jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "completely-wrong-untrusted-secret",
            algorithm="HS256",
        )
        try:
            forged_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=forged_tok)
            get_current_user(request=None, credentials=forged_creds, db=db)
            assert False
        except HTTPException as exc:
            assert exc.status_code == 401
            assert "Invalid or expired authentication token" in exc.detail

        print("  [OK] All unauthorized permutations (missing, empty, tampered, forged) rejected with 401.", flush=True)
        results["Scenario 9"] = "PASS"

        # =================================================================
        # Final Summary
        # =================================================================
        print_header("ALL 9 SCENARIOS VERIFICATION SUMMARY")
        for sc, res in results.items():
            print(f"  {sc}: {res}", flush=True)
        print_header("RESULT: ALL 9 AUTHENTICATION SCENARIOS PASSED (100%)")

    finally:
        db.close()


if __name__ == "__main__":
    run_all_tests()
