'''
Teacher routes  (require_teacher):
    POST   /flashcards/sets                       create a set
    GET    /flashcards/sets?course_id=            list sets for a course
    PATCH  /flashcards/sets/{set_id}              update set title/description
    DELETE /flashcards/sets/{set_id}              delete set + all cards
    POST   /flashcards/sets/{set_id}/cards        add a card
    PATCH  /flashcards/cards/{card_id}            edit a card
    DELETE /flashcards/cards/{card_id}            delete a card

Student routes  (require_student):
    GET    /flashcards/sets/{set_id}/study        get set + cards + my progress
    POST   /flashcards/progress                   mark card known/learning
    GET    /flashcards/sets/{set_id}/progress     my progress summary for a set
'''

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.db import get_db

from app.models.flashcard import Flashcard, FlashcardProgress, FlashcardSet
from app.models.user import User

from app.schemas.flashcard import (
    FlashcardCreate,
    FlashcardProgressUpdate,
    FlashcardResponse,
    FlashcardStudentResponse,
    FlashcardSetCreate,
    FlashcardSetDetail,
    FlashcardSetProgress,
    FlashcardSetResponse,
    FlashcardSetUpdate,
    FlashcardUpdate,
)

from app.security import require_student, require_teacher

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


# helpers
# not found flashcard set
def _get_set_or_404(set_id: int, db: Session) -> FlashcardSet:
    fs = db.get(FlashcardSet, set_id)
    if not fs:
        raise HTTPException(status_code = 404, detail = "Flashcard set not found")
    return fs

def _own_set_or_403(fs: FlashcardSet, teacher: User) -> None:
    if fs.created_by_user_id != teacher.id and teacher.role != "admin":
        raise HTTPException(status_code=403, detail="Not your flashcard set")

'''
teacher router
'''

# create a set
@router.post("/sets", response_model=FlashcardSetResponse, status_code=201)
def create_set(
    body: FlashcardSetCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''teacher creates a new flashcard topic for a course'''
    fs = FlashcardSet(
        **body.model_dump(),
        created_by_user_id=teacher.id,
    )
    db.add(fs)
    db.commit()
    db.refresh(fs)
    result = FlashcardSetResponse.model_validate(fs)
    result.card_count = 0
    return result

# list sets for a course
@router.get("/sets", response_model=List[FlashcardSetResponse])
def list_sets_teacher(
    course_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''list all flashcard sets that teacher created for a course'''
    sets = (
        db.query(FlashcardSet)
        .filter(
            FlashcardSet.course_id == course_id,
            FlashcardSet.created_by_user_id == teacher.id,
        )
        .all()
    )
    results = []
    for fs in sets:
        r = FlashcardSetResponse.model_validate(fs)
        r.card_count = len(fs.cards)
        results.append(r)
    return results

# update set title/description
@router.patch("/sets/{set_id}", response_model = FlashcardSetResponse)
def update_set(
    set_id: int,
    body: FlashcardSetUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    fs = _get_set_or_404(set_id, db)
    _own_set_or_403(fs, teacher)
    for field, value in body.model_dump(exclude_unset = True).items():
        setattr(fs, field, value)
    db.commit()
    db.refresh(fs)
    r = FlashcardSetResponse.model_validate(fs)
    r.card_count = len(fs.cards)
    return r

# delete set + all cards
@router.delete("/sets/{set_id}", status_code=204)
def delete_set(
    set_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    fs = _get_set_or_404(set_id, db)
    _own_set_or_403(fs, teacher)
    db.delete(fs)
    db.commit()

# add a card
@router.post("/sets/{set_id}/cards", response_model = FlashcardResponse, status_code = 201)
def add_card(
    set_id: int,
    body: FlashcardCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''teacher adds a card (term / definition / hint) to a set'''
    fs = _get_set_or_404(set_id, db)
    _own_set_or_403(fs, teacher)
    card = Flashcard(set_id = set_id, **body.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return card

# edit a card
@router.patch("/cards/{card_id}", response_model = FlashcardResponse)
def update_card(
    card_id: int,
    body: FlashcardUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    card = db.get(Flashcard, card_id)
    if not card:
        raise HTTPException(status_code = 404, detail = "Card not found")
    for field, value in body.model_dump(exclude_unset = True).items():
        setattr(card, field, value)
    db.commit()
    db.refresh(card)
    return card

# delete a card
@router.delete("/cards/{card_id}", status_code=204)
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    card = db.get(Flashcard, card_id)
    if not card:
        raise HTTPException(status_code = 404, detail = "Card not found")
    _own_set_or_403(card.flashcard_set, teacher)
    db.delete(card)
    db.commit()

'''
student route
'''

# get set + cards + my progress
@router.get("/sets/{set_id}/study", response_model = FlashcardSetDetail)
def study_set(
    set_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''
    - student opens a flashcard set to study
    - returns all active cards with the student's current status injected
    '''
    fs = _get_set_or_404(set_id, db)

    # build a map of card_id -> status for this student
    progress_map = {
        p.flashcard_id: p.status
        for p in db.query(FlashcardProgress).filter(
            FlashcardProgress.student_id == student.id,
            FlashcardProgress.flashcard_id.in_([c.id for c in fs.cards]),
        ).all()
    }

    cards_with_status = [
        FlashcardStudentResponse(
            id = c.id,
            term = c.term,
            definition = c.definition,
            hint = c.hint,
            image_url = c.image_url,
            order_index = c.order_index,
            status = progress_map.get(c.id),  # none if not yet reviewed
        )
        for c in fs.cards
        if c.is_active
    ]

    return FlashcardSetDetail(
        id = fs.id,
        course_id = fs.course_id,
        created_by_user_id = fs.created_by_user_id,
        title = fs.title,
        description = fs.description,
        created_at = fs.created_at,
        updated_at = fs.updated_at,
        card_count = len(cards_with_status),
        cards = cards_with_status,
    )

# mark card known/learning
@router.post("/progress", status_code=200)
def update_progress(
    body: FlashcardProgressUpdate,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''
    - student marks a card as 'known' or 'learning'
    - upsert: one row per (student, card)
    '''

    if body.status not in ("known", "learning"):
        raise HTTPException(status_code = 400, detail = "status must be 'known' or 'learning'")

    progress = (
        db.query(FlashcardProgress)
        .filter(
            FlashcardProgress.student_id == student.id,
            FlashcardProgress.flashcard_id == body.flashcard_id,
        )
        .first()
    )
    if progress:
        progress.status = body.status
    else:
        progress = FlashcardProgress(
            student_id = student.id,
            flashcard_id = body.flashcard_id,
            status = body.status,
        )
        db.add(progress)

    db.commit()
    return {"flashcard_id": body.flashcard_id, "status": body.status}

# my progress summary for a set
@router.get("/sets/{set_id}/progress", response_model = FlashcardSetProgress)
def get_set_progress(
    set_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''
    - returns a summary: how many cards are known / learning / not started
    - show the 'X words learned' counter on the student dashboard
    '''
    fs = _get_set_or_404(set_id, db)
    active_cards = [c for c in fs.cards if c.is_active]
    card_ids = [c.id for c in active_cards]

    progress_map = {
        p.flashcard_id: p.status
        for p in db.query(FlashcardProgress).filter(
            FlashcardProgress.student_id == student.id,
            FlashcardProgress.flashcard_id.in_(card_ids),
        ).all()
    }

    known = sum(1 for cid in card_ids if progress_map.get(cid) == "known")
    learning = sum(1 for cid in card_ids if progress_map.get(cid) == "learning")
    not_started = len(card_ids) - known - learning

    return FlashcardSetProgress(
        set_id = set_id,
        title = fs.title,
        total_cards = len(card_ids),
        known_count = known,
        learning_count = learning,
        not_started_count = not_started,
    )