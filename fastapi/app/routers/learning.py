'''
Teacher routes  (require_teacher):
    POST   /learning/modules                      create module
    PATCH  /learning/modules/{module_id}          update module
    DELETE /learning/modules/{module_id}          delete module + pages
    POST   /learning/pages                        create page
    GET    /learning/pages/{page_id}              get full page (with topic_tag)
    PATCH  /learning/pages/{page_id}              update page
    DELETE /learning/pages/{page_id}              delete page

Student routes  (require_student):
    GET    /learning/modules?course_id=           list published modules
    GET    /learning/modules/{module_id}/pages    list published pages in module
    GET    /learning/pages/{page_id}/study        get page (correct_answers stripped)
    POST   /learning/pages/mini-quiz              submit mini quiz answers
    GET    /learning/pages/{page_id}/my-quiz      get my best/latest score
'''

import copy
from typing import Any, Dict, List
from datetime import datetime
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db

from app.models.learning_page import LearningPage
from app.models.module import Module
from app.models.best_attempt import BestAttempt
from app.models.user import User
from app.models.page_progress import PageProgress

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
    ModuleDashboardResponse,
)

from app.security import require_student, require_teacher

router = APIRouter(prefix="/learning", tags=["learning"])

# helper

def _get_module_or_404(module_id: int, db: Session) -> Module:
    m = db.get(Module, module_id)
    if not m:
        raise HTTPException(status_code=404, detail="Module not found")
    return m

# no page
def _get_page_or_404(page_id: int, db: Session) -> LearningPage:
    p = db.get(LearningPage, page_id)
    if not p:
        raise HTTPException(status_code=404, detail="Learning page not found")
    return p


def _strip_answers(content_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    '''
    - remove correct answer and explanation from mini_quiz blocks before sending to students
    '''
    stripped = []
    for block in content_blocks:
        if block.get("type") == "mini_quiz":
            block = copy.deepcopy(block)
            for q in block.get("data", {}).get("questions", []):
                q.pop("correct_answer", None)
                q.pop("explanation", None)
        stripped.append(block)
    return stripped


'''
teacher route: module
'''

# create module
@router.post("/modules", response_model = ModuleResponse, status_code = 201)
def create_module(
    body: ModuleCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    module = Module(**body.model_dump())
    db.add(module)
    db.commit()
    db.refresh(module)
    return module

# update module
@router.patch("/modules/{module_id}", response_model = ModuleResponse)
def update_module(
    module_id: int,
    body: ModuleUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    module = _get_module_or_404(module_id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(module, field, value)
    db.commit()
    db.refresh(module)
    return module

# delete module + pages`
@router.delete("/modules/{module_id}", status_code = 204)
def delete_module(
    module_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    module = _get_module_or_404(module_id, db)
    db.delete(module)
    db.commit()


'''
teacher routes: learning pages
'''

# create page
@router.post("/pages", response_model = LearningPageResponse, status_code = 201)
def create_page(
    body: LearningPageCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):

    blocks = [b.model_dump() for b in body.content_blocks] if body.content_blocks else []
    
    page_data = {
        "module_id": body.module_id,
        "title": body.title,
        "template_type": body.template_type,
        "order_index": body.order_index,
        "preview": body.preview,
        "is_published": body.is_published,
        "content_blocks": blocks,
        "created_by_user_id": teacher.id,    
        "last_edited_by_user_id": teacher.id   
    }
    
    page = LearningPage(**page_data)
    db.add(page)
    db.commit()
    db.refresh(page)
    return page

# get full page (with topic_tag)
@router.get("/pages/{page_id}", response_model = LearningPageResponse)
def get_page_teacher(
    page_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    ''' full page including topic_tag: for teacher editor'''
    return _get_page_or_404(page_id, db)

# update page
@router.patch("/pages/{page_id}", response_model = LearningPageResponse)
def update_page(
    page_id: int,
    body: LearningPageUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    page = _get_page_or_404(page_id, db)
    data = body.model_dump(exclude_unset=True)
    if "content_blocks" in data and data["content_blocks"] is not None:
        data["content_blocks"] = [
            b.model_dump() for b in body.content_blocks
        ]
        
    data.pop("topic_tag", None)

    for field, value in data.items():
        setattr(page, field, value)
    page.last_edited_by_user_id = teacher.id
    db.commit()
    db.refresh(page)
    return page

# delete page
@router.delete("/pages/{page_id}", status_code=204)
def delete_page(
    page_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    page = _get_page_or_404(page_id, db)
    db.delete(page)
    db.commit()

'''
student route
'''

# list published modules
@router.get("/modules", response_model = List[ModuleResponse])
def list_modules_student(
    course_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''list all modules for a course so student see only published pages inside'''
    return (
        db.query(Module)
        .filter(Module.course_id == course_id)
        .order_by(Module.order_index)
        .all()
    )

# list published pages in module
@router.get("/modules/{module_id}/pages", response_model = List[LearningPageSummary])
def list_pages_student(
    module_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''list published pages in a module *summary only -> no content blocks'''
    module = _get_module_or_404(module_id, db)
    return [p for p in module.learning_pages if p.is_published]

# get page (correct_answers stripped)
@router.get("/pages/{page_id}/study", response_model = LearningPageStudentResponse)
def study_page(
    page_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''
    student reads a lesson page
    - topic tag is excluded entirely
    - correct answer and explanation stripped from mini quiz block
    '''
    page = _get_page_or_404(page_id, db)
    if not page.is_published:
        raise HTTPException(status_code = 404, detail = "Page not found")

    safe_blocks = _strip_answers(page.content_blocks)

    return LearningPageStudentResponse(
        id = page.id,
        module_id = page.module_id,
        title = page.title,
        template_type = page.template_type,
        content_blocks = safe_blocks,
        order_index = page.order_index,
        preview = page.preview,
    )

# submit mini quiz answers
@router.post("/pages/mini-quiz", response_model = MiniQuizResult)
def submit_mini_quiz(
    body: MiniQuizSubmit,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''
    - student submits answers for a mini_quiz block inside a learning page
    - finds the mini quiz block, grades, upsert best attempt
    - only best score is kept, so student can retake as many times as they want
    '''
    page = _get_page_or_404(body.learning_page_id, db)

    # find the mini quiz block in content blocks
    quiz_block = next(
        (b for b in page.content_blocks if b.get("type") == "mini_quiz"),
        None,
    )
    if not quiz_block:
        raise HTTPException(status_code = 400, detail = "This page has no mini quiz")

    questions = quiz_block.get("data", {}).get("questions", [])

    # upsert BestAttempt
    attempt = (
        db.query(BestAttempt)
        .filter(
            BestAttempt.student_id == student.id,
            BestAttempt.learning_page_id == body.learning_page_id,
        )
        .first()
    )
    if not attempt:
        attempt = BestAttempt(
            student_id = student.id,
            learning_page_id = body.learning_page_id,
            attempt_count = 0,
        )
        db.add(attempt)
        db.flush()

    attempt.grade(questions = questions, answers = body.answers)
    db.commit()
    db.refresh(attempt)
    return attempt

# get student best or latest score
@router.get("/pages/{page_id}/my-quiz", response_model = MiniQuizResult)
def get_my_quiz_result(
    page_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''returns the student's best or latest mini quiz score'''
    attempt = (
        db.query(BestAttempt)
        .filter(
            BestAttempt.student_id == student.id,
            BestAttempt.learning_page_id == page_id,
        )
        .first()
    )
    if not attempt:
        raise HTTPException(status_code = 404, detail = "No quiz attempt found for this page")
    return attempt

# Student routes: Progress Tracking
@router.post("/pages/{page_id}/complete", status_code=200)
def complete_page(
    page_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''
    - mark a learning page as completed for the current student
    - called by frontend when student clicks 'Mark as Done' or finishes video
    '''
    page = _get_page_or_404(page_id, db)
    
    progress = (
        db.query(PageProgress)
        .filter(
            PageProgress.student_id == student.id,
            PageProgress.learning_page_id == page_id,
        )
        .first()
    )
    
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
    return {"status": "success", "message": "Page marked as completed"}

@router.get("/modules/{module_id}/dashboard", response_model=ModuleDashboardResponse)
def get_module_dashboard(
    module_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''
    - calculate and return module progress data for the Vue dashboard
    - determines which pages are completed, active, or locked
    '''
    module = _get_module_or_404(module_id, db)
    
    pages = sorted(
        [p for p in module.learning_pages if p.is_published], 
        key=lambda x: x.order_index
    )
    total_count = len(pages)
    
    if total_count == 0:
        return {
            "chapterInfo": {
                "title": module.title,
                "description": "ไม่มีเนื้อหาในบทเรียนนี้",
                "progressPercent": 0,
                "completedCount": 0,
                "totalCount": 0,
                "totalTime": "0 นาที"
            },
            "lessons": []
        }

    completed_records = (
        db.query(PageProgress.learning_page_id)
        .filter(
            PageProgress.student_id == student.id,
            PageProgress.learning_page_id.in_([p.id for p in pages]),
            PageProgress.is_completed == True
        )
        .all()
    )
    
    completed_ids = [record[0] for record in completed_records]
    completed_count = len(completed_ids)
    
    progress_percent = int((completed_count / total_count) * 100)
    
    lessons_data = []
    is_next_active = True
    
    for page in pages:
        if page.id in completed_ids:
            status = "completed"
        elif is_next_active:
            status = "active"
            is_next_active = False 
        else:
            status = "locked"
            
        lessons_data.append({
            "id": page.id,
            "title": page.title,
            "subtitle": page.preview if page.preview else "เข้าสู่บทเรียนเพื่อดูเนื้อหา",
            "type": "วิดีโอ" if page.template_type == "video_lesson" else "เนื้อหา",
            "status": status
        })

    return {
        "chapterInfo": {
            "title": module.title,
            "description": "เรียนให้ครบทุกหัวข้อเพื่อปลดล็อกแบบทดสอบ Post-test และสะสมคะแนนเก็บเพื่อรับ Certificate",
            "progressPercent": progress_percent,
            "completedCount": completed_count,
            "totalCount": total_count,
            "totalTime": "N/A"
        },
        "lessons": lessons_data
    }

''' Teacher '''

teacher_router = APIRouter(prefix="/teacher", tags=["teacher_dashboard"])

class RecentActivityItem(BaseModel):
    id: int
    type: str
    title: str
    meta_info: str
    updated_at: datetime | None

@teacher_router.get("/recent-activities", response_model=List[RecentActivityItem])
def get_teacher_recent_activities(
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher)
):
    recent_pages = (
        db.query(LearningPage)
        .filter(LearningPage.created_by_user_id == teacher.id)
        .order_by(LearningPage.updated_at.desc())
        .limit(10)
        .all()
    )

    activities = []
    for page in recent_pages:
        status_text = "Published" if page.is_published else "Draft"
        activities.append(
            RecentActivityItem(
                id=page.id,
                type="lesson",
                title=page.title,
                meta_info=f"Topic {page.order_index} • {status_text}",
                updated_at=page.updated_at
            )
        )

    return activities