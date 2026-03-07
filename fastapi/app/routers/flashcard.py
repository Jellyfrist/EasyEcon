# app/routers/learning.py (ฉบับอัปเกรดสไตล์ Flashcard)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.learning_page import LearningPage
from app.models.page_progress import PageProgress
from app.models.user import User
from app.security import require_student, require_teacher
from app.schemas.learning import LearningPageCreate, LearningPageUpdate, LearningPageResponse

router = APIRouter(prefix="/learning", tags=["learning"])

# --- Helper เหมือนแฟลชการ์ด ---
def _get_page_or_404(page_id: int, db: Session) -> LearningPage:
    page = db.get(LearningPage, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Learning page not found")
    return page

def _is_owner_or_403(page: LearningPage, user: User):
    if page.created_by_user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your lesson page")

''' 
👨‍🏫 Teacher Routes: เหมือนหน้าจัดการ Flashcard Set
'''

# 1. สร้างหน้าบทเรียนใหม่ (เหมือน create_set)
@router.post("/pages", response_model=LearningPageResponse, status_code=201)
def create_page(
    body: LearningPageCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    page = LearningPage(
        **body.model_dump(),
        created_by_user_id=teacher.id
    )
    db.add(page)
    db.commit()
    db.refresh(page)
    return page

# 2. ดึงข้อมูลบทเรียนสำหรับ Editor (เหมือน get_cards)
@router.get("/pages/{page_id}", response_model=LearningPageResponse)
def get_page_for_editor(
    page_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    page = _get_page_or_404(page_id, db)
    _is_owner_or_403(page, teacher)
    return page

# 3. อัปเดตเนื้อหา (เหมือน update_card)
@router.patch("/pages/{page_id}", response_model=LearningPageResponse)
def update_page(
    page_id: int,
    body: LearningPageUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    page = _get_page_or_404(page_id, db)
    _is_owner_or_403(page, teacher)
    
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(page, field, value)
    
    db.commit()
    db.refresh(page)
    return page

'''
🎓 Student Routes: เหมือนหน้า Study Flashcard
'''

# 4. บันทึกสถานะการเรียนจบ (เหมือน update_progress)
@router.post("/pages/{page_id}/complete", status_code=200)
def mark_page_complete(
    page_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    _get_page_or_404(page_id, db) # เช็คว่ามีหน้าจริงไหม
    
    progress = db.query(PageProgress).filter(
        PageProgress.student_id == student.id,
        PageProgress.learning_page_id == page_id
    ).first()

    if not progress:
        progress = PageProgress(
            student_id=student.id,
            learning_page_id=page_id,
            is_completed=True
        )
        db.add(progress)
    else:
        progress.is_completed = True
        
    db.commit()
    return {"status": "completed", "page_id": page_id}