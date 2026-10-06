"""Existing API names backed by the normalized physical tables."""
from .user import User, TeacherInvitation
from .social_auth import SocialAuth
from .course import Course
from .module import Module
from .learning_page import LearningPage, Topic, Asset, LessonSection, SectionAsset
from .page_progress import PageProgress
from .exam_template import ExamTemplate, Question, Choice, AcceptedAnswer
from .exam_session import ExamSession
from .exam_attempt import ExamAttempt, AttemptQuestion, AttemptAnswer
from sqlalchemy import event, select, func
from sqlalchemy.orm import Session


def prepare_attempt(attempt):
    """Materialize the full frozen assessment before the existing grader runs."""
    if not hasattr(attempt, "_pending_answers"):
        return
    submitted = attempt._pending_answers
    attempt.selected_questions = []
    known = set()
    for i, question in enumerate(attempt.session.questions, 1):
        key = question.external_id
        known.add(key)
        value = submitted.get(key)
        answer = AttemptAnswer.from_value(value, key in submitted)
        answer.question = question
        if question.question_type == "short_answer" and value is not None:
            answer.typed_answer = str(value)
        elif value is not None:
            candidates = value if isinstance(value, list) else [value]
            answer.selected_choice_no = next((c.choice_no for c in question.choices
                if any(str(c.choice_text).strip().casefold() == str(v).strip().casefold()
                       for v in candidates)), None)
        attempt.selected_questions.append(AttemptQuestion(question=question, display_order=i, answer=answer))
    attempt.unmatched_answers = {k:v for k,v in submitted.items() if k not in known}
    attempt.max_score = sum((q.points for q in attempt.session.questions), 0)
    if attempt.passing_percentage_snapshot is None:
        attempt.passing_percentage_snapshot = attempt.session.template.passing_score_pct
    del attempt._pending_answers


@event.listens_for(Session, "before_flush")
def resolve_normalized_references(session, flush_context, instances):
    # No placeholder assets: a URL alone does not establish size, MIME or owner.
    def asset_for(url):
        asset = next((a for a in session.new if isinstance(a, Asset) and a.url == url), None)
        asset = asset or session.scalar(select(Asset).where(Asset.url == url))
        if asset is None:
            raise ValueError(f"Asset metadata is required for {url}; upload/register the existing file first")
        return asset

    for obj in list(session.new):
        if isinstance(obj, User) and obj.display_name is None:
            obj.display_name = obj.full_name or obj.username
        if isinstance(obj, (Module, LearningPage)) and obj.position is None:
            parent_attr = "course_id" if isinstance(obj, Module) else "module_id"
            parent_id = getattr(obj, parent_attr)
            model = type(obj)
            stored = session.scalar(select(func.max(model.position)).where(getattr(model,parent_attr)==parent_id)) or 0
            pending = [o.position or 0 for o in session.new if isinstance(o,model) and getattr(o,parent_attr)==parent_id]
            obj.position = max([stored]+pending)+1
    # Creating an assessment copy added more questions to the unit of work.
    topics = {}
    for obj in list(session.new)+list(session.dirty):
        if isinstance(obj, (LearningPage, Question)) and hasattr(obj,"_topic_name"):
            name = obj._topic_name
            if name is None:
                obj.topic = None
            else:
                if isinstance(obj, LearningPage):
                    module = obj.module or session.get(Module,obj.module_id)
                    course_id = module.course_id
                else:
                    course_id = obj.exam.course_id
                key=(course_id,name)
                if key not in topics:
                    topic=session.scalar(select(Topic).where(Topic.course_id==course_id,Topic.name==name))
                    if topic is None:
                        if session.bind.dialect.name == "postgresql":
                            from sqlalchemy.dialects.postgresql import insert
                        else:
                            from sqlalchemy.dialects.sqlite import insert
                        session.execute(insert(Topic).values(course_id=course_id,name=name)
                            .on_conflict_do_nothing(index_elements=["course_id","name"]))
                        topic=session.scalar(select(Topic).where(Topic.course_id==course_id,Topic.name==name))
                    topics[key]=topic
                obj.topic=topics[key]
            del obj._topic_name
        if isinstance(obj, Question) and hasattr(obj,"_image_urls"):
            assets = [asset_for(url) for url in obj._image_urls]
            obj.primary_image = assets[0] if assets else None
            del obj._image_urls
        if isinstance(obj, LessonSection):
            import json
            content=json.loads(obj.content_richtext)
            url=content.get("url") if obj.block_type=="image" and isinstance(content,dict) else None
            obj.assets=[SectionAsset(asset=asset_for(url))] if isinstance(url,str) else []
        if isinstance(obj, ExamAttempt):
            if obj.session is None and obj.session_id is not None:
                obj.session=session.get(ExamSession,obj.session_id)
            prepare_attempt(obj)


@event.listens_for(Session, "before_attach")
def materialize_assessment_before_session(session, obj):
    # Complete all question/answer-key inserts before opening a frozen session.
    if isinstance(obj, ExamSession) and hasattr(obj, "_template_id"):
        template = session.get(ExamTemplate, obj._template_id)
        if template is None or template.source_template_id is not None:
            raise ValueError("Unknown source exam template")
        copy = ExamTemplate(course_id=template.course_id, title=template.title,
            description=template.description, exam_type=template.exam_type,
            academic_year=template.academic_year, term=template.term,
            time_limit_minutes=template.time_limit_minutes, passing_score_pct=template.passing_score_pct,
            is_published=template.is_published, randomise_questions=template.randomise_questions,
            show_correct_after=template.show_correct_after, randomise_options=template.randomise_options,
            allow_review=template.allow_review, created_by_user_id=template.created_by_user_id,
            source_template=template,
            question_data=obj.__dict__.get("_question_snapshot",template.question_data))
        session.add(copy)
        session.flush()
        obj.assessment = copy
        del obj._template_id
        obj.__dict__.pop("_question_snapshot",None)


@event.listens_for(User, "before_insert")
def mark_new_local_subject(mapper, connection, user):
    if user.auth_subject_id is None:
        user._assign_local_subject=True


@event.listens_for(User, "after_insert")
def capture_new_local_subject(mapper, connection, user):
    # Preserve the existing JWT subject after the database allocates the user ID.
    if user.__dict__.pop("_assign_local_subject",False):
        from sqlalchemy.orm.attributes import set_committed_value
        subject=str(user.id)
        connection.execute(User.__table__.update().where(User.id==user.id)
            .values(auth_subject_id=subject,updated_at=user.updated_at))
        set_committed_value(user,"auth_subject_id",subject)


# SQL views are separate database objects, never Base subclasses/tables.
# Definitions follow the supplied SQL; API percentile semantics remain unchanged.
NORMALIZED_VIEWS = {
    'exam_result': """
SELECT a.attempt_id,a.student_id,s.exam_id,a.session_id,a.attempt_no,a.status,a.submitted_at,
 a.awarded_points,a.possible_points,a.passing_percentage_snapshot,
 CASE WHEN a.status='graded' THEN ROUND(100*a.awarded_points/NULLIF(a.possible_points,0),2) END AS score_percentage,
 CASE WHEN a.status='graded' AND a.possible_points>0 THEN 100*a.awarded_points/a.possible_points>=a.passing_percentage_snapshot END AS passed
FROM public.exam_attempt a JOIN public.exam_session s USING(session_id)
""",
    'attempt_topic_score': """
SELECT aq.attempt_id,q.topic_id,t.name AS topic_name,
 SUM(r.awarded_points) AS awarded_points,SUM(q.points) AS possible_points,
 CASE WHEN a.status='graded' THEN ROUND(100*COALESCE(SUM(r.awarded_points),0)/NULLIF(SUM(q.points),0),2) END AS percentage,
 COUNT(*) FILTER(WHERE r.is_correct IS FALSE) AS wrong_count
FROM public.attempt_question aq JOIN public.exam_attempt a USING(attempt_id)
JOIN public.question q USING(question_id) LEFT JOIN public.topic t USING(topic_id)
LEFT JOIN public.attempt_answer r ON (r.attempt_id,r.question_id)=(aq.attempt_id,aq.question_id)
GROUP BY aq.attempt_id,q.topic_id,t.name,a.status
""",
    'attempt_summary': """
SELECT a.attempt_id,COUNT(aq.question_id) AS question_count,
 COUNT(r.question_id) FILTER(WHERE r.selected_choice_no IS NOT NULL OR NULLIF(BTRIM(r.typed_answer),'') IS NOT NULL) AS answered_count
FROM public.exam_attempt a LEFT JOIN public.attempt_question aq USING(attempt_id)
LEFT JOIN public.attempt_answer r ON (r.attempt_id,r.question_id)=(aq.attempt_id,aq.question_id)
GROUP BY a.attempt_id
""",
    'exam_percentile': """
WITH cohort AS (
 SELECT DISTINCT ON (session_id,student_id) session_id,student_id,score_percentage
 FROM public.exam_result WHERE status='graded' AND score_percentage IS NOT NULL
 ORDER BY session_id,student_id,score_percentage DESC,submitted_at,attempt_id
)
SELECT r.attempt_id,COUNT(c.student_id) AS cohort_size,
 ROUND(100.0*(COUNT(c.student_id) FILTER(WHERE c.score_percentage<r.score_percentage)
 +0.5*COUNT(c.student_id) FILTER(WHERE c.score_percentage=r.score_percentage))/NULLIF(COUNT(c.student_id),0),2) AS percentile
FROM public.exam_result r LEFT JOIN cohort c ON c.session_id=r.session_id
WHERE r.status='graded' AND r.score_percentage IS NOT NULL GROUP BY r.attempt_id
""",
}

from sqlalchemy import DDL
from app.db import Base

# Explicit metadata creation on an empty test database also installs its views.
# Application startup only inspects schema; it never calls create_all.
for name, query in NORMALIZED_VIEWS.items():
    event.listen(Base.metadata, "after_create",
                 DDL(f"CREATE OR REPLACE VIEW public.{name} AS {query}").execute_if(dialect="postgresql"))
for name in reversed(NORMALIZED_VIEWS):
    event.listen(Base.metadata, "before_drop",
                 DDL(f"DROP VIEW IF EXISTS public.{name}").execute_if(dialect="postgresql"))
