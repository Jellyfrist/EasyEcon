'''
course = a subject created by a teacher e.g. Economics in Everyday Life

top level container
teachers can attach three kinds of content directly to a course:
- flashcard set = stand alone flashcard topics (not tied to any module)
- module = ordered lessons (learning gage with mini quiz)
- exam template = past midterm / final exam question banks

hierarchy:
  course
    ├── module = LearningPage (lessons + mini quiz)
    ├── flashcard set = Flashcard (stand alone, teacher chooses any topic)
    └── exam template = ExamSession -> ExamAttempt (past exams)
'''

from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .user import User
    from .module import Module
    from .flashcard import FlashcardSet
    from .exam_template import ExamTemplate

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable = False, index = True
    )

    # title and deacription
    title: Mapped[str] = mapped_column(String(50), nullable = False)
    description: Mapped[str] = mapped_column(Text, nullable = True)

    '''
    relationship
    '''

    # teacher
    teacher: Mapped["User"] = relationship(back_populates = "courses")

    # order lessson
    modules: Mapped[List["Module"]] = relationship(
        back_populates = "course", cascade = "all, delete-orphan"
    )

    # flashcard (stand alone)
    flashcard_sets: Mapped[List["FlashcardSet"]] = relationship(
        back_populates = "course", cascade = "all, delete-orphan"
    )

    # exam from past year or past semester
    exam_templates: Mapped[List["ExamTemplate"]] = relationship(
        back_populates = "course", cascade = "all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, title='{self.title}')>"