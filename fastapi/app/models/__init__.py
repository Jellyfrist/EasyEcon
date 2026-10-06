"""Existing API names backed by the normalized physical tables."""
from .user import User, TeacherInvitation
from .social_auth import SocialAuth
from .course import Course
from .module import Module
from .learning_page import LearningPage, Topic, Asset, LessonSection, SectionAsset
from .page_progress import PageProgress
from .exam_template import ExamTemplate, Question, Choice, AcceptedAnswer, QuestionAsset
from .exam_session import ExamSession
from .exam_attempt import ExamAttempt, AttemptQuestion, AttemptAnswer, AttemptAnswerValue, AttemptAnalysis, AttemptAnalysisLesson
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
            obj.images=[QuestionAsset(image_no=i,asset=asset_for(url)) for i,url in enumerate(obj._image_urls,1)]
            obj.primary_image=obj.images[0].asset if obj.images else None
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
