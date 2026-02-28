'''
best attempt = record a student's best/latest score for a mini quiz
embedded as a block inside a LearningPage's content_blocks JSON.

design:
- questions live in the LearningPage's content_blocks JSON (type: "mini_quiz")
* no DB rows for question
- one row per (student_id, learning_page_id): unique constraint enforced
- student can retake as many times as they want;
    - the row is upsert, never duplicated
    - only the best score is kept long term
- weakness_report flags weak topic_tags only: no cross page suggestions
(cross page suggestion are an exam attempt feature, not mini quiz

latest_answers schema:
    { "q1": "A", "q2": "mitochondria" }

weakness_report schema (sorted worst-first):
    [
        {
        "topic_tag": "supply_demand_basics",
        "score_pct": 33.0,
        "message": "You scored 33.0% on 'supply_demand_basics'. Review this lesson again."
        }
    ]
'''
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey,
    Integer, JSON, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

UTC = timezone.utc

# % correct below which a topic is flagged as weak
WEAK_THRESHOLD = 60 

if TYPE_CHECKING:
    from .user import User
    from .learning_page import LearningPage


class BestAttempt(Base):
    '''
    - one row per (student, learning_page)
    - upsert on every retake
    '''

    __tablename__ = "page_quiz_attempts"

    __table_args__ = (
        UniqueConstraint(
            "student_id", "learning_page_id",
            name = "uq_page_quiz_attempt_student_page",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)

    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable = False, index = True
    )
    learning_page_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("learning_pages.id"), nullable = False, index = True
    )

    # attempt tracking
    attempt_count: Mapped[int] = mapped_column(Integer, default = 1)

    # scores
    latest_score_pct: Mapped[float] = mapped_column(Float, default = 0.0)
    best_score_pct: Mapped[float] = mapped_column(Float, default = 0.0)
    passed: Mapped[bool] = mapped_column(Boolean, default = False)

    # latest attempt data
    latest_answers: Mapped[dict] = mapped_column(JSON, nullable = True, default = dict)

    # weakness analysis (topic flags)
    topic_stats: Mapped[dict] = mapped_column(JSON, nullable = True, default = dict)
    weakness_report: Mapped[list] = mapped_column(JSON, nullable=True, default = list)

    # timestamps
    first_attempted_at: Mapped[datetime] = mapped_column(
        DateTime, default = lambda: datetime.now(UTC)
    )
    last_attempted_at: Mapped[datetime] = mapped_column(
        DateTime,
        default = lambda: datetime.now(UTC),
        onupdate = lambda: datetime.now(UTC),
    )

    '''
    relationship
    '''
    student: Mapped["User"] = relationship(
        "User", foreign_keys=[student_id], back_populates="page_quiz_attempts"
    )
    learning_page: Mapped["LearningPage"] = relationship(back_populates="quiz_attempts")

    # grading

    def grade(self, questions: list, answers: dict) -> None:
        '''
        grade a new attempt
        - call this with the questions list from the mini_quiz content block
        and the student's submitted answers dict.
        - updates latest/best scores, topic_stats, weakness_report in-place.
        '''

        self.latest_answers = answers
        self.attempt_count = (self.attempt_count or 0) + 1
        self.last_attempted_at = datetime.now(UTC)

        raw_score = 0.0
        raw_max = 0.0
        topic_buckets: dict = {}

        for q in questions:
            qid = q.get("id")
            points = q.get("points", 1)
            correct = q.get("correct_answer")
            tag = q.get("topic_tag") or "untagged"

            raw_max += points
            if tag not in topic_buckets:
                topic_buckets[tag] = {"correct": 0, "total": 0}
            topic_buckets[tag]["total"] += 1

            student_ans = answers.get(qid)
            if student_ans is None:
                continue

            if isinstance(correct, list):
                is_correct = (
                    sorted(str(a).strip().lower() for a in student_ans)
                    == sorted(str(a).strip().lower() for a in correct)
                )
            else:
                is_correct = str(student_ans).strip().lower() == str(correct).strip().lower()

            if is_correct:
                raw_score += points
                topic_buckets[tag]["correct"] += 1

        score_pct = round((raw_score / raw_max * 100) if raw_max else 0.0, 2)
        self.latest_score_pct = score_pct
        self.best_score_pct = max(self.best_score_pct or 0.0, score_pct)
        self.passed = score_pct >= WEAK_THRESHOLD

        stats = {}
        for tag, data in topic_buckets.items():
            total = data["total"]
            correct_count = data["correct"]
            pct = round(correct_count / total * 100, 2) if total else 0.0
            stats[tag] = {
                "correct": correct_count,
                "total": total,
                "score_pct": pct,
                "is_weak": pct < WEAK_THRESHOLD,
            }
        self.topic_stats = stats

        self.weakness_report = sorted(
            [
                {
                    "topic_tag": tag,
                    "score_pct": v["score_pct"],
                    "message": (
                        f"You scored {v['score_pct']}% on '{tag}'. "
                        "Review this lesson again."
                    ),
                }
                for tag, v in stats.items()
                if v["is_weak"]
            ],
            key = lambda x: x["score_pct"],
        )

    def __repr__(self) -> str:
        return (
            f"<PageQuizAttempt(student={self.student_id}, "
            f"page={self.learning_page_id}, "
            f"best={self.best_score_pct}%, attempts={self.attempt_count})>"
        )