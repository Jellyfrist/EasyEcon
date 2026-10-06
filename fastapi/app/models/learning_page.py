from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
import json
from sqlalchemy import Integer, Identity, String, Text, Boolean, DateTime, JSON, ForeignKey, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, Index, select, text
from sqlalchemy.orm import mapped_column, relationship, synonym, object_session
from sqlalchemy.ext.hybrid import hybrid_property
from app.db import Base


def now_utc():
    return datetime.now(timezone.utc)


class Topic(Base):
    __tablename__ = 'topic'
    id = mapped_column('topic_id', Integer, Identity(always=False), primary_key=True, nullable=False)
    topic_id = synonym('id')
    course_id = mapped_column('course_id', Integer, nullable=False)
    name = mapped_column('name', String(150), nullable=False)
    __table_args__ = (
        UniqueConstraint('course_id', 'name'),
        ForeignKeyConstraint(['course_id'], ['course.course_id'], ondelete='RESTRICT'),
    )


class LearningPage(Base):
    __tablename__ = 'lesson'
    id = mapped_column('lesson_id', Integer, Identity(always=False), primary_key=True, nullable=False)
    lesson_id = synonym('id')
    module_id = mapped_column('module_id', Integer, nullable=False)
    topic_id = mapped_column('topic_id', Integer, nullable=True)
    title = mapped_column('title', String(150), nullable=False)
    position = mapped_column('position', Integer, nullable=False)
    is_published = mapped_column('is_published', Boolean, nullable=False, default=False)
    created_at = mapped_column('created_at', DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = mapped_column('updated_at', DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)
    __table_args__ = (
        UniqueConstraint('module_id', 'position'),
        ForeignKeyConstraint(['module_id'], ['module.module_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['topic_id'], ['topic.topic_id'], ondelete='RESTRICT'),
        CheckConstraint('position > 0'),
        Index('lesson_topic_idx', 'topic_id'),
    )

    order_index = mapped_column(Integer, nullable=False, default=0)
    template_type = mapped_column(String(50), nullable=False, default="blank")
    preview = mapped_column(Text, nullable=True)
    published_at = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_user_id = mapped_column(Integer, ForeignKey("app_user.user_id", ondelete="RESTRICT"), nullable=False)
    last_edited_by_user_id = mapped_column(Integer, ForeignKey("app_user.user_id", ondelete="RESTRICT"), nullable=True)
    module = relationship("Module", back_populates="learning_pages")
    topic = relationship("Topic")
    creator = relationship("User", foreign_keys=[created_by_user_id], back_populates="created_pages")
    last_editor = relationship("User", foreign_keys=[last_edited_by_user_id])
    page_progress = relationship("PageProgress", back_populates="learning_page", cascade="all, delete-orphan")
    sections = relationship("LessonSection", cascade="all, delete-orphan", order_by="LessonSection.section_no")

    @hybrid_property
    def topic_tag(self):
        return self.__dict__.get("_topic_name", self.topic.name if self.topic else None)

    @topic_tag.setter
    def topic_tag(self, value):
        self._topic_name = value
        if object_session(self):
            from sqlalchemy.orm import attributes
            attributes.flag_dirty(self)

    @topic_tag.expression
    def topic_tag(cls):
        return select(Topic.name).where(Topic.id == cls.topic_id).scalar_subquery()

    @property
    def content_blocks(self):
        return [row.as_dict() for row in self.sections]

    @content_blocks.setter
    def content_blocks(self, values):
        self.sections.clear()
        if object_session(self):
            object_session(self).flush()
        self.sections = [LessonSection.from_dict(v, i) for i, v in enumerate(values or [], 1)]


class LessonSection(Base):
    __tablename__ = 'lesson_section'
    lesson_id = mapped_column('lesson_id', Integer, primary_key=True, nullable=False)
    section_no = mapped_column('section_no', Integer, primary_key=True, nullable=False)
    content_richtext = mapped_column('content_richtext', Text, nullable=False)
    updated_at = mapped_column('updated_at', DateTime(timezone=True), nullable=True, default=now_utc, onupdate=now_utc)
    legacy_imported = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    __table_args__ = (
        ForeignKeyConstraint(['lesson_id'], ['lesson.lesson_id'], ondelete='RESTRICT'),
        CheckConstraint('section_no > 0'),
        CheckConstraint("legacy_imported OR updated_at IS NOT NULL", name="section_new_history_required"),
    )

    external_id = mapped_column(Text)
    block_type = mapped_column(Text)
    present_fields = mapped_column(Text, nullable=False, default='["id","type","data"]')
    extra = mapped_column(JSON, nullable=False, default=dict)
    assets = relationship("SectionAsset", cascade="all, delete-orphan")

    @classmethod
    def from_dict(cls, value, position):
        return cls(section_no=position, external_id=value.get("id"), block_type=value.get("type"),
                   content_richtext=json.dumps(value.get("data"), ensure_ascii=False),
                   present_fields=json.dumps(list(value)),
                   extra={k: deepcopy(v) for k, v in value.items() if k not in ("id", "type", "data")})

    def as_dict(self):
        values = {"id": self.external_id, "type": self.block_type, "data": json.loads(self.content_richtext)}
        values.update(self.extra or {})
        return {k: values[k] for k in json.loads(self.present_fields)}


class Asset(Base):
    __tablename__ = 'asset'
    id = mapped_column('asset_id', Integer, Identity(always=False), primary_key=True, nullable=False)
    asset_id = synonym('id')
    storage_key = mapped_column('storage_key', String(180), nullable=False)
    original_filename = mapped_column('original_filename', String(150), nullable=True)
    mime_type = mapped_column('mime_type', String(80), nullable=False)
    byte_size = mapped_column('byte_size', Integer, nullable=False)
    uploaded_by_user_id = mapped_column('uploaded_by_user_id', Integer, nullable=True)
    created_at = mapped_column('created_at', DateTime(timezone=True), nullable=False, default=now_utc)
    legacy_imported = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    __table_args__ = (
        UniqueConstraint('storage_key'),
        ForeignKeyConstraint(['uploaded_by_user_id'], ['app_user.user_id'], ondelete='RESTRICT'),
        CheckConstraint('byte_size > 0'),
        CheckConstraint("legacy_imported OR (storage_key IS NOT NULL AND original_filename IS NOT NULL AND mime_type IS NOT NULL AND byte_size IS NOT NULL AND uploaded_by_user_id IS NOT NULL AND created_at IS NOT NULL)", name="asset_new_metadata_required"),
    )

    uploader = relationship("User", foreign_keys=[uploaded_by_user_id])
    url = mapped_column(Text, nullable=False)


class SectionAsset(Base):
    __tablename__ = 'section_asset'
    lesson_id = mapped_column('lesson_id', Integer, primary_key=True, nullable=False)
    section_no = mapped_column('section_no', Integer, primary_key=True, nullable=False)
    asset_id = mapped_column('asset_id', Integer, primary_key=True, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['lesson_id', 'section_no'], ['lesson_section.lesson_id', 'lesson_section.section_no'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['asset_id'], ['asset.asset_id'], ondelete='RESTRICT'),
    )

    asset = relationship("Asset")
