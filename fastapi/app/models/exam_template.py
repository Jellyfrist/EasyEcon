'''
exam template = a teacher's reusable past-exam question bank

analogous to a blank Google Form
questions are stored as a JSON array inside `question_data` *no separate DB rows per question

this live under a Course because past year or semester exams span
an entire course, not just one chapter

question_data item schema:
{
  "id": "q1",
  "type": "multiple_choice",         # or "fill_in_the_blank" | "true_false" | "short_answer"
  "text": "What happens when supply increases?",
  "options": ["A) Price rises", "B) Price falls", "C) No change", "D) Demand rises"],
  "correct_answer": "B",             # string, or list[str] for multi-select
  "explanation": "When supply increases ...",
  "points": 5,
  "topic_tag": "supply_demand_basics",   # REQUIRED — used for weakness analysis
  "order_index": 0,
  "linked_learning_page_id": 12          # page suggested if student answers wrong
}

topic_tag is on exam questions (unlike mini quiz where it's optional)
b/c the whole point of the exam system is to analyse weaknesses and
link back to learning pages for review
'''

from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

from __future__ import annotations

UTC = timezone.utc

if TYPE_CHECKING:
    from .user import User
    from .course import Course
    from .exam_session import ExamSession


class ExamTemplate(Base):
    '''Teacher-authored exam template — the blank form before it is launched.'''

    __tablename__ = "exam_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # ownership
    created_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    # past exams cover the whole course
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable=False, index=True
    )

    # metadata
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # midterm | final | practice
    exam_type: Mapped[str] = mapped_column(String(30), nullable=False, default="midterm")

    # academic context — for browsing past-year papers
    academic_year: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="e.g. '2025'"
    )
    term: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="e.g. 'Semester 2'"
    )

    # question bank (JSON — no DB rows)
    question_data: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # settings
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    passing_score_pct: Mapped[int] = mapped_column(Integer, default=60)
    randomise_questions: Mapped[bool] = mapped_column(Boolean, default=False)
    randomise_options: Mapped[bool] = mapped_column(Boolean, default=False)
    show_correct_after: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_review: Mapped[bool] = mapped_column(Boolean, default=True)

    # publishing
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    # timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # relationships
    creator: Mapped["User"] = relationship(
        "User", foreign_keys=[created_by_user_id], back_populates="exam_templates"
    )
    course: Mapped["Course"] = relationship(back_populates="exam_templates")
    sessions: Mapped[List["ExamSession"]] = relationship(
        back_populates="template", cascade="all, delete-orphan"
    )

    # helpers
    @property
    def total_points(self) -> int:
        return sum(q.get("points", 0) for q in (self.question_data or []))

    @property
    def question_count(self) -> int:
        return len(self.question_data or [])

    def __repr__(self) -> str:
        return (
            f"<ExamTemplate(id={self.id}, title='{self.title}', "
            f"type='{self.exam_type}', year='{self.academic_year}')>"
        )