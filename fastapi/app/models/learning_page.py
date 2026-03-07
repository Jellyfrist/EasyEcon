
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

UTC = timezone.utc

if TYPE_CHECKING:
    from .module import Module
    from .user import User
    from .best_attempt import BestAttempt
    from .page_progress import PageProgress


class LearningPage(Base):
    __tablename__ = "learning_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    module_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("modules.id"), nullable = False, index = True
    )

    content_blocks: Mapped[list] = mapped_column(
        JSON, nullable = False, default = list,
    )

    template_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default = "blank",
    )

    title: Mapped[str] = mapped_column(String(200), nullable = False, default = "Untitled Page")
    order_index: Mapped[int] = mapped_column(Integer, default = 0)

    preview: Mapped[str] = mapped_column(Text, nullable = True)

    '''
    backend weakness-linking tag
    '''

    topic_tag: Mapped[str] = mapped_column(
        String(100), nullable = True, index = True
    )

    is_published: Mapped[bool] = mapped_column(Boolean, default = False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable = True)

    created_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    last_edited_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable = True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default = lambda: datetime.now(UTC),
        onupdate = lambda: datetime.now(UTC),
    )

    '''
    relationship
    '''
    module: Mapped["Module"] = relationship(back_populates = "learning_pages")

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="created_pages",
    )

    last_editor: Mapped["User"] = relationship(
        "User",
        foreign_keys = [last_edited_by_user_id],
    )

    quiz_attempts: Mapped[List["BestAttempt"]] = relationship(
        back_populates = "learning_page", cascade = "all, delete-orphan"
    )

    page_progress: Mapped[list["PageProgress"]] = relationship(
        back_populates="learning_page", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<LearningPage(id={self.id}, title='{self.title}')>"