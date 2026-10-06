from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Integer, Identity, String, Boolean, DateTime, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, select, text
from sqlalchemy.orm import mapped_column, relationship, synonym
from app.db import Base


def now_utc():
    return datetime.now(timezone.utc)


class Module(Base):
    __tablename__ = 'module'
    id = mapped_column('module_id', Integer, Identity(always=False), primary_key=True, nullable=False)
    module_id = synonym('id')
    course_id = mapped_column('course_id', Integer, nullable=False)
    title = mapped_column('title', String(150), nullable=False)
    position = mapped_column('position', Integer, nullable=False)
    is_hidden = mapped_column('is_hidden', Boolean, nullable=False, default=False)
    created_at = mapped_column('created_at', DateTime(timezone=True), nullable=True, default=now_utc)
    updated_at = mapped_column('updated_at', DateTime(timezone=True), nullable=True, default=now_utc, onupdate=now_utc)
    legacy_imported = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    __table_args__ = (
        UniqueConstraint('course_id', 'position'),
        ForeignKeyConstraint(['course_id'], ['course.course_id'], ondelete='RESTRICT'),
        CheckConstraint('position > 0'),
        CheckConstraint("legacy_imported OR (created_at IS NOT NULL AND updated_at IS NOT NULL)", name="module_new_history_required"),
    )

    order_index = mapped_column(Integer, nullable=False, default=0)
    course = relationship("Course", back_populates="modules")
    learning_pages = relationship("LearningPage", back_populates="module", cascade="all, delete-orphan", order_by="LearningPage.order_index")


    @staticmethod
    def synchronize_positions(db, model, parent_column, parent_id):
        """Keep the target's positive unique slots in the API's existing order."""
        from .course import Course
        parent = Course if model is Module else Module
        db.execute(select(parent.id).where(parent.id==parent_id).with_for_update())
        db.flush()
        rows=db.query(model).filter(getattr(model,parent_column)==parent_id).order_by(model.order_index,model.id).all()
        if all(row.position==i for i,row in enumerate(rows,1)):
            return
        # Immediate UNIQUE checks need a positive temporary range during swaps.
        offset=max((row.position for row in rows),default=0)+len(rows)
        for i,row in enumerate(rows,1):row.position=offset+i
        db.flush()
        for i,row in enumerate(rows,1):row.position=i
        db.flush()
