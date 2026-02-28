#!/usr/bin/env python3
# fastapi/app/routers/auth.py

'''
endpoints:
    POST /auth/register          = student self-registration
    POST /auth/token             = login (all roles) → JWT
    GET  /auth/me                = current user profile
    POST /auth/admin/teachers    = admin creates a teacher account
    GET  /auth/login/google      = redirect to Google OAuth
    GET  /auth/google/callback   = Google OAuth callback

Follows: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
'''

import logging

from datetime import timedelta

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.auth import UserResponse, Message

from app.config import settings
from jose import jwt, JWTError

from httpx import AsyncClient

from app.config import settings
from app.db import get_db
from app.models.user import User
from app.models.social_auth import SocialAuth
from app.schemas.auth import StudentRegister, TeacherCreate, Token, UserResponse
from app.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# Google OAuth config
GOOGLE_CLIENT_ID = settings.google_client_id or ""
GOOGLE_CLIENT_SECRET = settings.google_client_secret or ""
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"


# student selfregistration

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_student(body: StudentRegister, db: Session = Depends(get_db)):
    '''
    - student register themselves with username, email, and password.
    - role is always set to 'student': teachers are created by admins only.
    '''
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code = 400, detail = "Username already taken")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code = 400, detail = "Email already registered")

    user = User(
        username = body.username,
        email = body.email,
        hashed_password = hash_password(body.password),
        full_name = body.full_name,
        role = "student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# login (all roles) -> JWT

@router.post("/token", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    '''
    - standard OAuth2 password flow
    - username field accepts either username or email
    - returns a Bearer JWT
    '''
    # allow login by username OR email
    user = (
        db.query(User).filter(User.username == form.username).first()
        or db.query(User).filter(User.email == form.username).first()
    )
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive account")

    token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


# current user

@router.get("/me", response_model = UserResponse)
def me(current_user: User = Depends(get_current_user)):
    '''return the profile of the currently logged-in user'''
    return current_user


# admin: create teacher account

@router.post(
    "/admin/teachers",
    response_model = UserResponse,
    status_code = status.HTTP_201_CREATED,
)
def create_teacher(
    body: TeacherCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    '''
    admin create a teacher account with username + password
    teacher cannt self register: they must be created here
    '''
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code = 400, detail = "Username already taken")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code = 400, detail = "Email already registered")

    teacher = User(
        username = body.username,
        email = body.email,
        hashed_password = hash_password(body.password),
        full_name = body.full_name,
        role = "teacher",
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


# Google SSO

@router.get("/login/google", include_in_schema=True)
def google_login(request: Request):
    '''redirect student to Google consent page'''
    redirect_uri = str(request.url_for("google_callback"))
    url = (
        f"{GOOGLE_AUTH_URL}?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=openid%20email%20profile"
    )
    return RedirectResponse(url)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    '''
    - Google OAuth callback: student only
    - Creates or updates the User row, then returns a JWT
    '''
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code = 400, detail = "Missing authorization code")

    async with AsyncClient() as client:
        # exchange code for access token
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": str(request.url_for("google_callback")),
                "grant_type": "authorization_code",
            },
        )
        token_data = token_resp.json()
        if "error" in token_data:
            raise HTTPException(status_code = 400, detail = token_data["error"])

        # Fetch Google profile
        profile_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers = {"Authorization": f"Bearer {token_data['access_token']}"},
        )
        profile = profile_resp.json()

    google_id = profile["id"]
    email = profile["email"]
    name = profile.get("name", "")

    # find existing SSO link
    social = db.query(SocialAuth).filter(
        SocialAuth.provider == "google",
        SocialAuth.provider_id == google_id,
    ).first()

    if social:
        user = social.user
    else:
        # find or create user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # auto-generate username from email prefix
            base = email.split("@")[0]
            username = base
            suffix = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base}{suffix}"
                suffix += 1

            user = User(
                username=username,
                email=email,
                full_name=name,
                role="student",
            )
            db.add(user)
            db.flush()

        db.add(SocialAuth(
            user_id=user.id,
            provider="google",
            provider_id=google_id,
        ))
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    # return token: frontend reads from redirect URL or JSON
    frontend_url = settings.frontend_login_success_uri
    return RedirectResponse(url=f"{frontend_url}?token={token}")

# Github SSO
    
GITHUB_CLIENT_ID = settings.github_client_id or ""
GITHUB_CLIENT_SECRET = settings.github_client_secret or ""
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"
GITHUB_EMAIL_URL = "https://api.github.com/user/emails"

@router.get("/login/github")
def github_login(request: Request):
    redirect_uri = str(request.url_for("github_callback"))
    url = (
        f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=user:email"
    )
    return RedirectResponse(url)

@router.get("/github/callback", name="github_callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code = 400, detail = "Missing authorization code")

    async with AsyncClient() as client:
        # exchange code for access token
        token_resp = await client.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code = 400, detail = "GitHub OAuth failed")

        # fetch profile
        profile_resp = await client.get(
            GITHUB_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile = profile_resp.json()

        # gitHub may not expose email publicly: fetch separately
        email = profile.get("email")
        if not email:
            email_resp = await client.get(
                GITHUB_EMAIL_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            emails = email_resp.json()
            primary = next((e for e in emails if e.get("primary") and e.get("verified")), None)
            if not primary:
                raise HTTPException(status_code=400, detail="No verified email on GitHub account")
            email = primary["email"]

    github_id = str(profile["id"])
    name = profile.get("name") or profile.get("login", "")

    # same upsert logic as Google
    social = db.query(SocialAuth).filter(
        SocialAuth.provider == "github",
        SocialAuth.provider_id == github_id,
    ).first()

    if social:
        user = social.user
    else:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            base = email.split("@")[0]
            username = base
            suffix = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base}{suffix}"
                suffix += 1
            user = User(username=username, email=email, full_name=name, role="student")
            db.add(user)
            db.flush()

        db.add(SocialAuth(user_id=user.id, provider="github", provider_id=github_id))
        db.commit()
        db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return RedirectResponse(url=f"{settings.frontend_login_success_uri}?token={token}")