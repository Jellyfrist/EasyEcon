'''
JWT authentication

match JWTAndCSRFMiddleware in app/__init__.py:
  - token is read from the "jwt" cookie
  - CSRF token is embedded in the JWT payload as "csrf_token"
  - frontend must send X-CSRF-Token header on POST/PUT/DELETE requests

note: JWT authentication following https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
'''

import logging
import secrets

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

# password helper
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# JWT helper
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    '''
    creates a JWT with:
        - "sub"        : user id (str)
        - "role"       : user role
        - "csrf_token" : random hex - matched by JWTAndCSRFMiddleware
        - "exp"        : expiry timestamp

    frontend flow:
        1. after login, backend sets "jwt" cookie + returns csrf_token in JSON body
        2. frontend stores csrf_token (e.g. in memory or localStorage)
        3. frontend sends X-CSRF-Token: <csrf_token> header on every POST/PUT/DELETE
    '''
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({
        "exp": expire,
        "csrf_token": secrets.token_hex(16),
    })
    return jwt.encode(payload, SECRET_KEY, algorithm = ALGORITHM)

# current user depency
def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    '''
    - reads JWT from "jwt" cookie
    - raises 401 for missing / invalid / expired token
    '''
    credentials_exc = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
    )

    token = request.cookies.get("jwt")
    if not token:
        raise credentials_exc

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc
    
    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exc
    return user

# role
def require_student(current_user: User = Depends(get_current_user)) -> User:
    '''any authenticated active user can access student route'''
    return current_user


def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    '''only teachers and admins can access teacher route'''
    if current_user.role not in ("teacher", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher account required",
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    '''only admins can access admin route'''
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account required",
        )
    return current_user