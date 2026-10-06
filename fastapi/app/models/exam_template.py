from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import json
from sqlalchemy import BigInteger, Integer, Identity, String, Text, Numeric, Boolean, DateTime, JSON, ForeignKey, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import mapped_column, relationship, synonym, object_session
from sqlalchemy.ext.hybrid import hybrid_property
from app.db import Base

BIGINT = BigInteger().with_variant(Integer, "sqlite")

def now_utc():
    return datetime.now(timezone.utc)


class ExamTemplate(Base):
    __tablename__ = 'exam'
    id = mapped_column('exam_id', BIGINT, Identity(always=False), primary_key=True, nullable=False)
    exam_id = synonym('id')
    course_id = mapped_column('course_id', BIGINT, nullable=False)
    title = mapped_column('title', String(150), nullable=False)
    _description = mapped_column('description', Text, nullable=False, default='')
    exam_type = mapped_column('exam_type', String(12), nullable=False)
    _academic_year = mapped_column('academic_year', Integer, nullable=False)
    _term = mapped_column('term', Integer, nullable=False)
    time_limit_minutes = mapped_column('duration_minutes', Integer, nullable=True)
    duration_minutes = synonym('time_limit_minutes')
    passing_score_pct = mapped_column('passing_percentage', Numeric(5,2), nullable=False, default=60)
    passing_percentage = synonym('passing_score_pct')
    is_published = mapped_column('is_published', Boolean, nullable=False, default=False)
    randomise_questions = mapped_column('randomise_questions', Boolean, nullable=False, default=False)
    show_correct_after = mapped_column('show_explanations', Boolean, nullable=False, default=True)
    show_explanations = synonym('show_correct_after')
    created_at = mapped_column('created_at', DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = mapped_column('updated_at', DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['course.course_id'], ondelete='RESTRICT'),
        CheckConstraint("exam_type IN ('midterm','final','summer','quiz')"),
        CheckConstraint('academic_year > 0'),
        CheckConstraint('term BETWEEN 1 AND 3'),
        CheckConstraint('duration_minutes IS NULL OR duration_minutes > 0'),
        CheckConstraint('passing_percentage BETWEEN 0 AND 100'),
    )

    created_by_user_id = mapped_column(BIGINT, ForeignKey("app_user.user_id", ondelete="RESTRICT"), nullable=False)
    source_template_id = mapped_column(BIGINT, ForeignKey("exam.exam_id", ondelete="RESTRICT"), nullable=True)
    description_was_null = mapped_column(Boolean, nullable=False, default=True)
    academic_year_width = mapped_column(Integer, nullable=True)
    term_style = mapped_column(String(20), nullable=True)
    randomise_options = mapped_column(Boolean, nullable=False, default=False)
    allow_review = mapped_column(Boolean, nullable=False, default=True)
    course = relationship("Course", back_populates="all_exams", foreign_keys=[course_id])
    creator = relationship("User", back_populates="exam_templates", foreign_keys=[created_by_user_id])
    source_template = relationship("ExamTemplate", remote_side=[id], foreign_keys=[source_template_id])
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan", order_by="Question.position")
    sessions = relationship("ExamSession", back_populates="assessment", foreign_keys="ExamSession.exam_id")

    @hybrid_property
    def description(self):
        return None if self.description_was_null else self._description

    @description.setter
    def description(self, value):
        self.description_was_null = value is None
        self._description = value if value is not None else ""

    @description.expression
    def description(cls):
        return cls._description

    @hybrid_property
    def academic_year(self):
        return str(self._academic_year).zfill(self.academic_year_width or 0) if self._academic_year is not None else None

    @academic_year.setter
    def academic_year(self, value):
        self.academic_year_width = len(str(value)) if value is not None else None
        if value is None or not str(value).isdigit() or int(value) <= 0:
            raise ValueError("academic_year requires a positive year; no historical/default year is invented")
        self._academic_year = int(value)

    @academic_year.expression
    def academic_year(cls):
        return cls._academic_year

    @hybrid_property
    def term(self):
        if self._term is None:
            return None
        style = self.term_style or ""
        return style if style.lower()=="summer" else style+str(self._term)

    @term.setter
    def term(self, value):
        import re
        match = re.fullmatch(r"((?:Semester |Term )?)([123])", str(value), re.IGNORECASE)
        if str(value).lower() == "summer":
            number = 3
            self.term_style = str(value)
        elif match:
            number = int(match.group(2))
            self.term_style = match.group(1)
        else:
            raise ValueError("term requires 1, 2 or 3; supply evidence for old nonnumeric terms")
        self._term = number

    @term.expression
    def term(cls):
        return cls._term

    @property
    def question_data(self):
        return [q.as_dict() for q in self.questions]

    @question_data.setter
    def question_data(self, values):
        self.questions.clear()
        if object_session(self):
            object_session(self).flush()
        self.questions = [Question.from_dict(q, i) for i, q in enumerate(values or [], 1)]

    @property
    def total_points(self):
        return sum(q.get("points", 0) for q in self.question_data)

    @property
    def question_count(self):
        return len(self.questions)


class Question(Base):
    __tablename__ = 'question'
    id = mapped_column('question_id', BIGINT, Identity(always=False), primary_key=True, nullable=False)
    question_id = synonym('id')
    exam_id = mapped_column('exam_id', BIGINT, nullable=False)
    topic_id = mapped_column('topic_id', BIGINT, nullable=True)
    review_lesson_id = mapped_column('review_lesson_id', BIGINT, nullable=True)
    image_asset_id = mapped_column('image_asset_id', BIGINT, nullable=True)
    position = mapped_column('position', Integer, nullable=False)
    question_type = mapped_column('question_type', String(20), nullable=False)
    prompt_richtext = mapped_column('prompt_richtext', Text, nullable=False)
    points = mapped_column('points', Numeric(8,2), nullable=False)
    explanation_richtext = mapped_column('explanation_richtext', Text, nullable=False)
    __table_args__ = (
        UniqueConstraint('exam_id', 'position'),
        ForeignKeyConstraint(['exam_id'], ['exam.exam_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['topic_id'], ['topic.topic_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['review_lesson_id'], ['lesson.lesson_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['image_asset_id'], ['asset.asset_id'], ondelete='RESTRICT'),
        CheckConstraint('position > 0'),
        CheckConstraint('points > 0'),
        CheckConstraint("question_type IN ('multiple_choice','true_false','short_answer')"),
        Index('question_topic_idx', 'topic_id'),
    )

    external_id = mapped_column(Text, nullable=False)
    original_type = mapped_column(String(30), nullable=False)
    order_index = mapped_column(Integer, nullable=False, default=0)
    shape = mapped_column(JSON, nullable=False, default=dict)
    extra = mapped_column(JSON, nullable=False, default=dict)
    exam = relationship("ExamTemplate", back_populates="questions")
    topic = relationship("Topic")
    review_lesson = relationship("LearningPage", foreign_keys=[review_lesson_id])
    primary_image = relationship("Asset", foreign_keys=[image_asset_id])
    choices = relationship("Choice", cascade="all, delete-orphan", order_by="Choice.choice_no")
    accepted_answers = relationship("AcceptedAnswer", cascade="all, delete-orphan", order_by="AcceptedAnswer.answer_no")

    @classmethod
    def from_dict(cls, value, position):
        keys = {"id","type","text","text_html","explanation","points","topic_tag","order_index","linked_learning_page_id","image_urls","options","correct_answer"}
        raw = value.get("correct_answer")
        shape = {"fields": list(value), "options": "missing" if "options" not in value else "null" if value["options"] is None else "list",
                 "correct": "list" if isinstance(raw,list) else "scalar", "images": "null" if value.get("image_urls") is None else "list"}
        q = cls(external_id=value["id"], position=position,
                original_type=value["type"], question_type="short_answer" if value["type"] == "fill_in_the_blank" else value["type"],
                # Keep the complete editor document, including ordered/repeated
                # image URLs, without introducing a question_asset table.
                prompt_richtext=json.dumps({"text":value.get("text"),"text_html":value.get("text_html"),
                                           "image_urls":deepcopy(value.get("image_urls"))},ensure_ascii=False),
                explanation_richtext=value.get("explanation", ""), points=Decimal(str(value.get("points",1))),
                order_index=value.get("order_index",position-1), review_lesson_id=value.get("linked_learning_page_id"),
                shape=shape, extra={k: deepcopy(v) for k,v in value.items() if k not in keys})
        q._topic_name=value.get("topic_tag")
        correct = raw if isinstance(raw,list) else [raw]
        q.accepted_answers=[AcceptedAnswer.from_value(v,i) for i,v in enumerate(correct,1)]
        def same(a,b): return str(a).strip().casefold() == str(b).strip().casefold()
        option_values = value.get("options") or []
        if q.question_type == "true_false" and not option_values:
            # The existing question editor/reader displays the True and False choices.
            option_values = ["True", "False"]
        q.choices=[Choice(choice_no=i,label=chr(64+i),choice_text=str(v),is_correct=any(same(v,c) for c in correct))
                   for i,v in enumerate(option_values,1)]
        q._image_urls=deepcopy(value.get("image_urls") or [])
        return q

    def as_dict(self):
        raw = [a.as_value() for a in self.accepted_answers]
        number = float(self.points) if self.points is not None else 1
        editor_document=json.loads(self.prompt_richtext)
        values={"id":self.external_id,"type":self.original_type,"text":editor_document.get("text"),"text_html":editor_document.get("text_html"),
                "explanation":self.explanation_richtext,"points":int(number) if number.is_integer() else number,
                "topic_tag":self.__dict__.get("_topic_name",self.topic.name if self.topic else None),
                "order_index":self.order_index,"linked_learning_page_id":self.review_lesson_id,
                "options":None if self.shape.get("options")=="null" else [c.choice_text for c in self.choices],
                "correct_answer":raw if self.shape.get("correct")=="list" else raw[0] if raw else None,
                "image_urls":None if self.shape.get("images")=="null" else self.__dict__.get("_image_urls",editor_document.get("image_urls") or [])}
        values.update(self.extra or {})
        return {k:values[k] for k in self.shape.get("fields",values)}


class Choice(Base):
    __tablename__ = 'choice'
    question_id = mapped_column('question_id', BIGINT, primary_key=True, nullable=False)
    choice_no = mapped_column('choice_no', Integer, primary_key=True, nullable=False)
    label = mapped_column('label', String(10), nullable=False)
    choice_text = mapped_column('choice_text', Text, nullable=False)
    is_correct = mapped_column('is_correct', Boolean, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['question_id'], ['question.question_id'], ondelete='RESTRICT'),
        CheckConstraint('choice_no > 0'),
    )


class AcceptedAnswer(Base):
    __tablename__ = 'accepted_answer'
    question_id = mapped_column('question_id', BIGINT, primary_key=True, nullable=False)
    answer_no = mapped_column('answer_no', Integer, primary_key=True, nullable=False)
    answer_text = mapped_column('answer_text', Text, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['question_id'], ['question.question_id'], ondelete='RESTRICT'),
        CheckConstraint('answer_no > 0'),
    )

    value_type = mapped_column(String(12), nullable=False, default="str")

    @classmethod
    def from_value(cls, value, position):
        kind = "str" if isinstance(value,str) else "json"
        return cls(answer_no=position, answer_text=value if kind=="str" else json.dumps(value, ensure_ascii=False), value_type=kind)

    def as_value(self):
        return self.answer_text if self.value_type=="str" else json.loads(self.answer_text)
