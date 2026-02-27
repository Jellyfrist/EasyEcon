"""
learning page = a single lesson inside a module

free-form block-based content (like Notion / WordPress editor)

teachers add block in any order

available block types:

  { "id": "b1", "type": "heading",    "data": { "level": 1, "text": "..." } }
  { "id": "b2", "type": "heading",    "data": { "level": 2, "text": "..." } }
  { "id": "b3", "type": "paragraph",  "data": { "text": "..." } }
  { "id": "b4", "type": "image",      "data": { "url": "...", "caption": "..." } }
  { "id": "b5", "type": "video",      "data": { "url": "...", "caption": "..." } }
  { "id": "b6", "type": "formula",    "data": { "expression": "\\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}", "display": "block" } }
  #   expression: LaTeX string (e.g. "E = mc^2", "\\int_0^\\infty f(x)dx")
  #   display: "block"  -> centered on its own line (like Word equation block)
  #            "inline" -> embedded inside a paragraph
  { "id": "b7", "type": "divider",    "data": {} }
  { "id": "b8", "type": "mini_quiz",  "data": {
      "title": "Quick Check",
      "questions": [
        {
          "id": "q1",
          "type": "multiple_choice",
          "text": "What is ...?",
          "options": ["A) ...", "B) ...", "C) ..."],
          "correct_answer": "A",
          "explanation": "Because ...",
          "topic_tag": "supply_demand_basics",
          "points": 1
        }
      ]
  }}
  
topic_tag (on the page itself):
- backend-only label used to link this page to exam question tag
- when a student answers an exam question incorrectly and that question's
topic_tag matches this page's topic_tag, the system suggests this page
for review. *never shown on the student-facing UI

template_type:
  a frontend hint for which starter layout to pre-populate
  "blank" | "video_lesson" | "text_image" | "mixed"

teachers can freely add/remove/reorder blocks after picking one
"""

from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

from __future__ import annotations

UTC = timezone.utc

if TYPE_CHECKING:
    from .module import Module
    from .user import User
    from .best_attempt import BestAttempt


class LearningPage(Base):
    __tablename__ = "learning_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    module_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("modules.id"), nullable = False, index = True
    )

    # content
    # order array of block objects and see module docstring for schema
    content_blocks: Mapped[list] = mapped_column(
        JSON, nullable = False, default = list,
    )

    # frontend hint for starter layout *not restrict block
    # blank | video_lesson | text_image | mixed
    template_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default = "blank",
    )

    # page info
    title: Mapped[str] = mapped_column(String(200), nullable = False, default = "Untitled Page")
    order_index: Mapped[int] = mapped_column(Integer, default = 0)

    # short plain-text excerpt shown in module overview (auto-generated or set by teacher)
    preview: Mapped[str] = mapped_column(Text, nullable = True)

    '''
    backend weakness-linking tag
    '''
    # used to match this page to exam question topic_tags
    # so the system can suggest it as a review resource after incorrect answers
    # dont shown to student
    topic_tag: Mapped[str] = mapped_column(
        String(100), nullable = True, index = True
    )

    # publishing
    is_published: Mapped[bool] = mapped_column(Boolean, default = False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable = True)

    # author tracking
    # if have collab teacher
    last_edited_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable = True
    )

    # timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default = lambda: datetime.now(UTC),
        onupdate = lambda: datetime.now(UTC),
    )

    '''
    relationship
    '''
    module: Mapped["Module"] = relationship(back_populates = "learning_pages")

    # if have collab teacher
    last_editor: Mapped["User"] = relationship(
        "User",
        foreign_keys = [last_edited_by_user_id],
    )
    # mini quiz attempts: one row per (student, page), upsert on every retake
    quiz_attempts: Mapped[List["BestAttempt"]] = relationship(
        back_populates = "learning_page", cascade = "all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<LearningPage(id={self.id}, title='{self.title}')>"