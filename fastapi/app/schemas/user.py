from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, field_validator

class StudentProfileResponse(BaseModel):
    '''fields shown to a student on their settings page'''
    id: int
    username: str
    password: str     # shown as "********", not editable
    email: str        # shown but not editable
    role: str

    model_config = {"from_attributes": True}

class TeacherProfileResponse(BaseModel):
    '''fields shown to a teacher on their settings page'''
    id: int
    username: str             # shown, read-only (just for display, not editable)
    password: str             # shown, read-only (just for display, not editable)
    full_name: Optional[str]  # shown as display name on published content
    email: str                # shown, read-only
    role: str

    model_config = {"from_attributes": True}

# input schemas
class StudentUpdate(BaseModel):
    username: Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: Optional[str]) -> Optional[str]:
        # reject blank string but allow None (means no change)
        if v is not None and not v.strip():
            raise ValueError("username cannot be empty")
        return v

class PasswordUpdate(BaseModel):
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_long_enough(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v