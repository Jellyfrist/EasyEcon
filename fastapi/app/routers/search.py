'''
Unified search endpoint

GET /search?q=keyword   — seaech across all content type.
    - student: courses, flashcard sets, learning pages, exam sessions.
    - teacher: only own content.
'''

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.course import Course
from app.models.flashcard import FlashcardSet
from app.models.learning_page import LearningPage
from app.models.exam_template import ExamTemplate
from app.models.user import User
from app.security import require_student, require_teacher
from pydantic import BaseModel

router = APIRouter(prefix="/search", tags=["search"])


# response schemas

class SearchResultItem(BaseModel):
    id: int
    type: str        # "course" | "flashcard" | "learning" | "exam"
    title: str
    description: Optional[str] = None
    course_id: Optional[int] = None

    model_config = {"from_attributes": True}

class SearchResponse(BaseModel):
    courses: List[SearchResultItem] = []
    flashcards: List[SearchResultItem] = []
    learning: List[SearchResultItem] = []
    exams: List[SearchResultItem] = []
    total: int = 0


# student search
@router.get("/student", response_model=SearchResponse)
def search_student(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    pattern = f"%{q}%"

    courses = (
        db.query(Course)
        .filter(
            Course.title.ilike(pattern) |
            Course.description.ilike(pattern)
        )
        .limit(5).all()
    )

    flashcards = (
        db.query(FlashcardSet)
        .filter(
            FlashcardSet.is_active == True,
            FlashcardSet.title.ilike(pattern) |
            FlashcardSet.description.ilike(pattern)
        )
        .limit(5).all()
    )

    pages = (
        db.query(LearningPage)
        .filter(
            LearningPage.is_published == True,
            LearningPage.title.ilike(pattern)
        )
        .limit(5).all()
    )

    exams = (
        db.query(ExamTemplate)
        .filter(ExamTemplate.title.ilike(pattern))
        .limit(5).all()
    )

    def to_item(obj, type_: str) -> SearchResultItem:
        return SearchResultItem(
            id=obj.id,
            type=type_,
            title=obj.title,
            description=getattr(obj, "description", None),
            course_id=getattr(obj, "course_id", None),
        )

    result_courses = [to_item(c, "course") for c in courses]
    result_flashcards = [to_item(f, "flashcard") for f in flashcards]
    result_learning = [to_item(p, "learning") for p in pages]
    result_exams = [to_item(e, "exam") for e in exams]

    return SearchResponse(
        courses=result_courses,
        flashcards=result_flashcards,
        learning=result_learning,
        exams=result_exams,
        total=len(result_courses) + len(result_flashcards) + len(result_learning) + len(result_exams),
    )


# teacher search
@router.get("/teacher", response_model=SearchResponse)
def search_teacher(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    pattern = f"%{q}%"

    courses = (
        db.query(Course)
        .filter(
            Course.teacher_id == teacher.id,
            Course.title.ilike(pattern) |
            Course.description.ilike(pattern)
        )
        .limit(5).all()
    )

    flashcards = (
        db.query(FlashcardSet)
        .filter(
            FlashcardSet.created_by_user_id == teacher.id,
            FlashcardSet.is_active == True,
            FlashcardSet.title.ilike(pattern) |
            FlashcardSet.description.ilike(pattern)
        )
        .limit(5).all()
    )

    pages = (
        db.query(LearningPage)
        .filter(
            LearningPage.created_by_user_id == teacher.id,
            LearningPage.title.ilike(pattern)
        )
        .limit(5).all()
    )

    exams = (
        db.query(ExamTemplate)
        .filter(
            ExamTemplate.created_by_user_id == teacher.id,
            ExamTemplate.title.ilike(pattern)
        )
        .limit(5).all()
    )

    def to_item(obj, type_: str) -> SearchResultItem:
        return SearchResultItem(
            id=obj.id,
            type=type_,
            title=obj.title,
            description=getattr(obj, "description", None),
            course_id=getattr(obj, "course_id", None),
        )

    result_courses = [to_item(c, "course") for c in courses]
    result_flashcards = [to_item(f, "flashcard") for f in flashcards]
    result_learning = [to_item(p, "learning") for p in pages]
    result_exams = [to_item(e, "exam") for e in exams]

    return SearchResponse(
        courses=result_courses,
        flashcards=result_flashcards,
        learning=result_learning,
        exams=result_exams,
        total=len(result_courses) + len(result_flashcards) + len(result_learning) + len(result_exams),
    )