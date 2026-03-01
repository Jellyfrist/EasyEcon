'''
course = top-level container for 3 contents

Teacher routes (require_teacher):
    POST   /courses                       create course
    GET    /courses                       list my courses
    GET    /courses/{course_id}           get my course details
    PATCH  /courses/{course_id}           update my course
    DELETE /courses/{course_id}           delete course + all content

Student routes (require_student):
    GET    /courses                       browse all public courses
    GET    /courses/{course_id}           view course details
'''

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.course import Course
from app.models.user import User
from app.schemas.course import (
    CourseCreate,
    CourseDetail,
    CourseResponse,
    CourseUpdate,
)
from app.security import require_student, require_teacher

router = APIRouter(prefix="/courses", tags=["courses"])


# helpers

def _get_course_or_404(course_id: int, db: Session) -> Course:
    '''fetch course or raise 404'''
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code = 404, detail = "Course not found")
    return course


def _own_course_or_403(course: Course, teacher: User) -> None:
    '''verify teacher owns this course or is admin'''
    if course.teacher_id != teacher.id and teacher.role != "admin":
        raise HTTPException(status_code = 403, detail = "Not your course")


def _inject_counts(course: Course) -> CourseResponse:
    '''
    add content counts to course response.
    this avoids N+1 queries when listing multiple courses.
    '''
    response = CourseResponse.model_validate(course)
    response.module_count = len(course.modules)
    response.flashcard_set_count = len(course.flashcard_sets)
    response.exam_template_count = len(course.exam_templates)
    return response

'''
teacher routes
'''

# create course
@router.post("", response_model = CourseResponse, status_code = 201)
def create_course(
    body: CourseCreate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''teacher creates a new course container'''
    course = Course(**body.model_dump(), teacher_id = teacher.id)
    db.add(course)
    db.commit()
    db.refresh(course)
    return _inject_counts(course)

# list my courses
@router.get("", response_model = List[CourseResponse])
def list_courses(
    search: Optional[str] = Query(None, description = "search in title/description"),
    db: Session = Depends(get_db),
    user: User = Depends(require_teacher)  # teachers can also browse as students
):
    '''
    list courses:
    - teachers see only their own courses
    - students see all courses (when called with require_student)
    
    note: this endpoint is called by BOTH teacher and student frontends,
    but with different auth dependencies injected by the frontend router.
    '''
    
    # check if user is teacher viewing their own courses
    if user.role == "teacher":
        query = db.query(Course).filter(Course.teacher_id == user.id)
    else:
        # student: see all courses
        query = db.query(Course)
    
    # apply search filter if provided
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Course.title.ilike(search_pattern)) |
            (Course.description.ilike(search_pattern))
        )
    
    courses = query.order_by(Course.updated_at.desc()).all()
    return [_inject_counts(c) for c in courses]

# get course details
@router.get("/{course_id}", response_model = CourseDetail)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_teacher),  # or require_student depending on call
):
    '''
    get full course details with content counts.
    - teachers can only view their own courses
    - students can view any course
    '''
    course = _get_course_or_404(course_id, db)
    
    # if teacher, verify ownership
    if user.role == "teacher":
        _own_course_or_403(course, user)
    
    return _inject_counts(course)

# update course
@router.patch("/{course_id}", response_model = CourseResponse)
def update_course(
    course_id: int,
    body: CourseUpdate,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''teacher updates their course title/description'''
    course = _get_course_or_404(course_id, db)
    _own_course_or_403(course, teacher)
    
    for field, value in body.model_dump(exclude_unset = True).items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return _inject_counts(course)

# delete course
@router.delete("/{course_id}", status_code = 204)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    teacher: User = Depends(require_teacher),
):
    '''
    - teacher deletes their course
    - deletes all modules, flashcard sets, exam templates, and nested content
    '''
    course = _get_course_or_404(course_id, db)
    _own_course_or_403(course, teacher)
    db.delete(course)
    db.commit()

'''
student routes
'''

# browse all courses (student version)
@router.get("/browse/all", response_model = List[CourseResponse])
def browse_courses_student(
    search: Optional[str] = Query(None, description = "search in title/description"),
    db: Session = Depends(get_db),
    student: User = Depends(require_student)
):
    '''
    - students browse all public courses
    - support search by title/description
    '''
    query = db.query(Course)
    
    # apply search filter if provided
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Course.title.ilike(search_pattern)) |
            (Course.description.ilike(search_pattern))
        )
    
    courses = query.order_by(Course.updated_at.desc()).all()
    return [_inject_counts(c) for c in courses]

# view course details (student version)
@router.get("/{course_id}/view", response_model=CourseDetail)
def view_course_student(
    course_id: int,
    db: Session = Depends(get_db),
    student: User = Depends(require_student)
):
    '''
    - students view any course details
    - shows flashcard, learning and exam available in this course
    '''
    course = _get_course_or_404(course_id, db)
    return _inject_counts(course)