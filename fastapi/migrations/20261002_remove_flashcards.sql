-- Run in a transaction after backing up the target database.
-- Child tables first; intentionally no CASCADE.
DROP TABLE IF EXISTS flashcard_progress;
DROP TABLE IF EXISTS flashcards;
DROP TABLE IF EXISTS flashcard_sets;
