# Remove Flashcards

Branch: `refactor/remove-flashcards`. This change removes the feature rather than
merging it into lessons. Courses, modules/lessons, exams, authentication and
permissions retain their existing behavior and visual identity.

## Removed

- Student: `FlashcardDashboard.vue`, `FlashcardStudy.vue` and their routes.
- Teacher: `TeacherFlashcardDashboard.vue`, `FlashcardEditor.vue` and their routes.
- `flashcardService.js`, `flashcardStore.js`, `useFlashcardEditor.js`, preview image,
  and feature-specific global CSS.
- Backend Flashcard router, schemas, models and Course/User relationships.
- Flashcard menu items, promotional section, course counts and search results.
- Database tables: `flashcard_progress`, `flashcards`, `flashcard_sets`.

Vue files decrease from 40 to 36. This removes two student and two teacher pages;
it does not claim that the remaining UI has already been consolidated to 12 pages.
Course/exam creation click counts are unchanged by this feature removal.

## Exam image uploads

The exam editor previously uploaded images through the Flashcard API. It now uses
`POST /media/upload-image` with the same multipart file and `{ "url": ... }`
response, file types and teacher permission. The old Flashcard API is removed.
The existing `flashcard-images` storage bucket remains because exam images also
live there. Existing image URLs remain valid; no storage files were deleted.
`SUPABASE_MEDIA_BUCKET` can select a different bucket when configured separately.

## Database migration

Removing ORM models does not delete tables from an existing database. The explicit
migration is `fastapi/migrations/20261002_remove_flashcards.sql`.
The runner never loads `.env`; a target URL must be supplied explicitly.

Preview from the repository root:

```bash
python3 fastapi/scripts/remove_flashcards.py --database-url sqlite:///fastapi/local-no-flashcards.db
```

Apply to the reviewed local target:

```bash
python3 fastapi/scripts/remove_flashcards.py --database-url sqlite:///fastapi/local-no-flashcards.db --apply
```

SQLite receives a timestamped backup before deletion. The migration checks for
references from unrelated tables, deletes children first without CASCADE and
supports repeat execution. PostgreSQL SQL/runner support is provided; back up the
target database first and stop writes while migrating. PostgreSQL migration has
not been executed or integration-tested against a live server.

For this branch, `fastapi/local-test.db` was copied to
`fastapi/local-no-flashcards.db` and only the copy was migrated. The current
localhost backend on port 8002 uses the copy; Vite on port 8081 proxies to it.
The original database and remote/deployed databases were not migrated.
Database files and migration backups are ignored by Git. To restore locally,
stop the backend, restore the backup and switch to code that supports Flashcards.

The existing local course seed script was adapted to populate lessons and exams
without Flashcards, using the branch-specific local database.

## Validation

- Production frontend build passes without new warnings.
- All 36 Vue files are reachable; no imports point to deleted files.
- Remaining route names, paths and authentication guards are unchanged.
- SQLite migration preserves every row in the 10 unrelated application tables;
  foreign-key checks pass. Fresh ORM schema contains no Flashcard tables.
- Four migration tests cover preview, backup/preservation/repeat execution,
  unexpected dependencies and missing database protection.
- Existing two exam grading tests pass.
- Backend checks cover course counts, student/teacher search and protected exam
  image uploads, including invalid file types.
- Actual localhost login works for student, teacher and admin. Continuous exam
  answers, submission retry and countdown auto-submit still pass at desktop and
  mobile widths.

The existing Navbar can overflow at mobile width with a long username/email;
its search input is hidden below 768px by the existing CSS. These unrelated
responsive behaviors were preserved rather than redesigned in this branch.
