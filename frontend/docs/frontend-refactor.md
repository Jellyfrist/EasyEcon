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
