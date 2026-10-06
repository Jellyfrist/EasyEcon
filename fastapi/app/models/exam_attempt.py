from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import statistics
from typing import Dict, Iterable, List, Optional, Sequence
from sqlalchemy.orm import Session as OrmSession

WEAK_THRESHOLD=60
from sqlalchemy import BigInteger, Integer, Identity, String, Text, Numeric, Boolean, DateTime, JSON, ForeignKey, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import mapped_column, relationship, synonym, object_session
from app.db import Base

BIGINT = BigInteger().with_variant(Integer, "sqlite")

def now_utc():
    return datetime.now(timezone.utc)


class ExamAttempt(Base):
    __tablename__ = 'exam_attempt'
    id = mapped_column('attempt_id', BIGINT, Identity(always=False), primary_key=True, nullable=False)
    attempt_id = synonym('id')
    session_id = mapped_column('session_id', BIGINT, nullable=False)
    student_id = mapped_column('student_id', BIGINT, nullable=False)
    attempt_no = mapped_column('attempt_no', Integer, nullable=False, default=1)
    status = mapped_column('status', String(15), nullable=False, default="in_progress")
    started_at = mapped_column('started_at', DateTime(timezone=True), nullable=False, default=now_utc)
    submitted_at = mapped_column('submitted_at', DateTime(timezone=True), nullable=True)
    score = mapped_column('awarded_points', Numeric(12,2), nullable=True)
    awarded_points = synonym('score')
    max_score = mapped_column('possible_points', Numeric(12,2), nullable=True)
    possible_points = synonym('max_score')
    passing_percentage_snapshot = mapped_column('passing_percentage_snapshot', Numeric(5,2), nullable=False)
    __table_args__ = (
        UniqueConstraint('session_id', 'student_id', 'attempt_no'),
        ForeignKeyConstraint(['session_id'], ['exam_session.session_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['student_id'], ['app_user.user_id'], ondelete='RESTRICT'),
        CheckConstraint('attempt_no > 0'),
        CheckConstraint("status IN ('in_progress','submitted','graded','expired')"),
        CheckConstraint('submitted_at IS NULL OR submitted_at >= started_at'),
        CheckConstraint('awarded_points IS NULL OR awarded_points >= 0'),
        CheckConstraint('possible_points IS NULL OR possible_points >= 0'),
        CheckConstraint('awarded_points IS NULL OR possible_points IS NULL OR awarded_points <= possible_points'),
        CheckConstraint('passing_percentage_snapshot BETWEEN 0 AND 100'),
        Index('attempt_student_idx', 'student_id', 'session_id'),
    )

    score_pct = mapped_column(Numeric(7,2), nullable=False, default=0)
    passed = mapped_column(Boolean, nullable=False, default=False)
    percentile = mapped_column(Numeric(7,2), nullable=True)
    topic_stats_was_null = mapped_column(Boolean, nullable=False, default=False)
    weakness_report_was_null = mapped_column(Boolean, nullable=False, default=False)
    analysis_entries = relationship("AttemptAnalysis", cascade="all, delete-orphan", order_by="AttemptAnalysis.entry_no")
    unmatched_answers = mapped_column(JSON, nullable=False, default=dict)
    student = relationship("User", back_populates="exam_attempts")
    session = relationship("ExamSession", back_populates="attempts")
    selected_questions = relationship("AttemptQuestion", cascade="all, delete-orphan", order_by="AttemptQuestion.display_order")

    @property
    def answer_rows(self):
        return [s.answer for s in self.selected_questions if s.answer is not None]

    @property
    def answers(self):
        if hasattr(self,"_pending_answers"):
            return self._pending_answers
        result={r.question.external_id:r.as_value() for r in self.answer_rows if r.was_answered}
        result.update(self.unmatched_answers or {})
        return result

    @answers.setter
    def answers(self,value):
        self._pending_answers=deepcopy(value or {})

    @property
    def topic_stats(self):
        if self.topic_stats_was_null:
            return None
        return {row.topic_tag:row.as_value() for row in self.analysis_entries if row.kind=="topic"}

    @topic_stats.setter
    def topic_stats(self,value):
        self.topic_stats_was_null=value is None
        self.analysis_entries=[row for row in self.analysis_entries if row.kind!="topic"]
        self.analysis_entries.extend(AttemptAnalysis.from_value("topic",i,tag,fields)
            for i,(tag,fields) in enumerate((value or {}).items(),1))

    @property
    def weakness_report(self):
        if self.weakness_report_was_null:
            return None
        return [row.as_value() for row in self.analysis_entries if row.kind=="weakness"]

    @weakness_report.setter
    def weakness_report(self,value):
        self.weakness_report_was_null=value is None
        self.analysis_entries=[row for row in self.analysis_entries if row.kind!="weakness"]
        self.analysis_entries.extend(AttemptAnalysis.from_value("weakness",i,fields.get("topic_tag"),fields)
            for i,fields in enumerate(value or [],1))

    # grading logic
    @staticmethod
    def is_answer_correct(student_answer, correct_answer, question_type: str | None = None) -> bool:
        '''
        case/whitespace-insensitive comparison used by grading and by
        wrong_questions(). Short-answer lists are accepted alternatives;
        multiple-choice lists are multi-select answers and must match exactly.
        '''
        if student_answer is None:
            return False
        if isinstance(correct_answer, list):
            if question_type in ("short_answer", "fill_in_the_blank"):
                answer = str(student_answer).strip().casefold()
                return any(answer == str(choice).strip().casefold() for choice in correct_answer)
            if not isinstance(student_answer, list):
                return False
            return (
                sorted(str(a).strip().lower() for a in student_answer)
                == sorted(str(a).strip().lower() for a in correct_answer)
            )
        return str(student_answer).strip().casefold() == str(correct_answer).strip().casefold()

    def grade(self, passing_score_pct: int = 60) -> None:
        '''
        auto-grade this attempt against the session's question_snapshot.
        call this after setting self.answers.
        populates: score, max_score, score_pct, passed, topic_stats, weakness_report.
        All assessed data comes from the session snapshot adapter; editing the
        live template's questions does not change these question rows.
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

            if self.is_answer_correct(student_ans, correct, q.get("type")):
                raw_score += points
                topic_buckets[tag]["correct"] += 1

        self.score = Decimal(str(raw_score))
        self.max_score = Decimal(str(raw_max))
        self.score_pct = round((raw_score / raw_max * 100) if raw_max else 0.0, 2)
        self.passed = self.score_pct >= passing_score_pct
        self.passing_percentage_snapshot = passing_score_pct
        for row in self.answer_rows:
            q = row.question
            row.is_correct = self.is_answer_correct(row.as_value() if row.was_answered else None, q.as_dict().get("correct_answer"), q.original_type)
            row.awarded_points = q.points if row.is_correct else Decimal("0")
            row.answered_at = self.submitted_at if row.was_answered else None

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

        # Save answer grades while the parent is still in_progress, then finalize.
        orm = object_session(self)
        if orm is not None:
            orm.flush()
        self.status = "graded"

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

    def wrong_questions(self, include_answers: bool = False) -> List[dict]:
        '''
        the questions this student got wrong (or left blank), in snapshot order.

        [
          {
            "question_id": "q3",
            "type": "multiple_choice",
            "text": "What shifts the demand curve?",
            "topic_tag": "demand",
            "linked_learning_page_id": 42,   # may be None
            "points": 1,
            "answered": false,               # false = left blank
            "your_answer": "B",              # what the student submitted
            # only when include_answers is True:
            "correct_answer": "A",
            "explanation": "Income changes shift the whole curve ...",
          },
          ...
        ]

        include_answers reveals the correct answer and the teacher's
        explanation. callers pass the template's `show_correct_after` flag —
        a session that hides answers (e.g. retakes are still open) keeps them
        out of the payload.
        '''
        questions: list = self.session.question_snapshot or []
        answers = self.answers or {}

        wrong: List[dict] = []
        for q in questions:
            qid = q.get("id")
            student_ans = answers.get(qid)
            if self.is_answer_correct(student_ans, q.get("correct_answer"), q.get("type")):
                continue

            entry = {
                "question_id": qid,
                "type": q.get("type"),
                "text": q.get("text"),
                "image_urls": q.get("image_urls") or [],
                "topic_tag": q.get("topic_tag") or "untagged",
                "linked_learning_page_id": q.get("linked_learning_page_id"),
                "points": q.get("points", 1),
                "answered": student_ans is not None,
                "your_answer": student_ans,
            }
            if include_answers:
                entry["correct_answer"] = q.get("correct_answer")
                entry["explanation"] = q.get("explanation")

            wrong.append(entry)
        return wrong

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


class AttemptQuestion(Base):
    __tablename__ = 'attempt_question'
    attempt_id = mapped_column('attempt_id', BIGINT, primary_key=True, nullable=False)
    question_id = mapped_column('question_id', BIGINT, primary_key=True, nullable=False)
    display_order = mapped_column('display_order', Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint('attempt_id', 'display_order'),
        ForeignKeyConstraint(['attempt_id'], ['exam_attempt.attempt_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['question_id'], ['question.question_id'], ondelete='RESTRICT'),
        CheckConstraint('display_order > 0'),
    )

    question = relationship("Question")
    answer = relationship("AttemptAnswer", back_populates="selection", uselist=False, cascade="all, delete-orphan")


class AttemptAnswer(Base):
    __tablename__ = 'attempt_answer'
    attempt_id = mapped_column('attempt_id', BIGINT, primary_key=True, nullable=False)
    question_id = mapped_column('question_id', BIGINT, primary_key=True, nullable=False)
    selected_choice_no = mapped_column('selected_choice_no', Integer, nullable=True)
    typed_answer = mapped_column('typed_answer', Text, nullable=True)
    answered_at = mapped_column('answered_at', DateTime(timezone=True), nullable=True)
    awarded_points = mapped_column('awarded_points', Numeric(8,2), nullable=True)
    is_correct = mapped_column('is_correct', Boolean, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['attempt_id', 'question_id'], ['attempt_question.attempt_id', 'attempt_question.question_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['question_id', 'selected_choice_no'], ['choice.question_id', 'choice.choice_no'], ondelete='RESTRICT'),
        CheckConstraint('NOT (selected_choice_no IS NOT NULL AND typed_answer IS NOT NULL)'),
        CheckConstraint('awarded_points IS NULL OR awarded_points >= 0'),
        CheckConstraint('(awarded_points IS NULL) = (is_correct IS NULL)'),
    )

    was_answered = mapped_column(Boolean, nullable=False, default=False)
    value_shape = mapped_column(String(8), nullable=False, default="scalar")
    selection = relationship("AttemptQuestion", back_populates="answer")
    question = relationship("Question", foreign_keys=[question_id], primaryjoin="AttemptAnswer.question_id==Question.id", viewonly=True)
    values = relationship("AttemptAnswerValue", cascade="all, delete-orphan", order_by="AttemptAnswerValue.value_no")

    @property
    def external_question_id(self):
        return self.question.external_id

    @classmethod
    def from_value(cls,value,present=True):
        return cls(was_answered=present, value_shape="list" if isinstance(value,list) else "scalar",
                   values=[AttemptAnswerValue(value_no=i,value=deepcopy(v)) for i,v in enumerate(value if isinstance(value,list) else [value],1)])

    def as_value(self):
        values=[v.value for v in self.values]
        return values if self.value_shape=="list" else values[0] if values else None


class AttemptAnswerValue(Base):
    __tablename__="attempt_answer_value"
    attempt_id=mapped_column(BIGINT,primary_key=True)
    question_id=mapped_column(BIGINT,primary_key=True)
    value_no=mapped_column(Integer,primary_key=True)
    value=mapped_column(JSON,nullable=False)
    __table_args__=(ForeignKeyConstraint(["attempt_id","question_id"],["attempt_answer.attempt_id","attempt_answer.question_id"],ondelete="RESTRICT"),CheckConstraint("value_no>0"))


class AttemptAnalysis(Base):
    """Historical API report entries; counters retain their original semantics."""
    __tablename__="attempt_analysis"
    attempt_id=mapped_column(BIGINT,ForeignKey("exam_attempt.attempt_id",ondelete="RESTRICT"),primary_key=True)
    kind=mapped_column(String(10),primary_key=True)
    entry_no=mapped_column(Integer,primary_key=True)
    topic_tag=mapped_column(Text)
    fields=mapped_column(JSON,nullable=False)
    has_page_ids=mapped_column(Boolean,nullable=False,default=False)
    lesson_links=relationship("AttemptAnalysisLesson",cascade="all, delete-orphan",order_by="AttemptAnalysisLesson.link_no")
    __table_args__=(CheckConstraint("kind IN ('topic','weakness')"),CheckConstraint("entry_no>0"))

    @classmethod
    def from_value(cls,kind,position,tag,value):
        row=cls(kind=kind,entry_no=position,topic_tag=tag,has_page_ids="suggested_page_ids" in value,
                fields={k:deepcopy(v) for k,v in value.items() if k!="suggested_page_ids"})
        row.lesson_links=[AttemptAnalysisLesson(link_no=i,legacy_lesson_id=page) for i,page in enumerate(value.get("suggested_page_ids") or [],1)]
        return row

    def as_value(self):
        value=deepcopy(self.fields)
        if self.has_page_ids:value["suggested_page_ids"]=[link.legacy_lesson_id for link in self.lesson_links]
        return value


class AttemptAnalysisLesson(Base):
    __tablename__="attempt_analysis_lesson"
    attempt_id=mapped_column(BIGINT,primary_key=True)
    kind=mapped_column(String(10),primary_key=True)
    entry_no=mapped_column(Integer,primary_key=True)
    link_no=mapped_column(Integer,primary_key=True)
    # Old reports can refer to deleted lessons; preserve that historical ID, not a fake FK.
    legacy_lesson_id=mapped_column(BIGINT,nullable=False)
    __table_args__=(ForeignKeyConstraint(["attempt_id","kind","entry_no"],
        ["attempt_analysis.attempt_id","attempt_analysis.kind","attempt_analysis.entry_no"],ondelete="RESTRICT"),CheckConstraint("link_no>0"))
