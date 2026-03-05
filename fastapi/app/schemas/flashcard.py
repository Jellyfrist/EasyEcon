'''
from app.schemas.flashcard import (
    FlashcardCreate,
    FlashcardProgressUpdate,
    FlashcardResponse,
    FlashcardSetCreate,
    FlashcardSetDetail,
    FlashcardSetProgress,
    FlashcardSetResponse,
    FlashcardSetUpdate,
    FlashcardStudentResponse,
    FlashcardUpdate,
)
'''

from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# flashcard

class FlashcardCreate(BaseModel):
    term: str
    definition: str
    hint: Optional[str] = None
    image_url: Optional[str] = None
    order_index: int = 0


class FlashcardUpdate(BaseModel):
    term: Optional[str] = None
    definition: Optional[str] = None
    hint: Optional[str] = None
    image_url: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None


class FlashcardResponse(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    set_id: int
    term: str
    definition: str
    hint: Optional[str]
    image_url: Optional[str]
    order_index: int
    is_active: bool
    created_at: datetime


class FlashcardStudentResponse(BaseModel):
    '''sent to student: same fields, but progress status is injected by router'''
    model_config = ConfigDict(from_attributes=True)

    id: int
    term: str
    definition: str
    hint: Optional[str]
    image_url: Optional[str]
    order_index: int
    # injected from FlashcardProgress: none if student hasnt reviewed yet
    status: Optional[str] = None


# flashcard set

class FlashcardSetCreate(BaseModel):
    course_id: int
    title: str
    description: Optional[str] = None


class FlashcardSetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class FlashcardSetResponse(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    course_id: int
    created_by_user_id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    card_count: Optional[int] = None  # injected by router


class FlashcardSetDetail(FlashcardSetResponse):
    '''full set with all cards: used when teacher edits or student study'''
    cards: List[FlashcardStudentResponse] = []


# flashcard progress

class FlashcardProgressUpdate(BaseModel):
    '''student marks a card as known or learning'''
    flashcard_id: int
    status: str  # "known" or "learning"


class FlashcardSetProgress(BaseModel):
    '''summary shown on student dashboard for a set'''
    set_id: int
    title: str
    total_cards: int
    known_count: int
    learning_count: int
    not_started_count: int