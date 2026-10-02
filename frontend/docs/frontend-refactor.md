# Frontend refactor

Scope: Vue frontend only. Keep existing theme, fonts, spacing, API services,
request payloads, authentication, permissions, route names and route paths.

## Initial Vue inventory (44 files)

All paths below are relative to `frontend/src`.

| File | Purpose / overlap |
| --- | --- |
| App.vue | Application shell |
| components/Navbar.vue | Shared navigation |
| components/Footer.vue | Shared footer |
| components/DashboardHero.vue | Dashboard banner |
| components/AuthHeroSection.vue | Shared Login/Signup branding; already consolidated |
| components/QuestionEditor.vue | Active inline exam question editor |
| components/PasswordInput.vue | Unused |
| components/LearningLayout.vue | Unused layout; only consumer of old Sidebar |
| components/Sidebar.vue | Unreachable through unused LearningLayout |
| components/ExamQuestionEditor.vue | Unused alternative to QuestionEditor |
| components/exam/MultipleChoice.vue | Only used by unused ExamQuestionEditor |
| components/exam/TrueFalse.vue | Only used by unused ExamQuestionEditor |
| components/exam/ShortAnswer.vue | Only used by unused ExamQuestionEditor |
| views/Login.vue | Login; preserve authentication |
| views/Signup.vue | Signup; distinct from Login |
| views/LoginSuccess.vue | OAuth callback |
| views/VerifyEmail.vue | Email verification |
| views/UserSetting.vue | Profile settings |
| views/Dashboard.vue | Public/student dashboard |
| views/Teacher.vue | Teacher course dashboard |
| views/AdminPage.vue | Administration; distinct permissions |
| views/CourseDashboard.vue | Student course navigation |
| views/CourseEditor.vue | Teacher create/update course |
| views/ModulesList.vue | Student course module list |
| views/LearningDashboard.vue | Student module progress and lessons |
| views/LearningChapter.vue | Study page; duplicate lesson sidebar markup |
| views/LearningMiniquizPoint.vue | Module completion; duplicate lesson sidebar markup |
| views/TeacherLearningDashboard.vue | Teacher overview; distinct from module editing |
| views/LearningModule.vue | Teacher module creation and structure management |
| views/LearningEditor.vue | Teacher lesson content editor |
| views/FlashcardDashboard.vue | Student flashcard sets |
| views/TeacherFlashcardDashboard.vue | Teacher set management; distinct permissions/actions |
| views/FlashcardEditor.vue | Teacher card editing |
| views/FlashcardStudy.vue | Student study/review |
| views/ExamDashboard.vue | Student session list |
| views/ExamSet.vue | Student session information/start |
| views/TakeExam.vue | Student exam answering |
| views/ExamResult.vue | Score, topic breakdown and lesson suggestions |
| views/ExamAnalysis.vue | Duplicates result/topic data; adds wrong answers/explanations |
| views/ExamHistory.vue | Session attempt history; integrate with results |
| views/TeacherExamDashboard.vue | Teacher template/session management |
| views/ExamEditor.vue | Teacher inline template/questions |
| views/ExamLaunch.vue | Teacher scheduling and session launch; keep existing route |
| views/SessionExamResults.vue | Teacher results across students; distinct from student result |

## Work sequence

1. Remove unreachable Vue components; share lesson sidebar with original styles.
2. Render all student questions continuously with one submit button.
3. Combine score, analysis and session history while preserving legacy routes.
4. Simplify teacher forms and defaults without changing API payload contracts.

Each topic has its own commit. Only frontend files are staged.

## Validation

- Baseline production build: passed, no warnings.
- Shared sidebar: DOM and computed styles match the original at 1440px and
  390px on both study and module-completion pages.
- Continuous exam: all questions and one final submit button verified at
  1440px and 390px. Multiple choice, true/false, short answer and fill-in answers
  retain the existing submission payload. A failed submission retains answers
  and allows retry. Timer expiry sends exactly one submission.
- Verification intercepted exam POST requests; it did not modify server data.
- Combined results: score, topic breakdown, wrong answers, explanations,
  recommended lessons, best attempt and all attempt summaries render together.
  Existing result/analysis/history URLs still resolve without redirects or
  renamed routes. Route parameter changes reload the selected result.
- Result checks passed at 1440px and 390px, including history navigation,
  unreleased explanations, empty history and analysis API failure. Analysis
  failure preserves the score and does not show a false perfect-score message.

## Final changes by topic

1. **Shared components / cleanup**: remove the seven unreachable Vue components
   identified above. `LearningChapter` and `LearningMiniquizPoint` now use
   `LearningLessonSidebar`, including both original style variants.
2. **Student answering**: `TakeExam` renders every question on one page. The
   single submit button is at the bottom, beside the answer count and unanswered
   warning. Countdown and automatic submission remain. Failed submission keeps
   the timer and answers, and supports retry.
3. **Student results**: `ExamResult` includes `ExamQuestionReview` and
   `ExamAttemptHistory`. Remove the separate `ExamAnalysis.vue` and
   `ExamHistory.vue` views. Their route names and paths still render the combined
   result view. The selected result is fully expanded; older attempts retain a
   link to their complete result.
4. **Teacher forms**: `CourseEditor` creates/renames modules inline using the
   original learning APIs and one course save button. An empty first module row
   is ready when creating a course. `ExamEditor` has a visible Add Question action,
   current-year default, review/answer-release defaults for new exams, inline
   publication and optional session settings. One save can create/update the
   template and open a session. Existing exam settings are restored when editing.
   `ExamSessionFields` and `utils/examSession.js` are shared with the original
   `ExamLaunch` route. Fix correct-answer radio groups so each question has its
   own group. Saving a newly created template again updates it rather than
   creating another template.

## Files removed, shared and edited

- Removed unused files: `components/PasswordInput.vue`, `LearningLayout.vue`,
  `Sidebar.vue`, `ExamQuestionEditor.vue`, `exam/MultipleChoice.vue`,
  `exam/TrueFalse.vue`, `exam/ShortAnswer.vue`.
- Removed/replaced views: `views/ExamAnalysis.vue`, `views/ExamHistory.vue`
  (history presentation moved to `components/ExamAttemptHistory.vue`).
- Shared/new components: `LearningLessonSidebar.vue`, `ExamQuestionReview.vue`,
  `ExamAttemptHistory.vue`, `ExamSessionFields.vue`.
- Edited views: `LearningChapter.vue`, `LearningMiniquizPoint.vue`, `TakeExam.vue`,
  `ExamResult.vue`, `CourseEditor.vue`, `ExamEditor.vue`, `ExamLaunch.vue`.
- Other frontend files: `components/QuestionEditor.vue`, `router/index.js`,
  `utils/examSession.js`, this report.

## Teacher click counts

Counts start inside the editor and exclude typing/focusing text fields, scrolling
and the common dashboard entry click. Optional settings retain their controls.

| Task | Before | After |
| --- | --- | --- |
| Create a course and its first module | 3: Create Course → New Module → Create Module | 1: Create Course |
| Create a course without modules | 1 | 1 |
| Create, publish and open a new exam | 5: Publish → Save → Back → Launch Exam → Launch Session | 2: Open Session When Saving → Save & Open Session |
| Save a draft exam | 1 | 1 |
| Add another question | 1 | 1, with an additional visible action at the top and focus in the new question |

## Earlier verification / limits

- 39 Vue files remain; all are reachable through the application import graph.
  No broken local imports. Every existing route name and path is unchanged.
- Production build passes with no warnings. No new packages or UI library.
- Shared launch form computed styles match the original at 1440px and 390px.
- Teacher browser checks at both widths verify course/module saves, exam/session
  saves, current-year default, publication status on reload, independent answer
  radios and the original request keys. Partial failures retain successfully
  created IDs, so retry does not recreate courses/templates. After a successful
  session launch, ordinary saves do not launch another session.
- Browser write requests were intercepted for verification; server data was not
  changed. Local read/login requests used the existing localhost backend.
- Global CSS, fonts, dependencies, API services, stores and auth/permission
  guards are unchanged. No backend, database, server configuration or deployment
  files were edited or committed in this task.
- Explicit save is used instead of autosave. Opening a student session is opt-in;
  new exams remain drafts until the teacher chooses publication/session opening.
  Multi-resource saves use the separate existing API calls, not a transaction.
  If a later call fails, earlier successful resources stay saved and can be
  retried from the current form. No server change was needed.

## Latest task: continuous surfaces and consistent editors

The latest instructions retain the original design system and explicitly change
the exam surface/header, editor headers/layout and student course presentation.
The uncommitted general restyle from the preceding request was discarded. No
global palette, font, radius or shadow reset is included.

### Current Vue inventory (40 files)

Paths are relative to `frontend/src`. Each file is reachable through the
application import graph; no unresolved imports remain.

- Shell: `App.vue`.
- Components: `Navbar.vue`, `Footer.vue`, `DashboardHero.vue`,
  `AuthHeroSection.vue`, `QuestionEditor.vue`, `LearningLessonSidebar.vue`,
  `ExamSessionFields.vue`, `ExamQuestionReview.vue`, `ExamAttemptHistory.vue`,
  `EditorHeader.vue`.
- Views: `Login.vue`, `Signup.vue`, `LoginSuccess.vue`, `VerifyEmail.vue`,
  `UserSetting.vue`, `Dashboard.vue`, `Teacher.vue`, `AdminPage.vue`,
  `CourseDashboard.vue`, `CourseEditor.vue`, `ModulesList.vue`,
  `LearningDashboard.vue`, `LearningChapter.vue`, `LearningMiniquizPoint.vue`,
  `TeacherLearningDashboard.vue`, `LearningModule.vue`, `LearningEditor.vue`,
  `FlashcardDashboard.vue`, `TeacherFlashcardDashboard.vue`,
  `FlashcardEditor.vue`, `FlashcardStudy.vue`, `ExamDashboard.vue`, `ExamSet.vue`,
  `TakeExam.vue`, `ExamResult.vue`, `TeacherExamDashboard.vue`, `ExamEditor.vue`,
  `ExamLaunch.vue`, `SessionExamResults.vue`.

Overlap resolved: lesson sidebars, exam session fields, result/analysis/history
and editor headers. Student/teacher dashboards retain separate views because
their actions, data and permissions differ. `ExamSet` remains the first-attempt
information screen and an existing public route; Retake bypasses it.

### Changes and file report

| Section | Files / outcome |
| --- | --- |
| 1. Cleanup | Earlier removal: `components/PasswordInput.vue`, `LearningLayout.vue`, `Sidebar.vue`, `ExamQuestionEditor.vue`, `components/exam/MultipleChoice.vue`, `TrueFalse.vue`, `ShortAnswer.vue`; shared lesson sidebar in `LearningChapter.vue` and `LearningMiniquizPoint.vue`. No additional page deletion is needed for the shared editor header. |
| 2.1 Exam | `views/TakeExam.vue`: one white form surface, question sections with dividers, one Submit action; compact opaque sticky header below the existing navbar. Native answer controls remain keyboard accessible. Timer and submission payload unchanged. |
| 2.2 Retake | `views/ExamDashboard.vue`: Retake routes directly to `TakeExam`; first Start Exam keeps the existing information flow. Essential exam information/instructions appear in a compact panel within the answering surface using fields already returned by the API. |
| 2.3 Results | Earlier merge into `views/ExamResult.vue`, `components/ExamQuestionReview.vue`, `components/ExamAttemptHistory.vue`. Remove `views/ExamAnalysis.vue`; move `views/ExamHistory.vue` to the history component. `router/index.js` keeps all original names/paths. |
| 2.4 Course | `views/CourseDashboard.vue`: sidebar navigation, centered reading column, overview counts and study tools, following the supplied Postman Academy screenshot. Original loading/data script is retained exactly. |
| 3.1 Creation | Earlier changes in `CourseEditor.vue`, `ExamEditor.vue`, `QuestionEditor.vue`, `ExamLaunch.vue`, `ExamSessionFields.vue`, `utils/examSession.js`: inline modules/questions, defaults, single explicit save. Add section is also visible in the lesson header on mobile where the outline is hidden. |
| 3.2 / 3.5 Headers | New `components/EditorHeader.vue` and `composables/useNavbarOffset.js`. Shared header in `ExamEditor.vue`, `LearningEditor.vue`, `FlashcardEditor.vue`, `LearningModule.vue`, `CourseEditor.vue`; clickable breadcrumbs, title below, actions on the right, sticky below navbar. Style comes from the original FlashcardEditor header. |
| 3.3 Exam layout | `ExamEditor.vue`: wider main column and 280px behaviour panel. Below 1100px, behaviour moves into a two-column section; below 600px its controls stack. |
| 3.4 Lesson alignment | `LearningEditor.vue`: title, topic label/input and section name share one padded metadata container. Editor flex child has `min-width: 0`; its scrolling height accounts for navbar/header. |

Additional documentation: this file. No backend, API service, store,
authentication, permission, dependency, global style or server file changes.

### Teacher action counts

Counts exclude typing, scrolling and the common dashboard entry.

| Task | Original | Final |
| --- | --- | --- |
| Create course and first module | 3 | 1: Create Course |
| Save a course without modules | 1 | 1 |
| Create, publish and open an exam | 5 | 2: Open Session When Saving, then Save & Open Session |
| Save exam draft | 1 | 1 |
| Add question | 1 | 1, visible in the sticky header |
| Add lesson section | 1 on desktop | 1 on desktop and mobile |

### Latest verification and limitations

- Production build passes without errors or new warnings. Import audit passes
  for all 40 Vue files; route names/paths, guards, API services, stores,
  dependencies, App.vue and global styles match the original baseline.
- Desktop 1440px and mobile 390px: mixed exam answers, unchanged payload,
  retry after submission failure and exactly one timer-expiry submission pass.
- Actual local rendering: no question cards, persistent exam header/timer,
  direct Retake, course navigation, five sticky editor headers, all breadcrumb
  targets, wide settings and aligned lesson fields pass.
- Layout also passes at 1920 CSS px, the effective viewport of a 1440px display
  at 75% zoom. This is layout emulation, not a manual OS/browser zoom check.
- Results, legacy result URLs, history selection and partial API failures pass
  at both widths. Teacher course/module/exam/session payload and retry tests
  pass at both widths. Existing three-role local login checks pass.
- Browser rendering reads the local data. Write checks intercept requests;
  they do not create or change server records. Chrome resource limits during
  repeated full-page navigation were resolved by closing test pages between
  checks, without a production code change.
- Explicit Save is retained instead of adding autosave. Multi-resource saves
  continue to use the existing separate API calls and their retry behavior.
  No requested feature requires a backend or API contract change.
