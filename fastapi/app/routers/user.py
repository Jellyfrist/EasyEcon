'''
self-service profile routes: any authenticated user can call these.

what each role sees and can edit:

    student:
        - email     : shown, read-only (just for display)
        - username  : shown, editable
        - password  : editable (just change, not shown)

    teacher:
        - full_name : shown, read-only
        - email     : shown, read-only
        - username  : shown, read-only (just for display)
        - password  : shown, read-only (just for display)
        - nothing is editable (admin manages teacher accounts)

    note on teacher login:
        - teacher logs in with username or email + password (set by admin)
        - email is stored so admin knows who to contact
        - email can be used to log in
        - when teacher publishes content, full_name is shown (not username)

routes:
    GET   /users/me          get own profile (shape depends on role)
    PATCH /users/me          student updates username
    PATCH /users/me/password student changes password
'''

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db import get_db
from app.models.user import User
from app.security import get_current_user, hash_password

from app.schemas.user import (
    StudentProfileResponse,
    TeacherProfileResponse,
    StudentUpdate,
    PasswordUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])

# get own profile
@router.get("/me")
def get_profile(
    current_user: User = Depends(get_current_user),
):
    '''
    returns profile fields based on role:
    - student: id, username, email (read-only), role
    - teacher: id, full_name, email (read-only), role
    '''
    if current_user.role == "student":
        return StudentProfileResponse.model_validate(current_user)

    # teacher and admin
    return TeacherProfileResponse.model_validate(current_user)


# student updates username
@router.patch("/me")
def update_profile(
    body: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    '''
    only students can update their username.
    teachers cannot edit anything here: admin manages their account.
    '''
    if current_user.role != "student":
        raise HTTPException(
            status_code=403,
            detail="teacher accounts are managed by admin, so cannot edit your profile here",
        )

    # nothing to update
    if body.username is None:
        return StudentProfileResponse.model_validate(current_user)

    # check username is not taken by another user
    taken = db.query(User).filter(
        User.username == body.username,
        User.id != current_user.id,
    ).first()
    if taken:
        raise HTTPException(status_code=400, detail="username already taken")

    current_user.username = body.username
    db.commit()
    db.refresh(current_user)
    return StudentProfileResponse.model_validate(current_user)


# student changes password
@router.patch("/me/password")
def change_password(
    body: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    '''
    only students can change their own password.
    teacher passwords are managed by admin only
    (admin uses POST /admin/invite-teacher or PATCH /admin/users/{id}/role to reset).
    '''
    if current_user.role != "student":
        raise HTTPException(
            status_code=403,
            detail="teacher passwords are managed by admin, please contact your administrator",
        )

    current_user.hashed_password = hash_password(body.new_password)
    db.commit()
    return {"message": "password updated successfully"}