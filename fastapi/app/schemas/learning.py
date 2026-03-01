'''
from app.schemas.learning import (
    LearningPageCreate,
    LearningPageResponse,
    LearningPageStudentResponse,
    LearningPageSummary,
    LearningPageUpdate,
    MiniQuizResult,
    MiniQuizSubmit,
    ModuleCreate,
    ModuleResponse,
    ModuleUpdate,
)

block type support in content_blocks:
    heading | paragraph | image | video | formula | divider | mini_quiz

formula block data schema:
    {
        "expression": "\\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}",  # LaTeX string
        "display": "block"   # "block" = centered on own line | "inline" = inside paragraph
    }

* backed just stores then returns the LaTeX string
'''

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# content block
class ContentBlock(BaseModel):
    '''
    A single block inside a LearningPage.
    `type` drives how the frontend renders it.
    `data` holds all type-specific fields (text, url, questions, etc.)

    Examples:
      {"id": "b1", "type": "heading",   "data": {"level": 1, "text": "Intro"}}
      {"id": "b2", "type": "paragraph", "data": {"text": "..."}}
      {"id": "b3", "type": "image",     "data": {"url": "...", "caption": "..."}}
      {"id": "b4", "type": "video",     "data": {"url": "...", "caption": "..."}}
      {"id": "b5", "type": "formula",   "data": {"language": "python", "code": "..."}}
      {"id": "b6", "type": "divider",   "data": {}}
      {"id": "b7", "type": "mini_quiz", "data": {"title": "Quick Check", "questions": [...]}}
    '''

    id: str
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)

'''
module
'''

class ModuleCreate(BaseModel):
    course_id: int
    title: str
    order_index: int = 0


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    order_index: Optional[int] = None


class ModuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    title: str
    order_index: int

'''
learning page 
'''

class LearningPageCreate(BaseModel):
    module_id: int
    title: str = "Untitled Page"
    # UI hint for starter layout; does not restrict blocks
    template_type: str = Field(
        "blank",
        description = "blank | video_lesson | text_image | mixed",
    )
    content_blocks: List[ContentBlock] = []
    order_index: int = 0
    preview: Optional[str] = None
    # backend only tag for weakness linking -> dont shown to students
    topic_tag: Optional[str] = Field(None)
    is_published: bool = False


class LearningPageUpdate(BaseModel):
    title: Optional[str] = None
    template_type: Optional[str] = None
    content_blocks: Optional[List[ContentBlock]] = None
    order_index: Optional[int] = None
    preview: Optional[str] = None
    topic_tag: Optional[str] = None
    is_published: Optional[bool] = None

# full page response: for teachers (include topic_tag)
class LearningPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    module_id: int
    title: str
    template_type: str
    content_blocks: List[ContentBlock]
    order_index: int
    preview: Optional[str]
    topic_tag: Optional[str]    # visible to teacher only
    is_published: bool
    published_at: Optional[datetime]
    last_edited_by_user_id: Optional[int]
    updated_at: datetime

class LearningPageStudentResponse(BaseModel):
    '''
    page response for student
    - topic_tag is EXCLUDED
    - correct_answer and explanation stripped from mini_quiz blocks
    '''
    model_config = ConfigDict(from_attributes=True)

    id: int
    module_id: int
    title: str
    template_type: str
    content_blocks: List[ContentBlock]   # correct_answers stripped by router
    order_index: int
    preview: Optional[str]

class LearningPageSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    template_type: str
    order_index: int
    preview: Optional[str]
    is_published: bool

'''
mini quiz submission
'''

class MiniQuizSubmit(BaseModel):
    '''
    student submit answer for a mini quiz block on a learning page
    'answers' will map question id -> student's answer
    '''
    learning_page_id: int
    answers: Dict[str, Any] = Field(
        ...,
        description='e.g. {"q1": "A", "q2": "supply"}',
    )


class MiniQuizResult(BaseModel):
    '''return after grading a mini quiz attempt'''

    model_config = ConfigDict(from_attributes=True)

    latest_score_pct: float
    best_score_pct: float
    passed: bool
    attempt_count: int
    topic_stats: Dict[str, Any]
    weakness_report: List[Dict[str, Any]]