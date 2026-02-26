'''
exam attempt = a student's single submission for an exam session

stores:
    - raw answers keyed by question ID
    - auto-graded score and pass/fail
    - percentile rank among all attempts for this session
    - weakness analysis: topic tags where student performed poorly,
    each linked back to suggested LearningPage IDs for review

answers schema (dict):
{
  "q1": "A",               # MCQ — option letter/text chosen
  "q2": "mitochondria",    # fill-in-the-blank — student's text
  "q3": ["A", "C"]         # multi-select
}

topic_stats schema (dict), computed on submission:
{
  "biology_photosynthesis": {
    "correct": 1,
    "total": 3,
    "score_pct": 33,
    "is_weak": true,            # score_pct < WEAK_THRESHOLD (default 60)
    "suggested_page_ids": [42, 57]
  },
  ...
}

weakness_report schema (list), derived from topic_stats, sorted by score_pct asc:
[
  {
    "topic_tag": "biology_photosynthesis",
    "score_pct": 33,
    "suggested_page_ids": [42, 57],
    "message": "You scored 33% on 'biology_photosynthesis'. Review the linked lessons."
  },
  ...
]
'''

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session as OrmSession

from app.db import Base

from __future__ import annotations

UTC = timezone.utc

WEAK_THRESHOLD = 60  # % correct below which a topic is flagged as "weak"

if TYPE_CHECKING:
    from .exam_session import ExamSession
    from .user import User


class ExamAttempt(Base):
    '''
    one student's graded submission for an exam session
    all scoring and weakness analysis is computed from the session
    question_snapshot: no live DB question rows are need
    '''

    __tablename__ = "exam_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)

    # participants
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable = False
    )
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exam_sessions.id"), nullable = False
    )

    # submission
    answers: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict,
        comment="{ question_id: student_answer, ... }"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # scoring
    score: Mapped[float] = mapped_column(Float, default=0.0)
    max_score: Mapped[float] = mapped_column(Float, default=0.0)
    score_pct: Mapped[float] = mapped_column(Float, default=0.0) # score / max_score * 100
    passed: Mapped[bool] = mapped_column(Boolean, default=False)

    # percentile
    percentile: Mapped[float] = mapped_column(
        Float, nullable = True,
    )

    # weakness analysis
    topic_stats: Mapped[dict] = mapped_column(
        JSON, nullable = True, default = dict
    )

    # sorted list of weak topics with suggested page ID
    weakness_report: Mapped[list] = mapped_column(
        JSON, nullable=True, default=list,
    )

    
    '''
    relationship
    '''
    student: Mapped["User"] = relationship(
        "User", foreign_keys = [student_id], back_populates = "exam_attempts"
    )
    session: Mapped["ExamSession"] = relationship(
        "ExamSession", back_populates = "attempts"
    )

    # grading logic

    def grade(self, passing_score_pct: int = 60) -> None:
        '''
        auto grade this attempt against the session's question_snapshot

        call this after setting self.answers
        it populates:
            score, max_score, score_pct, passed, topic_stats, weakness_report

        this method is free of any DB queries
        from the JSON snapshot stored on the session
        '''
        questions: list = self.session.question_snapshot or []

        raw_score = 0.0
        raw_max = 0.0
        # { topic_tag: {"correct": int, "total": int, "page_ids": list[int]} }
        topic_buckets: dict = {}

        for q in questions:
            qid = q.get("id")
            points = q.get("points", 1)
            correct = q.get("correct_answer")
            tag = q.get("topic_tag") or "untagged"
            page_id = q.get("linked_learning_page_id")

            raw_max += points

            if tag not in topic_buckets:
                topic_buckets[tag] = {"correct": 0, "total": 0, "page_ids": []}

            topic_buckets[tag]["total"] += 1
            if page_id and page_id not in topic_buckets[tag]["page_ids"]:
                topic_buckets[tag]["page_ids"].append(page_id)

            student_ans = self.answers.get(qid)
            if student_ans is None:
                continue

            # normalise comparison
            if isinstance(correct, list):
                is_correct = sorted(str(a).strip().lower() for a in student_ans) == \
                             sorted(str(a).strip().lower() for a in correct)
            else:
                is_correct = str(student_ans).strip().lower() == str(correct).strip().lower()

            if is_correct:
                raw_score += points
                topic_buckets[tag]["correct"] += 1

        self.score = raw_score
        self.max_score = raw_max
        self.score_pct = round((raw_score / raw_max * 100) if raw_max else 0.0, 2)
        self.passed = self.score_pct >= passing_score_pct

        # build topic_stats
        stats = {}
        for tag, data in topic_buckets.items():
            total = data["total"]
            correct = data["correct"]
            pct = round(correct / total * 100, 2) if total else 0.0
            stats[tag] = {
                "correct": correct,
                "total": total,
                "score_pct": pct,
                "is_weak": pct < WEAK_THRESHOLD,
                "suggested_page_ids": data["page_ids"],
            }
        self.topic_stats = stats

        # build weakness_report (only weak topics, sorted worst-first)
        weak = [
            {
                "topic_tag": tag,
                "score_pct": v["score_pct"],
                "suggested_page_ids": v["suggested_page_ids"],
                "message": (
                    f"You scored {v['score_pct']}% on '{tag}'. "
                    "Review the linked lessons to strengthen this area."
                ),
            }
            for tag, v in stats.items()
            if v["is_weak"]
        ]
        self.weakness_report = sorted(weak, key=lambda x: x["score_pct"])

    @staticmethod
    def recalculate_percentiles(orm_session: OrmSession, session_id: int) -> None:
        """
        Recalculate percentile ranks for all submitted attempts in a session.

        Call this after each new attempt is committed:
            ExamAttempt.recalculate_percentiles(db, session_id=attempt.session_id)

        Percentile = % of other attempts with score_pct strictly lower than this one.
        (Standard "lower than" percentile formula.)
        """
        attempts = (
            orm_session.query(ExamAttempt)
            .filter(
                ExamAttempt.session_id == session_id,
                ExamAttempt.submitted_at.isnot(None),
            )
            .all()
        )
        if not attempts:
            return

        scores = [a.score_pct for a in attempts]
        n = len(scores)
        for attempt in attempts:
            below = sum(1 for s in scores if s < attempt.score_pct)
            attempt.percentile = round(below / n * 100, 2)

    def __repr__(self) -> str:
        return (
            f"<ExamAttempt(id={self.id}, student_id={self.student_id}, "
            f"score_pct={self.score_pct}, percentile={self.percentile})>"
        )