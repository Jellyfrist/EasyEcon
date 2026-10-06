from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from sqlalchemy import BigInteger, Integer, Identity, String, Text, DateTime, ForeignKeyConstraint, CheckConstraint, Index, select, text
from sqlalchemy.orm import mapped_column, relationship, synonym
from sqlalchemy.ext.hybrid import hybrid_property
from app.db import Base

BIGINT = BigInteger().with_variant(Integer, "sqlite")

def now_utc():
    return datetime.now(timezone.utc)


class ExamSession(Base):
    __tablename__ = 'exam_session'
    id = mapped_column('session_id', BIGINT, Identity(always=False), primary_key=True, nullable=False)
    session_id = synonym('id')
    exam_id = mapped_column('exam_id', BIGINT, nullable=False)
    launched_by_user_id = mapped_column('opened_by_teacher_id', BIGINT, nullable=False)
    opened_by_teacher_id = synonym('launched_by_user_id')
    launched_at = mapped_column('opened_at', DateTime(timezone=True), nullable=False, default=now_utc)
    opened_at = synonym('launched_at')
    closed_at = mapped_column('closed_at', DateTime(timezone=True), nullable=True)
    _max_attempts = mapped_column('max_attempts', Integer, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['exam_id'], ['exam.exam_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['opened_by_teacher_id'], ['app_user.user_id'], ondelete='RESTRICT'),
        CheckConstraint('max_attempts IS NULL OR max_attempts > 0'),
        CheckConstraint('closed_at IS NULL OR closed_at >= opened_at'),
        Index('session_exam_idx', 'exam_id'),
        Index("exam_session_one_open_per_exam", "exam_id", unique=True, postgresql_where=text("closed_at IS NULL"), sqlite_where=text("closed_at IS NULL")),
    )

    title = mapped_column(String(200), nullable=False)
    instructions = mapped_column(Text)
    available_from = mapped_column(DateTime(timezone=True))
    available_until = mapped_column(DateTime(timezone=True))
    time_limit_minutes = mapped_column(Integer)
    assessment = relationship("ExamTemplate", back_populates="sessions", foreign_keys=[exam_id])
    launched_by = relationship("User", back_populates="launched_sessions", foreign_keys=[launched_by_user_id])
    attempts = relationship("ExamAttempt", back_populates="session", cascade="all, delete-orphan")

    @hybrid_property
    def template_id(self):
        if hasattr(self,"_template_id"):
            return self._template_id
        return self.assessment.source_template_id or self.exam_id if self.assessment else self.exam_id

    @template_id.setter
    def template_id(self, value):
        self._template_id=value

    @template_id.expression
    def template_id(cls):
        from .exam_template import ExamTemplate
        from sqlalchemy import func
        return select(func.coalesce(ExamTemplate.source_template_id,ExamTemplate.id)).where(ExamTemplate.id==cls.exam_id).correlate(cls).scalar_subquery()

    @property
    def template(self):
        return self.assessment.source_template or self.assessment if self.assessment else None

    @property
    def questions(self):
        return self.assessment.questions if self.assessment else []

    @property
    def question_snapshot(self):
        return self.__dict__.get("_question_snapshot",self.assessment.question_data if self.assessment else [])

    @question_snapshot.setter
    def question_snapshot(self, value):
        self._question_snapshot=deepcopy(value or [])

    @hybrid_property
    def is_active(self):
        return self.closed_at is None

    @is_active.setter
    def is_active(self, value):
        if not value:
            self.closed_at=now_utc()
        else:
            self.closed_at=None

    @is_active.expression
    def is_active(cls):
        return cls.closed_at.is_(None)

    @is_active.update_expression
    def is_active(cls,value):
        return [(cls.closed_at,None if value else now_utc())]

    @property
    def max_attempts(self):
        return self._max_attempts if self._max_attempts is not None else 0

    @max_attempts.setter
    def max_attempts(self,value):
        self._max_attempts=None if value in (None,0) else value

    @property
    def is_open(self):
        def utc(v):return v.replace(tzinfo=timezone.utc) if v is not None and v.tzinfo is None else v
        now=now_utc()
        return self.is_active and (self.available_from is None or now>=utc(self.available_from)) and (self.available_until is None or now<=utc(self.available_until))
