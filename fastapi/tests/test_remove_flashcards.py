import contextlib
import io
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.remove_flashcards import migrate


class RemoveFlashcardsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'test.db'
        self.url = f'sqlite:///{self.path}'
        with sqlite3.connect(self.path) as db:
            db.executescript('''
                PRAGMA foreign_keys = ON;
                CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT);
                CREATE TABLE flashcard_sets (id INTEGER PRIMARY KEY, course_id INTEGER REFERENCES courses(id));
                CREATE TABLE flashcards (id INTEGER PRIMARY KEY, set_id INTEGER REFERENCES flashcard_sets(id));
                CREATE TABLE flashcard_progress (id INTEGER PRIMARY KEY, card_id INTEGER REFERENCES flashcards(id));
                INSERT INTO courses VALUES (1, 'Keep this course');
                INSERT INTO flashcard_sets VALUES (1, 1);
                INSERT INTO flashcards VALUES (1, 1);
                INSERT INTO flashcard_progress VALUES (1, 1);
            ''')

    def run_migration(self, apply=False):
        with contextlib.redirect_stdout(io.StringIO()):
            return migrate(self.url, apply)

    def tables(self, path=None):
        with sqlite3.connect(path or self.path) as db:
            return {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}

    def test_preview_does_not_change_database(self):
        before = self.path.read_bytes()
        self.assertEqual(self.run_migration(), dict.fromkeys(('flashcard_progress', 'flashcards', 'flashcard_sets'), 1))
        self.assertEqual(self.path.read_bytes(), before)

    def test_apply_preserves_courses_and_backs_up_all_tables(self):
        self.run_migration(apply=True)
        self.assertEqual(self.tables(), {'courses'})
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('SELECT * FROM courses').fetchall(), [(1, 'Keep this course')])
        backups = list(self.path.parent.glob('*.bak'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(len(self.tables(backups[0])), 4)
        self.run_migration(apply=True)
        self.assertEqual(self.tables(), {'courses'})

    def test_unrelated_dependency_blocks_removal(self):
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE other_feature (id INTEGER REFERENCES flashcards(id))')
        with self.assertRaisesRegex(ValueError, 'other_feature still references flashcards'):
            self.run_migration(apply=True)
        self.assertIn('flashcards', self.tables())

    def test_missing_database_is_not_created(self):
        path = self.path.parent / 'missing.db'
        with self.assertRaisesRegex(ValueError, 'must already exist'):
            migrate(f'sqlite:///{path}', apply=True)
        self.assertFalse(path.exists())


if __name__ == '__main__':
    unittest.main()
