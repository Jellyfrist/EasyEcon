'''
admin-only routes for managing users and teachers.

routes:
    GET    /admin/users                                 list all users (with optional role filter)
    PATCH  /admin/users/{user_id}/role                  change a user's role
    PATCH  /admin/users/{user_id}/deactivate            deactivate a user account
    POST   /admin/teachers/invite                       create teacher + auto-generate credentials + send email
    POST   /admin/teachers/{user_id}/send-credentials   reset password + resend credentials email

teacher invite flow:
    1. admin fills in full_name + email only
    2. system generates username from first name + 4 random digits (e.g. john4821)
    3. system generates a random 12-character password
    4. teacher account is created
    5. email is sent immediately with username + password
    6. teacher logs in via POST /auth/token using username + password
'''

import random
import secrets
import string

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User
from app.schemas.auth import TeacherInvite, UserResponse
from app.security import hash_password, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

ALLOWED_ROLES = ("student", "teacher", "admin")

# mail helper
def _get_mail_client() -> FastMail:
    '''build fastmail client from settings, raises 500 if not configured'''
    if not settings.mail_username or not settings.mail_password or not settings.mail_from:
        raise HTTPException(
            status_code=500,
            detail=(
                "mail not configured. "
                "set MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM in .env"
            ),
        )
    conf = ConnectionConfig(
        MAIL_USERNAME = settings.mail_username,
        MAIL_PASSWORD = settings.mail_password,
        MAIL_FROM = settings.mail_from,
        MAIL_PORT = settings.mail_port,
        MAIL_SERVER = settings.mail_server,
        MAIL_STARTTLS = True,
        MAIL_SSL_TLS = False,
        USE_CREDENTIALS = True,
    )
    return FastMail(conf)

def _generate_username(full_name: str, db: Session) -> str:
    '''
    generate a unique username from the first word of full_name + 4 random digits.
    e.g. "John Smith" -> "john4821"
    retries until a unique username is found.
    '''
    # take first word, lowercase, keep only letters
    first_name = full_name.strip().split()[0].lower()
    first_name = "".join(c for c in first_name if c.isalpha())

    # fallback if full_name has no letters (very rare edge case)
    if not first_name:
        first_name = "teacher"

    # retry until unique
    for _ in range(10):
        suffix = random.randint(1000, 9999)
        username = f"{first_name}{suffix}"
        if not db.query(User).filter(User.username == username).first():
            return username

    # if all 10 tries collide (extremely unlikely), raise an error
    raise HTTPException(
        status_code = 500,
        detail = "could not generate a unique username, please try again",
    )


def _generate_password() -> str:
    '''generate a random 12-character password with letters and digits'''
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(12))

# list all users
@router.get("/users", response_model = List[UserResponse])
def list_users(
    role: Optional[str] = Query(None, description = "filter by role: student, teacher, admin"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    '''admin views all user accounts, optionally filtered by role'''
    query = db.query(User)
    if role:
        if role not in ALLOWED_ROLES:
            raise HTTPException(status_code = 400, detail = f"role must be one of {ALLOWED_ROLES}")
        query = query.filter(User.role == role)
    return query.order_by(User.id).all()


# change user role
@router.patch("/users/{user_id}/role", response_model = UserResponse)
def change_user_role(
    user_id: int,
    role: str = Query(..., description="new role: student, teacher, admin"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    '''admin promotes or demotes a user'''
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code = 400, detail = f"role must be one of {ALLOWED_ROLES}")

    # prevent admin from removing their own admin role
    if user_id == admin.id and role != "admin":
        raise HTTPException(status_code = 400, detail = "you cannot remove your own admin role")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code = 404, detail = "user not found")

    user.role = role
    db.commit()
    db.refresh(user)
    return user

# deactivate user
@router.patch("/users/{user_id}/deactivate", response_model = UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    '''
    admin deactivates a user account (soft delete).
    deactivated users cannot log in.
    use this instead of deleting to keep data history.
    '''
    if user_id == admin.id:
        raise HTTPException(status_code = 400, detail = "you cannot deactivate yourself")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code = 404, detail = "user not found")

    user.is_active = False
    db.commit()
    db.refresh(user)
    return user

# invite teacher: auto-generate username + password + send email immediately
@router.post("/teachers/invite", response_model = UserResponse, status_code = 201)
async def invite_teacher(
    body: TeacherInvite,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    '''
    admin provides full_name + email only.
    system handles everything else automatically:
        - username: first name + 4 random digits (e.g. john4821)
        - password: random 12-character string
        - email: sent immediately with login credentials
    '''
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code = 400, detail = "email already registered")

    username = _generate_username(body.full_name, db)
    password = _generate_password()

    teacher = User(
        username = username,
        email = body.email,
        hashed_password = hash_password(password),
        full_name = body.full_name,
        role = "teacher",
        email_sent = True,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    # send credentials immediately in the background
    fm = _get_mail_client()
    message = MessageSchema(
        subject = "EasyEcon: your teacher account is ready",
        recipients = [body.email],
        body=(
            f"Hello {body.full_name},\n\n"
            f"Your teacher account on EasyEcon has been created.\n\n"
            f"Username : {username}\n"
            f"Password : {password}\n\n"
            f"Login at: {settings.frontend_login_success_uri.replace('/login-success', '/login')}\n\n"
            f"Please log in with your username, not this email address."
        ),
        subtype="plain",
    )
    background_tasks.add_task(fm.send_message, message)

    return teacher

# resend credentials: reset password + send new email
@router.post("/teachers/{user_id}/send-credentials", response_model=UserResponse)
async def send_credentials(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    '''
    resets the teacher's password to a new auto-generated one and resends the email.
    use this when a teacher loses their credentials.
    '''
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code = 404, detail = "user not found")
    if user.role != "teacher":
        raise HTTPException(status_code = 400, detail = "this action is only for teacher accounts")

    # generate new password and replace the old one
    new_password = _generate_password()
    user.hashed_password = hash_password(new_password)
    user.email_sent = True
    db.commit()
    db.refresh(user)

    fm = _get_mail_client()
    message = MessageSchema(
        subject = "EasyEcon: your login credentials have been reset",
        recipients = [user.email],
        body=(
            f"Hello {user.full_name or user.username},\n\n"
            f"Your EasyEcon account credentials have been reset.\n\n"
            f"Username : {user.username}\n"
            f"Password : {new_password}\n\n"
            f"Login at: {settings.frontend_login_success_uri.replace('/login-success', '/login')}\n\n"
            f"Please log in with your username, not this email address."
        ),
        subtype="plain",
    )
    background_tasks.add_task(fm.send_message, message)

    return user