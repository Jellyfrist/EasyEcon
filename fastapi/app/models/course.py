from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import BigInteger, Integer, Identity, String, Text, Boolean, DateTime, ForeignKeyConstraint, Index
from sqlalchemy.orm import mapped_column, relationship, synonym
from sqlalchemy.ext.hybrid import hybrid_property
from app.db import Base

BIGINT = BigInteger().with_variant(Integer, "sqlite")

def now_utc():
    return datetime.now(timezone.utc)


class Course(Base):
    __tablename__ = 'course'
    id = mapped_column('course_id', BIGINT, Identity(always=False), primary_key=True, nullable=False)
    course_id = synonym('id')
    teacher_id = mapped_column('owner_teacher_id', BIGINT, nullable=False)
    owner_teacher_id = synonym('teacher_id')
    title = mapped_column('title', String(50), nullable=False)
    _description = mapped_column('description', Text, nullable=False, default='')
    created_at = mapped_column('created_at', DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = mapped_column('updated_at', DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)
    __table_args__ = (
        ForeignKeyConstraint(['owner_teacher_id'], ['app_user.user_id'], ondelete='RESTRICT'),
        Index('course_owner_idx','owner_teacher_id'),
    )

    description_was_null = mapped_column(Boolean, nullable=False, default=True)
    teacher = relationship("User", back_populates="courses", foreign_keys=[teacher_id])
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    topics = relationship("Topic", cascade="all, delete-orphan")
    all_exams = relationship("ExamTemplate", back_populates="course", cascade="all, delete-orphan")

    @property
    def exam_templates(self):
        return [exam for exam in self.all_exams if exam.source_template_id is None]

    @hybrid_property
    def description(self):
        return None if self.description_was_null else self._description

    @description.setter
    def description(self, value):
        self.description_was_null = value is None
        self._description = value if value is not None else ""

    @description.expression
    def description(cls):
        return cls._description
