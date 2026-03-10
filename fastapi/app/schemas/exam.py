'''
examination system.

Flow:
  Teacher  ->  creates ExamTemplate  (question_data JSON)
           ->  launches ExamSession  (snapshot frozen at launch)
  Student  ->  submits ExamAttempt   (graded, weakness_report, percentile)
'''

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


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
    explanation: Optional[str] = None
    points: int = 1
    topic_tag: Optional[str] = None
    order_index: int = 0
    linked_learning_page_id: Optional[int] = None  # cross page suggestion if wrong


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
    percentile: Optional[float]
    topic_stats: Dict[str, Any]
    weakness_report: List[Dict[str, Any]]
    started_at: datetime
    submitted_at: Optional[datetime]