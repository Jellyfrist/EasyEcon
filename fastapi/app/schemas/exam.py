'''
examination system.

Flow:
  Teacher  ->  creates ExamTemplate  (question_data JSON)
           ->  launches ExamSession  (snapshot frozen at launch)
  Student  ->  submits ExamAttempt   (graded, weakness_report, percentile)

Every attempt response also carries PercentileReport blocks comparing the
score with other users: session, exam template, and platform-wide.
'''

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


# question inside a template
class ExamQuestion(BaseModel):
    '''
    one qusetion store inside ExamTemplate.question_data (JSON array)
    '''

    id: str = Field(..., description="Stable local ID, e.g. 'q1'")
    type: str = Field(
        ...,
        description = "multiple_choice | fill_in_the_blank | true_false | short_answer",
    )
    text: str
    options: Optional[List[str]] = None       # none for fill in the blank / short answer
    correct_answer: Any                       # str or list[str] for multi select
    explanation: str = Field(
        "",
        description = "why the correct answer is correct — written by the teacher, required "
                      "(empty or missing is rejected by the validator below)",
    )
    points: int = 1
    topic_tag: Optional[str] = None
    order_index: int = 0
    linked_learning_page_id: Optional[int] = None  # cross page suggestion if wrong

    @model_validator(mode="after")
    def explanation_written_by_teacher(self) -> "ExamQuestion":
        '''
        every question must carry its own explanation.
        nothing is generated or copied for the teacher — a blank or
        whitespace-only explanation is rejected, naming the question.
        '''
        if not (self.explanation or "").strip():
            label = self.id or "this question"
            raise ValueError(
                f"Question '{label}': an explanation is required. "
                "Write your own explanation of the correct answer."
            )
        self.explanation = self.explanation.strip()
        return self


'''
Exam Template
'''

# create template
class ExamTemplateCreate(BaseModel):
    course_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    exam_type: str = Field("midterm", description = "midterm | final")
    academic_year: Optional[str] = Field(None, description = "e.g. '2025'")
    term: Optional[str] = Field(None, description = "e.g. 'Semester 2'")
    question_data: List[ExamQuestion] = []
    time_limit_minutes: Optional[int] = None
    passing_score_pct: int = 60
    randomise_questions: bool = False
    randomise_options: bool = False
    show_correct_after: bool = True
    allow_review: bool = True
    is_published: bool = False

# update template
class ExamTemplateUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    exam_type: Optional[str] = None
    academic_year: Optional[str] = None
    term: Optional[str] = None
    question_data: Optional[List[ExamQuestion]] = None
    time_limit_minutes: Optional[int] = None
    passing_score_pct: Optional[int] = None
    randomise_questions: Optional[bool] = None
    randomise_options: Optional[bool] = None
    show_correct_after: Optional[bool] = None
    allow_review: Optional[bool] = None
    is_published: Optional[bool] = None

# response
class ExamTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: Optional[int]
    created_by_user_id: int
    title: str
    description: Optional[str]
    exam_type: str
    academic_year: Optional[str]
    term: Optional[str]
    question_data: List[Dict[str, Any]]
    question_count: int
    total_points: int
    time_limit_minutes: Optional[int]
    passing_score_pct: int
    randomise_questions: bool
    randomise_options: bool
    show_correct_after: bool
    allow_review: bool
    is_published: bool
    created_at: datetime
    updated_at: datetime


class ExamTemplateSummary(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    title: str
    exam_type: str
    academic_year: Optional[str]
    term: Optional[str]
    question_count: int
    total_points: int
    is_published: bool


'''
Exam Session
'''

# create session
class ExamSessionCreate(BaseModel):
    template_id: int
    title: str
    instructions: Optional[str] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    time_limit_minutes: Optional[int] = None
    max_attempts: int = 1

# response session
class ExamSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_id: int
    title: str
    instructions: Optional[str]
    available_from: Optional[datetime]
    available_until: Optional[datetime]
    time_limit_minutes: Optional[int]
    max_attempts: int
    is_active: bool
    launched_by_user_id: int
    launched_at: datetime
    is_open: bool

class ExamSessionStudentResponse(BaseModel):
    '''
    - sent to students when they open an exam.
    - correct answer, explanation, and linked learning page id 
    are all stripped by the router before returning.
    '''
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    instructions: Optional[str]
    time_limit_minutes: Optional[int]
    questions: List[Dict[str, Any]]   # correct_answer stripped by router
    course_id: Optional[int] = None

'''
Exam Attempt
'''

# submit exam
class ExamAttemptSubmit(BaseModel):
    session_id: int
    answers: Dict[str, Any] = Field(
        ...,
        description='{"q1": "A", "q2": "demand", "q3": ["A","C"]}',
    )

# a lesson a student can jump to after getting a topic wrong
class TopicLessonLink(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page_id: int
    title: str
    module_id: int
    module_title: Optional[str] = None
    course_id: Optional[int] = None
    topic_tag: Optional[str] = None
    is_published: bool = True
    study_url: str = Field(
        ...,
        description="frontend path of the lesson, e.g. /courses/1/modules/3/pages/42",
    )
    redirect_url: str = Field(
        ...,
        description="backend route that 307-redirects straight to study_url",
    )


# one question the student got wrong, with the teacher's explanation
class WrongQuestionDetail(BaseModel):
    '''
    correct_answer and explanation are only filled when the exam template has
    show_correct_after = True; otherwise both stay None.
    '''

    question_id: str
    type: Optional[str] = None
    text: Optional[str] = None
    topic_tag: Optional[str] = None
    points: int = 1
    answered: bool = True              # false = left blank
    your_answer: Optional[Any] = None
    correct_answer: Optional[Any] = None
    explanation: Optional[str] = None
    linked_learning_page_id: Optional[int] = None


# one wrongly-answered topic + where to go review it
class WrongTopicReview(BaseModel):
    topic_tag: str
    wrong_count: int
    total_questions: int
    score_pct: float
    is_weak: bool                      # below WEAK_THRESHOLD (60%)
    message: Optional[str] = None
    question_ids: List[str] = Field(default_factory=list)
    questions: List[WrongQuestionDetail] = Field(
        default_factory=list,
        description="the wrong questions themselves, with the teacher's explanation "
                    "when the template reveals answers after submission",
    )
    lessons: List[TopicLessonLink] = Field(default_factory=list)
    redirect_url: Optional[str] = Field(
        None,
        description="click target: redirects to the first suggested lesson; "
                    "null when no lesson is linked to this topic yet",
    )


# percentile standing of one score inside a reference group
class PercentileReport(BaseModel):
    '''
    payload built by ExamAttempt.build_report / score_report / student_percentile.
    "scope" says which attempts the percentile was measured against:
    {"session_id": 3} = one session, {"template_id": 7} = every launch of
    that exam, {} = every graded attempt by every user.
    '''

    model_config = ConfigDict(from_attributes=True)

    score_pct: float
    percentile: Optional[float] = None   # None when nobody else has a score
    rank: Optional[int] = None           # 1 = best, ties share the better rank
    population: int                      # how many scores back the percentile
    mean: Optional[float] = None
    median: Optional[float] = None
    highest: Optional[float] = None
    lowest: Optional[float] = None
    scope: Dict[str, Any] = Field(default_factory=dict)
    per_user: Optional[str] = None       # best | latest | mean | None (every attempt)
    method: Optional[str] = None         # below | midpoint | at_or_below


# attempt response
class ExamAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    session_id: int
    score: float
    max_score: float
    score_pct: float
    passed: bool
    percentile: Optional[float]          # stored, session-scoped (legacy)
    topic_stats: Dict[str, Any]
    weakness_report: List[Dict[str, Any]]
    started_at: datetime
    submitted_at: Optional[datetime]

    # computed per request, never stored: where this score stands against
    # other students' scores. null while the attempt is not graded yet.
    session_percentile: Optional[PercentileReport] = None   # vs this session
    exam_percentile: Optional[PercentileReport] = None      # vs every launch of the exam
    overall_percentile: Optional[PercentileReport] = None   # vs all users, all exams