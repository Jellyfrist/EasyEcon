'''
module = an ordered chapter within a Course e.g. Chapter 3: Supply

contain learning pages (lesson)

- teachers decide where to insert mini quiz
by adding a mini_quiz block inside any LearningPage's content_blocks JSON.

note: flashcard set and exam template isnt inside module
'''

from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from .course import Course
    from .learning_page import LearningPage

class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable = False, index = True
    )

    # title of this module
    title: Mapped[str] = mapped_column(String(100), nullable = False)
    order_index: Mapped[int] = mapped_column(Integer, default = 0)

    '''
    relationship
    '''

    course: Mapped["Course"] = relationship(back_populates = "modules")
    learning_pages: Mapped[List["LearningPage"]] = relationship(
        back_populates = "module",
        cascade = "all, delete-orphan",
        order_by = "LearningPage.order_index",
    )

    def __repr__(self) -> str:
        return f"<Module(id={self.id}, title='{self.title}')>"