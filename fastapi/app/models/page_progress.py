from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Integer, Boolean, DateTime, ForeignKeyConstraint, CheckConstraint, text
from sqlalchemy.orm import mapped_column, relationship, synonym
from app.db import Base


def now_utc():
    return datetime.now(timezone.utc)


class PageProgress(Base):
    __tablename__ = 'lesson_progress'
    student_id = mapped_column('student_id', Integer, primary_key=True, nullable=False)
    learning_page_id = mapped_column('lesson_id', Integer, primary_key=True, nullable=False)
    lesson_id = synonym('learning_page_id')
    last_section_no = mapped_column('last_section_no', Integer, nullable=True)
    started_at = mapped_column('started_at', DateTime(timezone=True), nullable=True, default=now_utc)
    last_viewed_at = mapped_column('last_viewed_at', DateTime(timezone=True), nullable=True)
    legacy_imported = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    completed_at = mapped_column('completed_at', DateTime(timezone=True), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['student_id'], ['app_user.user_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['lesson_id'], ['lesson.lesson_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['lesson_id', 'last_section_no'], ['lesson_section.lesson_id', 'lesson_section.section_no'], ondelete='RESTRICT'),
        CheckConstraint("legacy_imported OR (started_at IS NOT NULL AND last_viewed_at IS NOT NULL)", name="progress_new_history_required"),
    )

    id = mapped_column(Integer, nullable=True, unique=True)
    is_completed = mapped_column(Boolean, nullable=False, default=False)
    student = relationship("User", back_populates="progress_records")
    learning_page = relationship("LearningPage", back_populates="page_progress")
