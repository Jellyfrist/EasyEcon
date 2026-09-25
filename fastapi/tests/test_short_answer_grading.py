import unittest

from app.models.exam_attempt import ExamAttempt
from app.models.exam_session import ExamSession


class ShortAnswerGradingTests(unittest.TestCase):
    def test_alternative_answers_are_accepted_and_not_reported_wrong(self):
        question = {
            "id": "q1", "type": "short_answer", "text": "Consumer surplus?",
            "correct_answer": ["220 บาท/ตัว", "220", "220 บาท"],
            "points": 1, "topic_tag": "surplus",
        }
        attempt = ExamAttempt(answers={"q1": " 220 "})
        attempt.session = ExamSession(question_snapshot=[question])

        attempt.grade()

        self.assertEqual(attempt.score, 1)
        self.assertEqual(attempt.wrong_questions(), [])

    def test_multiple_choice_list_still_requires_all_choices(self):
        self.assertFalse(ExamAttempt.is_answer_correct("A", ["A", "C"], "multiple_choice"))
        self.assertTrue(ExamAttempt.is_answer_correct(["C", "A"], ["A", "C"], "multiple_choice"))


if __name__ == "__main__":
    unittest.main()
