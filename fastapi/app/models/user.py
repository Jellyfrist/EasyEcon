'''
user.py = every person in system

3 roles
- student = self-register via email/password OR Google/GitHub SSO
- teacher = created by an admin (username + password only)
- admin = seed manually or promote by another admin

password is hash by bcrypt

have csrf protection
'''

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

UTC = timezone.utc

if TYPE_CHECKING:
    from .social_auth import SocialAuth
    from .course import Course
    from .learning_page import LearningPage
    from .flashcard import FlashcardProgress
    from .best_attempt import BestAttempt
    from .exam_attempt import ExamAttempt
    from .exam_session import ExamSession
    from .exam_template import ExamTemplate
    from .page_progress import PageProgress

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    username: Mapped[str] = mapped_column(String(50), unique = True, index = True, nullable = False)
    
    email: Mapped[str] = mapped_column(String(100), unique = True, index = True, nullable = False)
    hashed_password: Mapped[Optional[str]] = mapped_column(
        String(255), nullable = True,
        # nullable = True because when user authenticates via SSO
    )

    # role: student / teacher / admin
    role: Mapped[str] = mapped_column(String(20), default = "student", nullable = False)
    is_active: Mapped[bool] = mapped_column(Boolean, default = True)

    # profile
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable = True)

    # teacher account tracking
    email_sent: Mapped[bool] = mapped_column(Boolean, default = False)

    #vertify mail
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    '''
    relationship
    '''

    # SSO login (Google / GitHub)
    social_accounts: Mapped[List["SocialAuth"]] = relationship(
        back_populates = "user", cascade = "all, delete-orphan"
    )

    # teacher: create course, learning page, exam, launch session
    courses: Mapped[List["Course"]] = relationship(back_populates = "teacher")
    created_pages: Mapped[List["LearningPage"]] = relationship(
        back_populates = "creator",
        foreign_keys = "LearningPage.created_by_user_id",
    )
    exam_templates: Mapped[List["ExamTemplate"]] = relationship(
        back_populates = "creator",
        foreign_keys = "ExamTemplate.created_by_user_id",
    )
    launched_sessions: Mapped[List["ExamSession"]] = relationship(
        back_populates = "launched_by",
        foreign_keys = "ExamSession.launched_by_user_id",
    )

    progress_records: Mapped[List["PageProgress"]] = relationship(
        back_populates="student",
        foreign_keys="PageProgress.student_id"
    )

    # student: flashcard, mini quiz attempts, best mini quiz attempt, exam attempts
    flashcard_progress: Mapped[List["FlashcardProgress"]] = relationship(
        back_populates = "student",
        foreign_keys="FlashcardProgress.student_id",
    )
    best_attempt: Mapped[List["BestAttempt"]] = relationship(
        back_populates="student",
        foreign_keys="BestAttempt.student_id",
    )
    exam_attempts: Mapped[List["ExamAttempt"]] = relationship(
        back_populates="student",
        foreign_keys="ExamAttempt.student_id",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"