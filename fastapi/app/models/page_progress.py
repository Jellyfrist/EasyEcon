'''
page progress = tracks a student's completion status for a single learning page

student tracking record
created or updated when a student finishes reading/watching a lesson page.
used by the frontend (LearningDashboard) to calculate module completion percentage 
(e.g., 45%) and determine which subsequent lessons should be "active" or "locked".

tracks two main things:
- is_completed = boolean flag indicating the student finished the lesson
- completed_at = timestamp of when they finished

hierarchy:
  module
    └── learning page (lesson content)
          ├── content blocks (headings, videos, paragraphs, etc.)
          ├── quiz attempt = BestAttempt (tracks mini quiz scores)
          └── page progress = PageProgress (tracks reading/watching completion)
'''

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

UTC = timezone.utc

if TYPE_CHECKING:
    from .user import User
    from .learning_page import LearningPage

class PageProgress(Base):
    __tablename__ = "page_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    learning_page_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learning_pages.id"), nullable=False, index=True
    )
    
    # สถานะว่าเรียนจบหรือยัง
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # เวลาที่เรียนจบ
    completed_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    # relationships
    student: Mapped["User"] = relationship("User", back_populates="progress_records")
    # 🚨 แก้ชื่อตัวแปรตรงนี้ให้ตรงกับ back_populates ของฝั่งลูกครับ
    learning_page: Mapped["LearningPage"] = relationship("LearningPage", back_populates="page_progress")

    def __repr__(self) -> str:
        return f"<PageProgress(student_id={self.student_id}, page_id={self.learning_page_id}, completed={self.is_completed})>"