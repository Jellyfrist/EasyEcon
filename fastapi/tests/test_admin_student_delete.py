import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.db import Base
from app.models.best_attempt import BestAttempt
from app.models.course import Course
from app.models.exam_attempt import ExamAttempt
from app.models.exam_session import ExamSession
from app.models.exam_template import ExamTemplate
from app.models.learning_page import LearningPage
from app.models.module import Module
from app.models.page_progress import PageProgress
from app.models.social_auth import SocialAuth
from app.models.user import User
from app.routers.admin import deactivate_user, delete_student


class AdminStudentDeleteTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.admin = self._user("admin", "admin")

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def _user(self, username, role):
        user = User(username=username, email=f"{username}@example.com", role=role)
        self.db.add(user)
        self.db.flush()
        return user

    def _course_content(self, owner):
        course = Course(teacher_id=owner.id, title="Economics")
        self.db.add(course)
        self.db.flush()
        module = Module(course_id=course.id, title="Supply")
        self.db.add(module)
        self.db.flush()
        page = LearningPage(
            module_id=module.id,
            title="Supply and demand",
            content_blocks=[],
            template_type="blank",
            created_by_user_id=owner.id,
        )
        self.db.add(page)
        self.db.flush()
        template = ExamTemplate(
            created_by_user_id=owner.id,
            course_id=course.id,
            title="Practice exam",
            exam_type="quiz",
            question_data=[],
        )
        self.db.add(template)
        self.db.flush()
        session = ExamSession(
            template_id=template.id,
            question_snapshot=[],
            title="Practice exam",
            launched_by_user_id=owner.id,
        )
        self.db.add(session)
        self.db.flush()
        return course, page, template, session

    def test_student_is_hard_deleted_with_personal_records_but_shared_content_remains(self):
        teacher = self._user("teacher", "teacher")
        student = self._user("student", "student")
        course, page, template, exam_session = self._course_content(teacher)
        page.last_edited_by_user_id = student.id
        self.db.add_all([
            SocialAuth(user_id=student.id, provider="google", provider_id="student-google"),
            PageProgress(student_id=student.id, learning_page_id=page.id),
            BestAttempt(student_id=student.id, learning_page_id=page.id),
            ExamAttempt(student_id=student.id, session_id=exam_session.id, answers={}),
        ])
        student_id = student.id
        course_id = course.id
        page_id = page.id
        template_id = template.id
        self.db.commit()

        response = delete_student(student_id, self.db, self.admin)
        self.db.expire_all()

        self.assertEqual(response.status_code, 204)
        self.assertIsNone(self.db.get(User, student_id))
        self.assertEqual(self.db.query(SocialAuth).filter_by(user_id=student_id).count(), 0)
        self.assertEqual(self.db.query(PageProgress).filter_by(student_id=student_id).count(), 0)
        self.assertEqual(self.db.query(BestAttempt).filter_by(student_id=student_id).count(), 0)
        self.assertEqual(self.db.query(ExamAttempt).filter_by(student_id=student_id).count(), 0)
        self.assertIsNotNone(self.db.get(Course, course_id))
        self.assertIsNotNone(self.db.get(ExamTemplate, template_id))
        self.assertIsNone(self.db.get(LearningPage, page_id).last_edited_by_user_id)

    def test_student_with_teaching_content_is_not_deleted(self):
        student = self._user("student-owner", "student")
        course = Course(teacher_id=student.id, title="Owned content")
        self.db.add(course)
        self.db.commit()

        with self.assertRaises(HTTPException) as raised:
            delete_student(student.id, self.db, self.admin)

        self.assertEqual(raised.exception.status_code, 409)
        self.assertIsNotNone(self.db.get(User, student.id))
        self.assertIsNotNone(self.db.get(Course, course.id))

    def test_teacher_deactivation_remains_soft_delete(self):
        teacher = self._user("teacher-account", "teacher")
        self.db.commit()

        result = deactivate_user(teacher.id, self.db, self.admin)

        self.assertFalse(result.is_active)
        self.assertIsNotNone(self.db.get(User, teacher.id))

    def test_hard_delete_endpoint_refuses_non_students(self):
        teacher = self._user("teacher-account", "teacher")
        self.db.commit()

        with self.assertRaises(HTTPException) as raised:
            delete_student(teacher.id, self.db, self.admin)

        self.assertEqual(raised.exception.status_code, 400)
        self.assertIsNotNone(self.db.get(User, teacher.id))


if __name__ == "__main__":
    unittest.main()
