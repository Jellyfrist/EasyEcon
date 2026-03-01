'''
course schemas for request/response validation

used by:
- teachers to create and manage their courses
- students to browse and view course details
'''

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

# course create
class CourseCreate(BaseModel):
    '''teacher creates a new course'''
    title: str = Field(..., max_length=50)
    description: Optional[str] = None

# course update
class CourseUpdate(BaseModel):
    '''teacher updates their course'''
    title: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None

# course response (summary)
class CourseResponse(BaseModel):
    '''basic course info for list views'''
    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # computed fields (injected by router)
    module_count: Optional[int] = None
    flashcard_set_count: Optional[int] = None
    exam_template_count: Optional[int] = None

# course detail (full view)
class CourseDetail(CourseResponse):
    '''
    full course details with all content.
    used when viewing a single course page.
    '''
    # these will be populated by the router if needed
    # for now, we just include the counts above
    # later you can add: modules: List[ModuleSummary] = [] if you want nested data
    pass

# course summary (for nested responses)
class CourseSummary(BaseModel):
    '''minimal course info for embedding in other responses'''
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    teacher_id: int