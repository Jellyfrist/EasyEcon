'''
Teacher routes:
    POST   /flashcards/sets                           create a set
    GET    /flashcards/sets?course_id=                list active sets
    PATCH  /flashcards/sets/{set_id}                  update set
    DELETE /flashcards/sets/{set_id}                  soft delete set + cards
    GET    /flashcards/sets/{set_id}/cards            list active cards
    POST   /flashcards/sets/{set_id}/cards            add a card
    PATCH  /flashcards/cards/{card_id}                edit a card
    DELETE /flashcards/cards/{card_id}                soft delete a card
    POST   /flashcards/upload-image                   upload image to supabase
    GET    /flashcards/recycle-bin?course_id=         list deleted sets + cards
    POST   /flashcards/sets/{set_id}/restore          restore a soft-deleted set
    POST   /flashcards/cards/{card_id}/restore        restore a soft-deleted card
    DELETE /flashcards/sets/{set_id}/permanent        permanent delete set
    DELETE /flashcards/cards/{card_id}/permanent      permanent delete card

Student routes:
    GET    /flashcards/sets/{set_id}/study            get set + cards + progress
    POST   /flashcards/progress                       mark card known/learning
    GET    /flashcards/sets/{set_id}/progress         progress summary
'''

import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List
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
from app.schemas.learning import LearningPageCreate, LearningPageUpdate, LearningPageResponse

router = APIRouter(prefix='/flashcards', tags=['flashcards'])

UTC = timezone.utc
RECYCLE_BIN_DAYS = 30  # auto delete after this 30 days

'''
supabase storage
'''

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')
BUCKET = 'flashcard-images'

def _supabase_headers():
    return {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
    }

def _public_url(file_path: str) -> str:
    return f'{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{file_path}'

async def _upload_to_supabase(file: UploadFile) -> str:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise HTTPException(status_code=500, detail='supabase storage not configured')
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
    file_path = f'{uuid.uuid4()}.{ext}'
    content = await file.read()
    upload_url = f'{SUPABASE_URL}/storage/v1/object/{BUCKET}/{file_path}'
    headers = {**_supabase_headers(), 'Content-Type': file.content_type or 'image/jpeg'}
    async with httpx.AsyncClient() as client:
        res = await client.post(upload_url, content=content, headers=headers)
        if res.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail=f'image upload failed: {res.text}')
    return _public_url(file_path)

async def _delete_from_supabase(image_url: str):
    if not image_url or not SUPABASE_URL:
        return
    prefix = f'{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/'
    if not image_url.startswith(prefix):
        return
    file_path = image_url[len(prefix):]
    delete_url = f'{SUPABASE_URL}/storage/v1/object/{BUCKET}/{file_path}'
    async with httpx.AsyncClient() as client:
        await client.delete(delete_url, headers=_supabase_headers())


'''
db helpers
'''

def _get_set_or_404(set_id: int, db: Session) -> FlashcardSet:
    '''get active set or raise 404'''
    fs = db.get(FlashcardSet, set_id)
    if not fs or not fs.is_active:
        raise HTTPException(status_code=404, detail='Flashcard set not found')
    return fs

def _get_any_set_or_404(set_id: int, db: Session) -> FlashcardSet:
    '''get any set (active or deleted) — used for restore and permanent delete'''
    fs = db.get(FlashcardSet, set_id)
    if not fs:
        raise HTTPException(status_code=404, detail='Flashcard set not found')
    return fs

def _get_any_card_or_404(card_id: int, db: Session) -> Flashcard:
    '''get any card (active or deleted) — used for restore and permanent delete'''
    card = db.get(Flashcard, card_id)
    if not card:
        raise HTTPException(status_code=404, detail='Card not found')
    return card

def _own_set_or_403(fs: FlashcardSet, teacher: User):
    if fs.created_by_user_id != teacher.id and teacher.role != 'admin':
        raise HTTPException(status_code=403, detail='Not your flashcard set')
    

'''
image upload
'''

@router.post('/upload-image')
async def upload_image(
    file: UploadFile = File(...),
    teacher: User = Depends(require_teacher),
):
    allowed = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail='only jpeg, png, webp, gif allowed')
    url = await _upload_to_supabase(file)
    return {'url': url}


'''
teacher: sets
'''

@router.post('/sets', response_model=FlashcardSetResponse, status_code=201)
def create_set(
    body: FlashcardSetCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    fs = FlashcardSet(**body.model_dump(), created_by_user_id=teacher.id)
    db.add(fs)
    db.commit()
    db.refresh(fs)
    result = FlashcardSetResponse.model_validate(fs)
    result.card_count = 0
    return result

@router.get('/sets', response_model=List[FlashcardSetResponse])
def list_sets_teacher(
    course_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    sets = (
        db.query(FlashcardSet)
        .filter(
            FlashcardSet.course_id == course_id,
            FlashcardSet.created_by_user_id == teacher.id,
            FlashcardSet.is_active == True,
        )
        .all()
    )
    results = []
    for fs in sets:
        r = FlashcardSetResponse.model_validate(fs)
        r.card_count = len([c for c in fs.cards if c.is_active])
        results.append(r)
    return results

@router.patch('/sets/{set_id}', response_model=FlashcardSetResponse)
def update_set(
    set_id: int,
    body: FlashcardSetUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    fs = _get_set_or_404(set_id, db)
    _own_set_or_403(fs, teacher)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(fs, field, value)
    db.commit()
    db.refresh(fs)
    r = FlashcardSetResponse.model_validate(fs)
    r.card_count = len([c for c in fs.cards if c.is_active])
    return r

@router.delete('/sets/{set_id}', status_code=204)
def delete_set(
    set_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''soft delete: hide set and all its cards, recoverable from recycle bin'''
    fs = _get_set_or_404(set_id, db)
    _own_set_or_403(fs, teacher)
    now = datetime.now(UTC)
    fs.is_active = False
    fs.deleted_at = now
    for card in fs.cards:
        if card.is_active:
            card.is_active = False
            card.deleted_at = now
    db.commit()



'''
teacher: cards
'''

@router.get('/sets/{set_id}/cards', response_model=List[FlashcardResponse])
def get_cards(
    set_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    fs = _get_set_or_404(set_id, db)
    _own_set_or_403(fs, teacher)
    return [c for c in fs.cards if c.is_active]

@router.post('/sets/{set_id}/cards', response_model=FlashcardResponse, status_code=201)
def add_card(
    set_id: int,
    body: FlashcardCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    fs = _get_set_or_404(set_id, db)
    _own_set_or_403(fs, teacher)
    card = Flashcard(set_id=set_id, **body.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return card

@router.patch('/cards/{card_id}', response_model=FlashcardResponse)
def update_card(
    card_id: int,
    body: FlashcardUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    card = db.get(Flashcard, card_id)
    if not card or not card.is_active:
        raise HTTPException(status_code=404, detail='Card not found')
    _own_set_or_403(card.flashcard_set, teacher)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(card, field, value)
    db.commit()
    db.refresh(card)
    return card

@router.delete('/cards/{card_id}', status_code=204)
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''soft delete: hide card, recoverable from recycle bin'''
    card = db.get(Flashcard, card_id)
    if not card or not card.is_active:
        raise HTTPException(status_code=404, detail='Card not found')
    _own_set_or_403(card.flashcard_set, teacher)
    card.is_active = False
    card.deleted_at = datetime.now(UTC)
    db.commit()


'''
recycle bin
'''

@router.get('/recycle-bin')
def get_recycle_bin(
    course_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''
    returns all soft-deleted sets and orphan cards for a course.
    items older than 30 days show a warning that they will be auto-purged.
    '''
    now = datetime.now(UTC)
    cutoff = now - timedelta(days=RECYCLE_BIN_DAYS)

    # deleted sets belonging to this teacher + course
    deleted_sets = (
        db.query(FlashcardSet)
        .filter(
            FlashcardSet.course_id == course_id,
            FlashcardSet.created_by_user_id == teacher.id,
            FlashcardSet.is_active == False,
        )
        .all()
    )

    # deleted cards whose parent set is still active (orphan deleted cards)
    deleted_cards = (
        db.query(Flashcard)
        .join(FlashcardSet, Flashcard.set_id == FlashcardSet.id)
        .filter(
            FlashcardSet.course_id == course_id,
            FlashcardSet.created_by_user_id == teacher.id,
            FlashcardSet.is_active == True,
            Flashcard.is_active == False,
        )
        .all()
    )

    def days_left(deleted_at):
        if not deleted_at:
            return RECYCLE_BIN_DAYS
        # make deleted_at timezone-aware if it's naive
        if deleted_at.tzinfo is None:
            deleted_at = deleted_at.replace(tzinfo=UTC)
        remaining = (deleted_at + timedelta(days=RECYCLE_BIN_DAYS) - now).days
        return max(0, remaining)

    return {
        'deleted_sets': [
            {
                'id': fs.id,
                'title': fs.title,
                'description': fs.description,
                'deleted_at': fs.deleted_at,
                'days_left': days_left(fs.deleted_at),
                'card_count': len(fs.cards),
            }
            for fs in deleted_sets
        ],
        'deleted_cards': [
            {
                'id': c.id,
                'set_id': c.set_id,
                'set_title': c.flashcard_set.title,
                'term': c.term,
                'definition': c.definition,
                'deleted_at': c.deleted_at,
                'days_left': days_left(c.deleted_at),
            }
            for c in deleted_cards
        ],
    }

@router.post('/sets/{set_id}/restore', status_code=200)
def restore_set(
    set_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''restore a soft-deleted set and all its cards'''
    fs = _get_any_set_or_404(set_id, db)
    _own_set_or_403(fs, teacher)
    if fs.is_active:
        raise HTTPException(status_code=400, detail='Set is not deleted')
    fs.is_active = True
    fs.deleted_at = None
    for card in fs.cards:
        card.is_active = True
        card.deleted_at = None
    db.commit()
    return {'message': f'Set "{fs.title}" restored successfully'}

@router.post('/cards/{card_id}/restore', status_code=200)
def restore_card(
    card_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''restore a single soft-deleted card'''
    card = _get_any_card_or_404(card_id, db)
    _own_set_or_403(card.flashcard_set, teacher)
    if card.is_active:
        raise HTTPException(status_code=400, detail='Card is not deleted')
    # restore card only if its parent set is active
    if not card.flashcard_set.is_active:
        raise HTTPException(
            status_code=400,
            detail='Cannot restore card: parent set is deleted. Restore the set first.'
        )
    card.is_active = True
    card.deleted_at = None
    db.commit()
    return {'message': f'Card "{card.term}" restored successfully'}

@router.delete('/sets/{set_id}/permanent', status_code=204)
async def permanent_delete_set(
    set_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''permanently delete a set from recycle bin — removes db rows and images'''
    fs = _get_any_set_or_404(set_id, db)
    _own_set_or_403(fs, teacher)
    if fs.is_active:
        raise HTTPException(status_code=400, detail='Soft delete the set first before permanent delete')
    for card in fs.cards:
        if card.image_url:
            await _delete_from_supabase(card.image_url)
    db.delete(fs)
    db.commit()

@router.delete('/cards/{card_id}/permanent', status_code=204)
async def permanent_delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''permanently delete a card from recycle bin — removes db row and image'''
    card = _get_any_card_or_404(card_id, db)
    _own_set_or_403(card.flashcard_set, teacher)
    if card.is_active:
        raise HTTPException(status_code=400, detail='Soft delete the card first before permanent delete')
    if card.image_url:
        await _delete_from_supabase(card.image_url)
    db.delete(card)
    db.commit()


'''
student routes
'''

@router.get('/sets/{set_id}/study', response_model=FlashcardSetDetail)
def study_set(
    set_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    fs = _get_set_or_404(set_id, db)
    progress_map = {
        p.flashcard_id: p.status
        for p in db.query(FlashcardProgress).filter(
            FlashcardProgress.student_id == student.id,
            FlashcardProgress.flashcard_id.in_([c.id for c in fs.cards]),
        ).all()
    }
    cards_with_status = [
        FlashcardStudentResponse(
            id=c.id,
            term=c.term,
            definition=c.definition,
            hint=c.hint,
            image_url=c.image_url,
            order_index=c.order_index,
            status=progress_map.get(c.id),
        )
        for c in fs.cards
        if c.is_active
    ]
    return FlashcardSetDetail(
        id=fs.id,
        course_id=fs.course_id,
        created_by_user_id=fs.created_by_user_id,
        title=fs.title,
        description=fs.description,
        created_at=fs.created_at,
        updated_at=fs.updated_at,
        card_count=len(cards_with_status),
        cards=cards_with_status,
    )

@router.post('/progress', status_code=200)
def update_progress(
    body: FlashcardProgressUpdate,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    if body.status not in ('known', 'learning'):
        raise HTTPException(status_code=400, detail="status must be 'known' or 'learning'")
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
            student_id=student.id,
            flashcard_id=body.flashcard_id,
            status=body.status,
        )
        db.add(progress)
    db.commit()
    return {'flashcard_id': body.flashcard_id, 'status': body.status}

@router.get('/sets/{set_id}/progress', response_model=FlashcardSetProgress)
def get_set_progress(
    set_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
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
    known = sum(1 for cid in card_ids if progress_map.get(cid) == 'known')
    learning = sum(1 for cid in card_ids if progress_map.get(cid) == 'learning')
    return FlashcardSetProgress(
        set_id=set_id,
        title=fs.title,
        total_cards=len(card_ids),
        known_count=known,
        learning_count=learning,
        not_started_count=len(card_ids) - known - learning,
    )