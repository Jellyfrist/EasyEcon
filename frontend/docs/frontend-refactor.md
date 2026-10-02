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

## Final verification / limits

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
