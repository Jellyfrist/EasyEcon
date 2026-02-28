'''
app/routers/exam.py

Teacher routes  (require_teacher):
    POST   /exam/templates                        create exam template
    GET    /exam/templates?course_id=             list templates (past-year browser)
    GET    /exam/templates/{id}                   get full template
    PATCH  /exam/templates/{id}                   update template
    DELETE /exam/templates/{id}                   delete template
    POST   /exam/sessions                         launch session from template
    GET    /exam/sessions/{id}/results            view all student results

Student routes  (require_student):
    GET    /exam/sessions?course_id=              list open sessions for a course
    GET    /exam/sessions/{id}/open               get session with questions (answers stripped)
    POST   /exam/attempts                         submit answers -> graded immediately
    GET    /exam/attempts/{id}                    get my attempt result
    GET    /exam/sessions/{id}/my-attempts        list all my attempts for a session
'''

import copy

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.exam_attempt import ExamAttempt
from app.models.exam_session import ExamSession
from app.models.exam_template import ExamTemplate
from app.models.user import User
from app.schemas.exam import (
    ExamAttemptResponse,
    ExamAttemptSubmit,
    ExamSessionCreate,
    ExamSessionResponse,
    ExamSessionStudentResponse,
    ExamTemplateCreate,
    ExamTemplateResponse,
    ExamTemplateSummary,
    ExamTemplateUpdate,
)
from app.security import require_student, require_teacher

router = APIRouter(prefix="/exam", tags=["exam"])


# helper

def _get_template_or_404(template_id: int, db: Session) -> ExamTemplate:
    t = db.get(ExamTemplate, template_id)
    if not t:
        raise HTTPException(status_code = 404, detail = "Exam template not found")
    return t


def _get_session_or_404(session_id: int, db: Session) -> ExamSession:
    s = db.get(ExamSession, session_id)
    if not s:
        raise HTTPException(status_code = 404, detail = "Exam session not found")
    return s

def _own_template_or_403(template: ExamTemplate, teacher: User) -> None:
    if template.created_by_user_id != teacher.id and teacher.role != "admin":
        raise HTTPException(status_code=403, detail="Not your exam template")


def _strip_answers_from_questions(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    '''remove correct answer, explanation, and linked learning page id from question'''
    stripped = []
    for q in questions:
        q = copy.deepcopy(q)
        q.pop("correct_answer", None)
        q.pop("explanation", None)
        q.pop("linked_learning_page_id", None)
        stripped.append(q)
    return stripped


'''
teacher route: ExamTemplate
'''

# create exam template
@router.post("/templates", response_model=ExamTemplateResponse, status_code=201)
def create_template(
    body: ExamTemplateCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''
    - teacher creates an exam template (like a blank Google Form)
    - questions are stored as JSON *no in DB
    - topic tag is required on each question for weakness analysis
    '''
    data = body.model_dump()
    data["question_data"] = [q.model_dump() for q in body.question_data]
    template = ExamTemplate(**data, created_by_user_id=teacher.id)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

# list templates (past-year browser)
@router.get("/templates", response_model=List[ExamTemplateSummary])
def list_templates(
    course_id: int,
    exam_type: Optional[str] = None,
    academic_year: Optional[str] = None,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''
    - list exam templates for a course
    - filter by exam type (midterm/final) or academic year to browse past papers
    '''
    q = db.query(ExamTemplate).filter(ExamTemplate.course_id == course_id)
    if exam_type:
        q = q.filter(ExamTemplate.exam_type == exam_type)
    if academic_year:
        q = q.filter(ExamTemplate.academic_year == academic_year)
    return q.order_by(ExamTemplate.academic_year.desc()).all()

# get full template
@router.get("/templates/{template_id}", response_model=ExamTemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    return _get_template_or_404(template_id, db)

# update template
@router.patch("/templates/{template_id}", response_model=ExamTemplateResponse)
def update_template(
    template_id: int,
    body: ExamTemplateUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    template = _get_template_or_404(template_id, db)
    _own_template_or_403(template, teacher)
    data = body.model_dump(exclude_unset = True)
    if "question_data" in data and data["question_data"] is not None:
        data["question_data"] = [q.model_dump() for q in body.question_data]
    for field, value in data.items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template

# delete template
@router.delete("/templates/{template_id}", status_code=204)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    template = _get_template_or_404(template_id, db)
    _own_template_or_403(template, teacher)
    db.delete(template)
    db.commit()

'''
teacher route: Exam Session
'''

# launch session from template
@router.post("/sessions", response_model = ExamSessionResponse, status_code = 201)
def launch_session(
    body: ExamSessionCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''
    - teacher launches an exam session from a template
    - question snapshot is frozen at this moment: safe to edit template later
    '''
    template = _get_template_or_404(body.template_id, db)
    session = ExamSession(
        **body.model_dump(),
        # frozen copy
        question_snapshot=template.question_data,
        launched_by_user_id=teacher.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

# view all student results
@router.get("/sessions/{session_id}/results", response_model = List[ExamAttemptResponse])
def session_results(
    session_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''teacher views all student results + weakness reports for a session'''
    _get_session_or_404(session_id, db)
    return (
        db.query(ExamAttempt)
        .filter(ExamAttempt.session_id == session_id)
        .order_by(ExamAttempt.score_pct.desc())
        .all()
    )


'''
student route
'''

# list open sessions for a course
@router.get("/sessions", response_model = List[ExamSessionResponse])
def list_open_sessions(
    course_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''list all active exam sessions for a course that are currently open'''
    sessions = (
        db.query(ExamSession)
        .join(ExamTemplate)
        .filter(
            ExamTemplate.course_id == course_id,
            ExamSession.is_active == True,
        )
        .all()
    )
    return [s for s in sessions if s.is_open]

# get session with questions (answers stripped)
@router.get("/sessions/{session_id}/open", response_model = ExamSessionStudentResponse)
def open_session_for_student(
    session_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''
    - student open an exam session.
    - return questions with correct answer, explanation, and linked learning page id
    all stripped out, so student only sees the question text and options.
    '''
    session = _get_session_or_404(session_id, db)
    if not session.is_open:
        raise HTTPException(status_code = 400, detail = "This exam is not currently open")

    safe_questions = _strip_answers_from_questions(session.question_snapshot)

    return ExamSessionStudentResponse(
        id = session.id,
        title = session.title,
        instructions = session.instructions,
        time_limit_minutes = session.time_limit_minutes,
        questions = safe_questions,
    )

# submit answers -> graded immediately
@router.post("/attempts", response_model = ExamAttemptResponse, status_code = 201)
def submit_attempt(
    body: ExamAttemptSubmit,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''
    - student submit exam answers.
    - graded immediately from question snapshot (no extra DB queries).
    - percentiles recalculated for all attempts in this session.
    - returns full result including weakness report and suggested page IDs.
    '''
    session = _get_session_or_404(body.session_id, db)
    if not session.is_open:
        raise HTTPException(status_code = 400, detail = "This exam is not currently open")

    '''
    - past exam (routers/exam.py) has max_attempts controlled by the teacher
    when launching the session.
    - this is intentional: a teacher might set max_attempts=1 for a real exam,
    or max_attempts = 0 (unlimited) for practice.
    '''
    if session.max_attempts > 0:
        existing_count = (
            db.query(ExamAttempt)
            .filter(
                ExamAttempt.session_id == body.session_id,
                ExamAttempt.student_id == student.id,
            )
            .count()
        )
        if existing_count >= session.max_attempts:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {session.max_attempts} attempt(s) allowed",
            )

    attempt = ExamAttempt(
        student_id=student.id,
        session_id=body.session_id,
        answers=body.answers,
        submitted_at=datetime.now(timezone.utc),
    )
    db.add(attempt)
    db.flush()  # get attempt.id

    passing_pct = (
        session.template.passing_score_pct
        if session.template
        else 60
    )
    attempt.grade(passing_score_pct=passing_pct)
    db.commit()

    # recalculate percentiles for everyone in this session
    ExamAttempt.recalculate_percentiles(db, session_id = body.session_id)
    db.commit()
    db.refresh(attempt)
    return attempt

# get my attempt result
@router.get("/attempts/{attempt_id}", response_model = ExamAttemptResponse)
def get_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''student retrieves their own attempt result'''
    attempt = db.get(ExamAttempt, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.student_id != student.id and student.role not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="Not your attempt")
    return attempt

# list all my attempts for a session
@router.get("/sessions/{session_id}/my-attempts", response_model = List[ExamAttemptResponse])
def my_attempts(
    session_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student),
):
    '''list all of the student's attempts for a session'''
    return (
        db.query(ExamAttempt)
        .filter(
            ExamAttempt.session_id == session_id,
            ExamAttempt.student_id == student.id,
        )
        .order_by(ExamAttempt.submitted_at.desc())
        .all()
    )