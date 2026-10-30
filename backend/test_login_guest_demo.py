import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from jose import jwt

sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.database import SessionLocal, get_db
from app.models.user import User
from app.models.project import Project
from app.api.auth import demo_login, guest_login, login, signup
from app.schemas.auth import LoginRequest, SignupRequest
from app.api.dependencies import get_current_user, require_registered_user
from app.api.projects import list_projects, create_project, get_owned_project
from app.schemas.project import ProjectCreate
from app.services.jwt_service import create_access_token, decode_access_token_payload
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import HTTPException

def test_all():
    print("==================================================", flush=True)
    print("DATANOVA AI: LOGIN, DEMO & GUEST ACCESS VERIFICATION", flush=True)
    print("==================================================", flush=True)

    db = SessionLocal()
    try:
        # 1. Normal Registration & Login
        print("\n[1] Testing Normal Registration & Login...", flush=True)
        unique_email = f"test_{int(datetime.utcnow().timestamp())}@example.com"
        reg_res = signup(
            request=SignupRequest(
                email=unique_email,
                password="TestPassword@123",
                full_name="Standard User",
            ),
            db=db,
        )
        assert reg_res.access_token is not None
        assert reg_res.user.email == unique_email
        assert reg_res.user.is_guest is False
        print("-> User registration successful:", reg_res.user.email, flush=True)

        login_res = login(
            request=LoginRequest(
                email=unique_email,
                password="TestPassword@123",
            ),
            db=db,
        )
        assert login_res.access_token is not None
        assert login_res.user.id == reg_res.user.id
        print("-> User login successful!", flush=True)

        # 2. Invalid Login & Passwords
        print("\n[2] Testing Invalid Credentials Handling...", flush=True)
        try:
            login(
                request=LoginRequest(
                    email=unique_email,
                    password="WrongPassword!999",
                ),
                db=db,
            )
            assert False, "Should have raised 401 for wrong password"
        except HTTPException as exc:
            assert exc.status_code == 401
            print("-> Invalid password properly returns 401 Unauthorized:", exc.detail, flush=True)

        # 3. One-Click Demo Account Login
        print("\n[3] Testing One-Click Demo Account (/auth/demo)...", flush=True)
        demo_res = demo_login(db=db)
        assert demo_res.access_token is not None
        assert demo_res.user.email == settings.DEMO_USER_EMAIL.lower()
        assert demo_res.user.is_guest is False
        demo_user_id = demo_res.user.id
        print(f"-> Demo login succeeded! User ID: {demo_user_id}, Email: {demo_res.user.email}", flush=True)

        # Verify demo user has preseeded project
        demo_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=demo_res.access_token)
        demo_current_user = get_current_user(request=None, credentials=demo_creds, db=db)
        demo_projects = list_projects(current_user=demo_current_user, db=db)
        assert len(demo_projects) >= 1
        print(f"-> Demo user preseeded project verified: '{demo_projects[0].name}'", flush=True)

        # Verify direct login with demo credentials also works
        demo_direct = login(
            request=LoginRequest(
                email=settings.DEMO_USER_EMAIL,
                password=settings.DEMO_USER_PASSWORD,
            ),
            db=db,
        )
        assert demo_direct.user.id == demo_user_id
        print("-> Direct login with demo credentials verified!", flush=True)

        # 4. Guest Access (/auth/guest)
        print("\n[4] Testing Guest Session (/auth/guest)...", flush=True)
        # Check initial user count in DB
        initial_users_count = db.query(User).count()

        guest_res = guest_login()
        assert guest_res.access_token is not None
        assert guest_res.user.id == 0
        assert guest_res.user.is_guest is True
        assert guest_res.user.email == "guest@datanova.ai"

        # Check DB user count: must NOT have increased!
        after_guest_users_count = db.query(User).count()
        assert initial_users_count == after_guest_users_count, "Guest login must not create permanent DB user rows"
        print(f"-> Guest session created! ID: {guest_res.user.id}, is_guest: {guest_res.user.is_guest}", flush=True)
        print("-> Zero database rows created for guest (Database pollution check: PASS)", flush=True)

        # 5. Guest Permissions & Isolation Enforcement
        print("\n[5] Testing Guest Authorization & Boundary Enforcement...", flush=True)
        guest_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=guest_res.access_token)
        guest_current_user = get_current_user(request=None, credentials=guest_creds, db=db)
        assert guest_current_user.is_guest is True

        # 5a. Projects list for guest must be empty
        guest_proj_list = list_projects(current_user=guest_current_user, db=db)
        assert len(guest_proj_list) == 0, "Guest must see 0 projects"
        print("-> Guest projects list isolated: 0 projects returned", flush=True)

        # 5b. Project creation must be blocked with 403 Forbidden
        try:
            create_project(
                request=ProjectCreate(name="Guest Forbidden Project"),
                current_user=guest_current_user,
                db=db,
            )
            assert False, "Guest project creation must be rejected"
        except HTTPException as exc:
            assert exc.status_code == 403
            print(f"-> Guest project creation strictly blocked with 403: {exc.detail}", flush=True)

        # 5c. require_registered_user must reject guest with 403
        try:
            require_registered_user(current_user=guest_current_user)
            assert False, "require_registered_user must reject guest"
        except HTTPException as exc:
            assert exc.status_code == 403
            print(f"-> require_registered_user guard blocked guest: {exc.detail}", flush=True)

        # 5d. Guest cannot access demo project (404)
        try:
            get_owned_project(
                project_id=demo_projects[0].id,
                current_user=guest_current_user,
                db=db,
            )
            assert False, "Guest must not access demo project"
        except HTTPException as exc:
            assert exc.status_code == 404
            print(f"-> Guest accessing demo project safely blocked with 404: {exc.detail}", flush=True)

        # 6. Session Expiration & Invalid Tokens
        print("\n[6] Testing Token Expiration & Tampering...", flush=True)
        # Expired token
        expired_token = jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=5)},
            settings.JWT_SECRET_KEY,
            algorithm="HS256",
        )
        expired_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)
        try:
            get_current_user(request=None, credentials=expired_creds, db=db)
            assert False, "Expired token must be rejected"
        except HTTPException as exc:
            assert exc.status_code == 401
            print("-> Expired token correctly rejected with 401:", exc.detail, flush=True)

        # Tampered token
        tampered_creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.here")
        try:
            get_current_user(request=None, credentials=tampered_creds, db=db)
            assert False, "Tampered token must be rejected"
        except HTTPException as exc:
            assert exc.status_code == 401
            print("-> Tampered token correctly rejected with 401:", exc.detail, flush=True)

        # Clean up test user
        test_u = db.query(User).filter(User.email == unique_email).first()
        if test_u:
            db.delete(test_u)
            db.commit()

        print("\n==================================================", flush=True)
        print(">>> 100% OF AUTH, DEMO & GUEST TESTS PASSED! <<<", flush=True)
        print("==================================================", flush=True)

    finally:
        db.close()

if __name__ == "__main__":
    test_all()
