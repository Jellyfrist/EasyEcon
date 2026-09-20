'''
exam attempt = a student's single submission for an exam session

stores:
    - raw answers keyed by question ID
    - auto-graded score and pass/fail
    - percentile rank among all attempts for this session

percentile helpers (no extra columns, nothing written to the DB):
    ExamAttempt.percentile_of(score, population, method=...)   pure math
    ExamAttempt.collect_scores(db, session_id=/template_id=)   reference group
    ExamAttempt.score_report(db, score, ...)                   rank one score
    ExamAttempt.student_percentile(db, student_id, ...)        one user vs all
    ExamAttempt.leaderboard(db, ...)                           everyone ranked
scope = a session (session_id), an exam template across every launch
(template_id), or the whole platform (neither) — so a score can be shown
against all users' scores, not only the classmates in one session.
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

from __future__ import annotations

import statistics
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Sequence

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session as OrmSession

from app.db import Base

UTC = timezone.utc

WEAK_THRESHOLD = 60  # % correct below which a topic is flagged as "weak"

if TYPE_CHECKING:
    from .exam_session import ExamSession
    from .user import User


class ExamAttempt(Base):
    '''
    one student's graded submission for an exam session.
    all scoring and weakness analysis is computed from the session's
    question_snapshot — no live DB question rows needed.
    '''

    __tablename__ = "exam_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # participants
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exam_sessions.id"), nullable=False
    )

    # submission
    answers: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict,
        comment="{ question_id: student_answer, ... }"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # scoring
    score: Mapped[float] = mapped_column(Float, default=0.0)
    max_score: Mapped[float] = mapped_column(Float, default=0.0)
    score_pct: Mapped[float] = mapped_column(Float, default=0.0)  # score / max_score * 100
    passed: Mapped[bool] = mapped_column(Boolean, default=False)

    # percentile rank within this session (0-100), recalculated after each submission
    percentile: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # weakness analysis
    topic_stats: Mapped[dict] = mapped_column(JSON, nullable=True, default=dict)
    weakness_report: Mapped[list] = mapped_column(JSON, nullable=True, default=list)

    # relationships
    student: Mapped["User"] = relationship(
        "User", foreign_keys=[student_id], back_populates="exam_attempts"
    )
    session: Mapped["ExamSession"] = relationship(
        "ExamSession", back_populates="attempts"
    )

    # grading logic
    def grade(self, passing_score_pct: int = 60) -> None:
        '''
        auto-grade this attempt against the session's question_snapshot.
        call this after setting self.answers.
        populates: score, max_score, score_pct, passed, topic_stats, weakness_report.
        no DB queries — all data comes from the JSON snapshot on the session.
        '''
        questions: list = self.session.question_snapshot or []

        raw_score = 0.0
        raw_max = 0.0
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

        # build weakness_report — weak topics only, sorted worst-first
        self.weakness_report = sorted(
            [
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
            ],
            key=lambda x: x["score_pct"],
        )

    @staticmethod
    def recalculate_percentiles(orm_session: OrmSession, session_id: int) -> None:
        '''
        recalculate percentile ranks for all submitted attempts in a session.
        call this after each new attempt is committed.
        percentile = % of attempts with score_pct strictly lower than this one.
        '''
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

    # ------------------------------------------------------------------
    # percentile analytics (read-only)
    # ------------------------------------------------------------------
    # these helpers never write to the DB and need no new columns.
    # the stored `percentile` column stays session-scoped (filled by
    # recalculate_percentiles); the methods below compute a percentile
    # against any other reference group on demand — a single session, every
    # session launched from one template, or every graded attempt by every
    # user on the platform.

    @staticmethod
    def percentile_of(
        score_pct: float,
        population: Sequence[float],
        method: str = "midpoint",
    ) -> Optional[float]:
        '''
        percentile of `score_pct` inside `population` (0-100).

        method:
            "below"       — % of scores strictly lower (matches the stored column)
            "midpoint"    — % below + half of the ties; fairest for equal scores
            "at_or_below" — % lower or equal (a top score gives 100)

        returns None when the population is empty.
        '''
        scores = [s for s in population if s is not None]
        n = len(scores)
        if n == 0:
            return None

        below = sum(1 for s in scores if s < score_pct)
        equal = sum(1 for s in scores if s == score_pct)

        if method == "below":
            ratio = below / n
        elif method == "at_or_below":
            ratio = (below + equal) / n
        elif method == "midpoint":
            ratio = (below + equal / 2) / n
        else:
            raise ValueError(f"unknown percentile method: {method!r}")

        return round(ratio * 100, 2)

    @staticmethod
    def _scores_by_student(
        attempts: Iterable["ExamAttempt"],
        per_user: str = "best",
    ) -> Dict[int, float]:
        '''
        one representative score per student.

        per_user: "best" (highest), "latest" (newest submission), "mean".
        '''
        buckets: Dict[int, List["ExamAttempt"]] = {}
        for a in attempts:
            buckets.setdefault(a.student_id, []).append(a)

        out: Dict[int, float] = {}
        for student_id, student_attempts in buckets.items():
            if per_user == "best":
                out[student_id] = max(a.score_pct for a in student_attempts)
            elif per_user == "latest":
                newest = max(
                    student_attempts,
                    key=lambda a: (a.submitted_at or datetime.min, a.id or 0),
                )
                out[student_id] = newest.score_pct
            elif per_user == "mean":
                vals = [a.score_pct for a in student_attempts]
                out[student_id] = round(sum(vals) / len(vals), 2)
            else:
                raise ValueError(f"unknown per_user mode: {per_user!r}")
        return out

    @classmethod
    def _one_score_per_student(
        cls,
        attempts: Iterable["ExamAttempt"],
        per_user: Optional[str],
    ) -> List[float]:
        '''
        collapse attempts into the score list used as a reference population.
        per_user=None keeps every graded attempt (retakes included).
        '''
        attempts = list(attempts)
        if per_user is None:
            return [a.score_pct for a in attempts]
        return list(cls._scores_by_student(attempts, per_user).values())

    @staticmethod
    def population_with(
        scores_by_student: Dict[int, float],
        student_id: int,
        score_pct: float,
    ) -> List[float]:
        '''
        population where `student_id` is represented by `score_pct` itself
        instead of their aggregate.

        without this, ranking one attempt against a "best score per student"
        population compares a student against their own better attempt — a
        retake could end up ranked below the population size.
        '''
        population = [s for sid, s in scores_by_student.items() if sid != student_id]
        population.append(score_pct)
        return population

    @classmethod
    def _scoped_query(
        cls,
        orm_session: OrmSession,
        *,
        session_id: Optional[int] = None,
        template_id: Optional[int] = None,
        student_id: Optional[int] = None,
    ):
        '''graded attempts narrowed to a scope (intersection of the filters).'''
        query = orm_session.query(cls).filter(cls.submitted_at.isnot(None))

        if session_id is not None:
            query = query.filter(cls.session_id == session_id)

        if template_id is not None:
            from .exam_session import ExamSession

            query = query.join(
                ExamSession, cls.session_id == ExamSession.id
            ).filter(ExamSession.template_id == template_id)

        if student_id is not None:
            query = query.filter(cls.student_id == student_id)

        return query

    @classmethod
    def collect_scores_by_student(
        cls,
        orm_session: OrmSession,
        *,
        session_id: Optional[int] = None,
        template_id: Optional[int] = None,
        per_user: str = "best",
    ) -> Dict[int, float]:
        '''
        { student_id: representative score } for a scope.
        passing no scope filter means "every graded attempt by every user".
        '''
        attempts = cls._scoped_query(
            orm_session, session_id=session_id, template_id=template_id
        ).all()
        return cls._scores_by_student(attempts, per_user)

    @classmethod
    def collect_scores(
        cls,
        orm_session: OrmSession,
        *,
        session_id: Optional[int] = None,
        template_id: Optional[int] = None,
        student_id: Optional[int] = None,
        per_user: Optional[str] = "best",
    ) -> List[float]:
        '''score_pct values of all graded attempts in a scope.'''
        attempts = cls._scoped_query(
            orm_session,
            session_id=session_id,
            template_id=template_id,
            student_id=student_id,
        ).all()
        return cls._one_score_per_student(attempts, per_user)

    @classmethod
    def build_report(
        cls,
        score_pct: float,
        scores: Sequence[float],
        *,
        method: str = "midpoint",
        per_user: Optional[str] = "best",
        scope: Optional[dict] = None,
    ) -> dict:
        '''
        rank one score against an already-collected population:

        {
          "score_pct": 78.0,
          "percentile": 82.5,     # None when the population is empty
          "rank": 4,              # 1 = best, ties share the better rank
          "population": 40,       # how many scores back the percentile
          "mean": 63.1, "median": 65.0, "highest": 98.0, "lowest": 12.0,
          "scope": {...}, "per_user": "best", "method": "midpoint"
        }
        '''
        scores = [s for s in scores if s is not None]
        population = len(scores)

        return {
            "score_pct": round(score_pct, 2),
            "percentile": cls.percentile_of(score_pct, scores, method=method),
            "rank": (sum(1 for s in scores if s > score_pct) + 1) if population else None,
            "population": population,
            "mean": round(statistics.fmean(scores), 2) if population else None,
            "median": round(statistics.median(scores), 2) if population else None,
            "highest": max(scores) if population else None,
            "lowest": min(scores) if population else None,
            "scope": scope or {},
            "per_user": per_user,
            "method": method,
        }

    @classmethod
    def score_report(
        cls,
        orm_session: OrmSession,
        score_pct: float,
        *,
        session_id: Optional[int] = None,
        template_id: Optional[int] = None,
        student_id: Optional[int] = None,
        per_user: Optional[str] = "best",
        method: str = "midpoint",
    ) -> dict:
        '''
        rank one score against everybody else in the scope (one query).

        pass `student_id` when the score belongs to a student already in the
        population: their own aggregate is then replaced by this score, so a
        retake is never ranked against its own better attempt.
        '''
        if per_user is None or student_id is None:
            scores = cls.collect_scores(
                orm_session,
                session_id=session_id,
                template_id=template_id,
                per_user=per_user,
            )
        else:
            by_student = cls.collect_scores_by_student(
                orm_session,
                session_id=session_id,
                template_id=template_id,
                per_user=per_user,
            )
            scores = cls.population_with(by_student, student_id, score_pct)

        return cls.build_report(
            score_pct,
            scores,
            method=method,
            per_user=per_user,
            scope={"session_id": session_id, "template_id": template_id},
        )

    @classmethod
    def student_percentile(
        cls,
        orm_session: OrmSession,
        student_id: int,
        *,
        session_id: Optional[int] = None,
        template_id: Optional[int] = None,
        aggregate: str = "best",
        per_user: Optional[str] = "best",
        method: str = "midpoint",
    ) -> Optional[dict]:
        '''
        one student's standing against all users in the scope.

        `aggregate` picks the student's own representative score
        ("best" / "latest" / "mean"); `per_user` does the same for everybody
        they are compared with.

        returns None when the student has no graded attempt in the scope.
        adds "student_id", "attempts_counted" and "aggregate" to the payload.
        '''
        own_attempts = cls._scoped_query(
            orm_session,
            session_id=session_id,
            template_id=template_id,
            student_id=student_id,
        ).all()
        if not own_attempts:
            return None

        own_score = cls._scores_by_student(own_attempts, aggregate)[student_id]

        report = cls.score_report(
            orm_session,
            own_score,
            session_id=session_id,
            template_id=template_id,
            student_id=student_id,
            per_user=per_user,
            method=method,
        )
        report["student_id"] = student_id
        report["attempts_counted"] = len(own_attempts)
        report["aggregate"] = aggregate
        return report

    @classmethod
    def leaderboard(
        cls,
        orm_session: OrmSession,
        *,
        session_id: Optional[int] = None,
        template_id: Optional[int] = None,
        per_user: str = "best",
        method: str = "midpoint",
        limit: Optional[int] = None,
    ) -> List[dict]:
        '''
        every student in the scope with their score, rank and percentile,
        best first — one row per student.
        '''
        attempts = cls._scoped_query(
            orm_session, session_id=session_id, template_id=template_id
        ).all()

        attempts_per_student: Dict[int, int] = {}
        for a in attempts:
            attempts_per_student[a.student_id] = attempts_per_student.get(a.student_id, 0) + 1

        per_student = cls._scores_by_student(attempts, per_user)
        scores = list(per_student.values())

        rows = [
            {
                "student_id": student_id,
                "score_pct": round(score, 2),
                "percentile": cls.percentile_of(score, scores, method=method),
                "rank": sum(1 for s in scores if s > score) + 1,
                "attempts": attempts_per_student[student_id],
            }
            for student_id, score in per_student.items()
        ]
        rows.sort(key=lambda r: (-r["score_pct"], r["student_id"]))
        return rows[:limit] if limit else rows

    def __repr__(self) -> str:
        return (
            f"<ExamAttempt(id={self.id}, student_id={self.student_id}, "
            f"score_pct={self.score_pct}, percentile={self.percentile})>"
        )