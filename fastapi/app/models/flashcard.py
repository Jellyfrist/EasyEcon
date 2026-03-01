'''
flashcard = stand alone flashcard topics under a course

hierarchy:
  course
    └── flashcard set  (teacher creates any topic they want *not tied to a module)
            └── flashcard  (term / definition / hint)
                    └── flashcard progress  (student: "known" or "learning")

teacher flow:
    1. open a course dashboard
    2. create a flashcard set with a topic title e.g. "Key Economic Terms"
    3. add flashcard rows: term (front), definition (back), optional hint

student flow:
    1. click the flashcard topic for a course
    2. flip through cards: mark each as "known" or "learning"
    3. flashcard progress is upserted on every review so students can
    come back anytime and see how many words they have learned
'''

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer,
    String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

UTC = timezone.utc

if TYPE_CHECKING:
    from .course import Course
    from .user import User

'''
Flashcard Set
'''

class FlashcardSet(Base):
    '''
    - a named collection of flashcards belonging to one course
    - teachers can create as many sets as they like per course,
    on any topic they choose
    '''

    __tablename__ = "flashcard_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)

    # belongs to Course directly * not to a Module or LearningPage
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable = False, index = True
    )

    title: Mapped[str] = mapped_column(String(200), nullable = False)
    description: Mapped[str] = mapped_column(Text, nullable = True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default = lambda: datetime.now(UTC),
        onupdate = lambda: datetime.now(UTC),
    )

    '''
    relationships
    '''
    
    course: Mapped["Course"] = relationship(back_populates = "flashcard_sets")
    cards: Mapped[List["Flashcard"]] = relationship(
        back_populates = "flashcard_set",
        cascade = "all, delete-orphan",
        order_by = "Flashcard.order_index",
    )

    def __repr__(self) -> str:
        return f"<FlashcardSet(id={self.id}, title='{self.title}')>"

'''
Flashcard
'''

class Flashcard(Base):
    '''
    - a single card with a term (front face) and definition (back face)
    - template fields: term (keyword), definition (description), hint (optional)
    '''

    __tablename__ = "flashcards"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    set_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("flashcard_sets.id"), nullable = False, index = True
    )

    term: Mapped[str] = mapped_column(Text, nullable = False)             # front: keyword
    definition: Mapped[str] = mapped_column(Text, nullable = False)       # back: description
    hint: Mapped[Optional[str]] = mapped_column(Text, nullable = True)              # optional hint
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable = True)  # optional back image

    order_index: Mapped[int] = mapped_column(Integer, default = 0)
    is_active: Mapped[bool] = mapped_column(Boolean, default = True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    '''
    relationship
    '''

    flashcard_set: Mapped["FlashcardSet"] = relationship(back_populates = "cards")
    progress_records: Mapped[List["FlashcardProgress"]] = relationship(
        back_populates = "flashcard", cascade = "all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Flashcard(id={self.id}, term='{self.term[:30]}')>"

'''
Flashcard Progress
'''

class FlashcardProgress(Base):
    '''
    - per-student progress on each individual card
    - one row per (student_id, flashcard_id): upsert on every review

    status: "known" | "learning"

    - the student dashboard derives "how many words learned on this topic"
    by counting rows where status = "known" for a given FlashcardSet
    '''

    __tablename__ = "flashcard_progress"

    __table_args__ = (
        UniqueConstraint(
            "student_id", "flashcard_id",
            name = "uq_flashcard_progress_student_card",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable = False, index = True
    )
    flashcard_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("flashcards.id"), nullable = False, index = True
    )

    # known or learning
    status: Mapped[str] = mapped_column(String(20), nullable = False, default = "learning")
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default = lambda: datetime.now(UTC),
        onupdate = lambda: datetime.now(UTC),
    )

    '''
    relationship
    '''

    student: Mapped["User"] = relationship(
        "User", foreign_keys = [student_id], back_populates = "flashcard_progress"
    )
    flashcard: Mapped["Flashcard"] = relationship(back_populates = "progress_records")

    def __repr__(self) -> str:
        return (
            f"<FlashcardProgress(student={self.student_id}, "
            f"card={self.flashcard_id}, status='{self.status}')>"
        )