'''
exam session = a launched copy of an exam templete sent to students

analogous to clicking "Send" in Google Forms

one template can be launched multiple times e.g. different classes, makeup exams, retakes

the session stores a snapshot of question_data at launch time so that
teachers can later edit the template without affecting in-progress sessions
'''

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

from __future__ import annotations

UTC = timezone.utc

if TYPE_CHECKING:
    from .exam_template import ExamTemplate
    from .user import User
    from .exam_attempt import ExamAttempt


class ExamSession(Base):
    '''
    an exam launched from a template.
    students submit exam attempts against this session.
    '''

    __tablename__ = "exam_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)

    # source template
    template_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exam_templates.id"), nullable = False
    )

    # design: questions are embedded here. (not in DB)
    # Copy of template.question_data taken at launch
    # Ensures grading is consistent even if the template is later edited
    question_snapshot: Mapped[list] = mapped_column(
        JSON, nullable = False, default=list,
    )

    # session info
    title: Mapped[str] = mapped_column(String(200), nullable = False)
    instructions: Mapped[str] = mapped_column(Text, nullable = True)

    # access window
    available_from: Mapped[datetime] = mapped_column(DateTime, nullable = True)
    available_until: Mapped[datetime] = mapped_column(DateTime, nullable = True)

    # override settings (inherit from template if None)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, nullable = True)
    max_attempts: Mapped[int] = mapped_column(
        Integer, default = 1
    )

    # lifecycle
    is_active: Mapped[bool] = mapped_column(Boolean, default = True)
    launched_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable = False
    )
    launched_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    '''
    relationship
    '''
    template: Mapped["ExamTemplate"] = relationship(
        "ExamTemplate", back_populates = "sessions"
    )
    launched_by: Mapped["User"] = relationship(
        "User", foreign_keys = [launched_by_user_id], back_populates = "launched_sessions"
    )
    attempts: Mapped[List["ExamAttempt"]] = relationship(
        "ExamAttempt", back_populates = "session", cascade = "all, delete-orphan"
    )

    # helper
    @property
    def is_open(self) -> bool:
        '''True if the session is currently accepting submissions'''
        now = datetime.now(UTC)
        if not self.is_active:
            return False
        if self.available_from and now < self.available_from:
            return False
        if self.available_until and now > self.available_until:
            return False
        return True

    def __repr__(self) -> str:
        return f"<ExamSession(id={self.id}, title='{self.title}', active={self.is_active})>"