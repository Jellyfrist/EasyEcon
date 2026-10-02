# Student module reader

The lesson reader follows the supplied Postman Academy screenshot: a flat white
outline on the left, centered article content, a pink active lesson row, and a
Previous / Next bar pinned at the bottom. Existing brand colors, fonts, quizzes
and progress APIs remain in use. On mobile, the Lessons button opens the outline.

`LearningLessonSidebar.vue` adds a reader variant; the completion screen retains
its existing sidebar presentation. `LearningChapter.vue` renders the reader.
`ModulesList.vue` opens the first published lesson directly.

The redundant `LearningDashboard.vue` is deleted. Its existing route name and
module URL remain available and use the same reader, opening the first unlocked
lesson automatically. Empty modules show an empty state with a return link.
The reader omits the marketing footer to fit below the existing Navbar.

Starting a lesson from the module list takes one click instead of two.
Teacher creation workflows are unchanged by this section.

Verified with a production build, import/route audit and browser checks at 1440px
and 390px: direct entry and old links, outline selection state, fixed navigation,
Previous / Next, actual progress saving, quiz submission payload and score display,
and empty modules. Backend, API services, authentication and permission guards
were not changed.
