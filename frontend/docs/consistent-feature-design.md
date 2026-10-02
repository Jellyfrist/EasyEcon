# Consistent feature UI

Branch: `refactor/remove-flashcards`.

## Later course overview preference

The course overview was subsequently restored to the user's original screenshot:
pink gradient hero, separate total cards and full-width green Modules / orange
Exams banners on the original page background. Flashcards remain removed, so
there are two totals and two study tools. Other feature pages keep their shared
layout/navigation. The course data loading and API remain unchanged.

## Direct exam start

Start Exam and Retake show a confirmation popup explaining that the timer
starts on confirmation. Cancel/Escape stay on the list without opening the exam;
confirmation enters TakeExam directly. `ExamSet.vue` is removed. The existing ExamSession route name and `/exam/session/:sessionId`
URL redirect to TakeExam with the query preserved. Exam and result Back links
return to the exam list (Dashboard fallback for old result links without course
context). Submission carries the course query to the result page. The existing
exam information/instructions remain on the answering surface; timer and payload
logic are unchanged. One additional student page is removed.

## Shared presentation and navigation

`FeaturePage.vue` owns the white surface, 1120px content width, gutters, card
surfaces and primary actions. `EditorHeader.vue` owns breadcrumbs, title, Back
and sticky actions below the existing Navbar. Reader pages retain their outline
and centered reading column. `FeatureToolbar.vue` shares exam search/filter
presentation between student and teacher. `CourseNavigation.vue` shares the
Course Overview / Modules / Exams outline and feature totals across all three
student pages.

The original Dashboard, Login, Signup and Teacher My Courses remain unchanged.
The Navbar hides the username/email text on small screens to prevent overflow;
its existing outside-click directive is registered to restore search closing
and remove its unresolved-directive warning.

## Files merged, removed and changed

- Removed `views/TeacherLearningDashboard.vue`: the duplicate module overview
  now uses `LearningModule.vue`. Both existing route names/URLs remain valid;
  guards and permissions are unchanged.
- Added `components/FeaturePage.vue`, `CourseNavigation.vue`,
  `FeatureToolbar.vue`; updated `EditorHeader.vue`, `Navbar.vue`, `style.css`.
- Student views: `CourseDashboard.vue`, `ModulesList.vue`, `ExamDashboard.vue`,
  `ExamSet.vue`, `TakeExam.vue`, `ExamResult.vue`, `LearningChapter.vue`,
  `LearningMiniquizPoint.vue`.
- Teacher views: `CourseEditor.vue`, `LearningModule.vue`, `LearningEditor.vue`,
  `TeacherExamDashboard.vue`, `ExamEditor.vue`, `ExamLaunch.vue`,
  `SessionExamResults.vue`.
- Admin: `AdminPage.vue` uses the same shell/header; removed the unresolved
  inner Footer instance. Admin operations and permission logic are unchanged.
- Updated `router/index.js` to reuse the module manager for the legacy route.

Student exams retain one continuous form, one Submit action, timer/progress in
the sticky header and direct Retake. Combined result/history/review behavior
is retained. The lesson reader keeps the supplied Postman arrangement.

Teacher breadcrumbs consistently use My Courses / Manage Course / Modules or
Exams / Editor. Back links follow that hierarchy instead of browser history.
New Lesson is visible on each module row, without expanding Manage Lessons.
The lesson editor retains its padded metadata container and sticky actions;
exam settings retain the wider main column and compact 280px behaviour column.

## Click counts

Counts exclude typing, scrolling and entering the relevant editor.

| Task | Before this consistency change | After |
| --- | --- | --- |
| Course and first inline module save | 1 | 1 |
| Create/publish/open exam | 2 | 2 |
| Open module manager from Manage Course | 2 | 1 |
| New Lesson from module manager | 2 | 1 |
| New Lesson from Manage Course, using management path | 4 | 2 |

The old duplicate overview also offered a direct Add Lesson shortcut taking
2 clicks from Manage Course; that shortest path remains 2 clicks. The gain is
removing the extra overview and making creation visible in the manager.
Earlier inline-workflow changes reduced course/module creation from 3 saves to
1, and exam publication/opening from 5 actions to 2; see
`frontend/docs/frontend-refactor.md`. This change does not claim additional
reductions for those already simplified flows.

## Verification and limits

- Production build passes without errors or warnings.
- Import/reachability audit: 37 Vue files, all reachable, no deleted-file imports
  or Flashcard references. Existing route names/paths and guards are preserved.
- Actual local role login and all 15 feature route cases at 1440px and 390px:
  shared header/background/typography, primary buttons, breadcrumb targets,
  course totals, no horizontal overflow, no Vue warnings or page errors.
- Actual Course / Modules / Exams navigation retains totals and active state.
  Teacher New Lesson and Back traverse the intended hierarchy.
- Exam settings/sticky header pass at 1920 CSS px, equivalent layout width to
  a 1440px viewport at 75% zoom; manual browser zoom is not claimed.
- Continuous exam tests, submission retry/countdown, combined results and
  legacy URLs, inline teacher payload/retry tests, and Postman lesson navigation/
  progress/quiz checks passed after shared-layout integration at both widths.
  Submission tests intercept writes; navigation checks use local data.
- No backend, API service, payload, database, authentication, permission or
  dependency changes in this section. No new UI library or autosave.
- This removes one redundant page; it does not claim the entire app is already
  at 12 pages. Auth/account and original dashboards remain separate.
