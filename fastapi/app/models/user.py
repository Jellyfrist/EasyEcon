from __future__ import annotations
from datetime import datetime, timezone
import uuid
from sqlalchemy import Integer, Identity, String, Boolean, DateTime, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, Index, text
from sqlalchemy.orm import mapped_column, relationship, synonym
from sqlalchemy.ext.hybrid import hybrid_property
from app.db import Base


def now_utc():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = 'app_user'
    id = mapped_column('user_id', Integer, Identity(always=False), primary_key=True, nullable=False)
    user_id = synonym('id')
    username = mapped_column('username', String(80), nullable=False)
    email = mapped_column('email', String(254), nullable=False)
    display_name = mapped_column('display_name', String(120), nullable=False)
    role = mapped_column('role', String(10), nullable=False, default="student")
    account_status = mapped_column('account_status', String(12), nullable=False, default="active")
    auth_subject_id = mapped_column('auth_subject_id', String(120), nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = mapped_column('created_at', DateTime(timezone=True), nullable=True, default=now_utc)
    updated_at = mapped_column('updated_at', DateTime(timezone=True), nullable=True, default=now_utc, onupdate=now_utc)
    legacy_imported = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    __table_args__ = (
        UniqueConstraint('username'),
        UniqueConstraint('email'),
        UniqueConstraint('auth_subject_id'),
        CheckConstraint("role IN ('admin','teacher','student')"),
        CheckConstraint("account_status IN ('active','inactive')"),
        CheckConstraint("legacy_imported OR (created_at IS NOT NULL AND updated_at IS NOT NULL)", name="user_new_history_required"),
    )

    hashed_password = mapped_column(String(255), nullable=True)
    full_name = mapped_column(String(100), nullable=True)
    email_sent = mapped_column(Boolean, default=False, nullable=False)
    is_verified = mapped_column(Boolean, default=False, nullable=False)
    verification_token = mapped_column(String(255), nullable=True)
    social_accounts = relationship("SocialAuth", back_populates="user", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="teacher")
    created_pages = relationship("LearningPage", foreign_keys="LearningPage.created_by_user_id", back_populates="creator")
    exam_templates = relationship("ExamTemplate", foreign_keys="ExamTemplate.created_by_user_id", back_populates="creator")
    launched_sessions = relationship("ExamSession", back_populates="launched_by")
    progress_records = relationship("PageProgress", back_populates="student", cascade="all, delete-orphan")
    exam_attempts = relationship("ExamAttempt", back_populates="student")

    @hybrid_property
    def is_active(self):
        return self.account_status == "active"

    @is_active.setter
    def is_active(self, value):
        self.account_status = "active" if value else "inactive"

    @is_active.expression
    def is_active(cls):
        return cls.account_status == "active"


class TeacherInvitation(Base):
    __tablename__ = 'teacher_invitation'
    id = mapped_column('invitation_id', Integer, Identity(always=False), primary_key=True, nullable=False)
    invitation_id = synonym('id')
    invited_user_id = mapped_column('invited_user_id', Integer, nullable=False)
    invited_by_admin_id = mapped_column('invited_by_admin_id', Integer, nullable=False)
    recipient_name = mapped_column('recipient_name', String(120), nullable=False)
    recipient_email = mapped_column('recipient_email', String(254), nullable=False)
    delivery_status = mapped_column('delivery_status', String(10), nullable=False, default="pending")
    created_at = mapped_column('created_at', DateTime(timezone=True), nullable=False, default=now_utc)
    last_sent_at = mapped_column('last_sent_at', DateTime(timezone=True), nullable=True)
    send_count = mapped_column('send_count', Integer, nullable=False, default=0)
    __table_args__ = (
        ForeignKeyConstraint(['invited_user_id'], ['app_user.user_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['invited_by_admin_id'], ['app_user.user_id'], ondelete='RESTRICT'),
        CheckConstraint("delivery_status IN ('pending','sent','failed')"),
        CheckConstraint('send_count >= 0'),
        Index('invitation_recipient_idx', 'invited_user_id'),
    )
