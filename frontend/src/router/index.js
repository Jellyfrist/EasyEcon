import { createRouter, createWebHistory } from 'vue-router';
import { authService } from '@/services/authService';

/**
    Backend route mapping:

    AUTH (routers/auth.py)
        POST /auth/token                    -> /login (Login.vue)
        POST /auth/register                 -> /signup (Signup.vue)
        GET  /auth/login/google             -> loginWithGoogle() in authService
        GET  /auth/google/callback          -> backend redirects -> /login-success
        GET  /auth/login/github             -> loginWithGithub() in authService
        GET  /auth/github/callback          -> backend redirects -> /login-success
        GET  /auth/me                       -> /profile (Profile.vue)
        POST /auth/logout                   -> logout() in authService
        POST /auth/admin/teachers           -> /admin (Admin.vue)

    LEARNING (routers/learning.py)
        GET  /learning/modules              -> /learning (LearningDashboard.vue)
        GET  /learning/modules/:id/pages    -> /learning/module/:moduleId (LearningModule.vue)
        GET  /learning/pages/:id/study      -> /learning/page/:pageId (Learning.vue)
        POST /learning/pages/mini-quiz      -> inside Learning.vue (no separate route needed)
        GET  /learning/pages/:id/my-quiz    -> inside Learning.vue (no separate route needed)
        POST /learning/modules              -> /teacher (Teacher.vue)
        POST /learning/pages                -> /teacher/lesson-builder/:pageId?
        PATCH/DELETE /learning/pages/:id    -> /teacher/lesson-builder/:pageId

    FLASHCARD (routers/flashcard.py)
        GET  /flashcards/sets               -> /flashcards (FlashcardsDashboard.vue)
        GET  /flashcards/sets/:id/study     -> /flashcards/study/:setId (FlashcardStudy.vue)
        POST /flashcards/progress           -> inside FlashcardStudy.vue (no separate route)
        GET  /flashcards/sets/:id/progress  -> inside FlashcardStudy.vue (no separate route)
        POST /flashcards/sets               -> /flashcards/edit/:setId?
        PATCH/DELETE /flashcards/...        -> /flashcards/edit/:setId?

    EXAM (routers/exam.py)
        GET  /exam/sessions                 -> /exam (ExamDashboard.vue)
        GET  /exam/sessions/:id/open        -> /exam/:sessionId (ExamSession.vue)
        POST /exam/attempts                 -> /exam/take/:sessionId (ExamTake.vue)
        GET  /exam/attempts/:id             -> /exam/result/:attemptId (ExamResult.vue)
        GET  /exam/sessions/:id/my-attempts -> /exam/history/:sessionId (ExamHistory.vue)
        GET  weakness_report from attempt   -> /exam/analysis/:attemptId (ExamAnalysis.vue)
        POST /exam/templates                -> /teacher/exam/new
        PATCH/DELETE /exam/templates/:id    -> /teacher/exam/edit/:templateId
        POST /exam/sessions                 -> /teacher/exam/launch/:templateId
        GET  /exam/sessions/:id/results     -> /teacher/exam/results/:sessionId
**/

const routes = [

  /* =========== Initial page =========== */
  {
    path: '/',
    redirect: '/dashboard'
  },

  /* =========== Auth =========== */
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { 
      showNavbar: false,
      showFooter: false,
      guest: true,
      title: 'Log in - EasyEcon'
    }
  },
  {
    path: '/signup',
    name: 'Signup',
    component: () => import('@/views/Signup.vue'),
    meta: { 
      showNavbar: false,
      showFooter: false,
      guest: true,
      title: 'Sign up - EasyEcon'
    }
  },
  {
    // Google/GitHub SSO lands here with ?csrf_token=xxx
    // LoginSuccess.vue calls authStore.handleSSOCallback() on mount.
    path: '/login-success',
    name: 'LoginSuccess',
    component: () => import('@/views/LoginSuccess.vue'),
    meta: { 
      showNavbar: false,
      showFooter: false,
      requiresAuth: true,
      title: 'Login Successfully'
    }
  },

  /* =========== Dashboard (Initial page for each role) ===========*/

  // Student
  // main student page: course lists and learning features.
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      title: 'Elevate Your Economics Grade - EasyEcon'
    }
  },
  // Teacher
  // main teacher page: lists modules, flashcard sets, exam templates.
  {
    path: '/teacher',
    name: 'Teacher',
    component: () => import('@/views/Teacher.vue'),
    meta: { 
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Teacher Dashboard - EasyEcon'
    }
  },
  // Admin
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: {
      showNavbar: false,
      showFooter: false,
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Admin - EasyEcon'
    }
  },

  /* =========== User Information (Profile) =========== */
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'My Profile - EasyEcon'
    }
  },

  /* =========== Feature =========== */

  /* ---- Learning by lesson ---- */

  // student - dashboard: list all modules.
  // API: GET /learning/modules?course_id=
  {
    path: '/learning',
    name: 'LearningDashboard',
    component: () => import('@/views/LearningDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      showDashboardHero: true,
      requiresAuth: true,
      title: 'Learning Dashboard - EasyEcon'
    }
  },
  // student - dashboard - learnig module: list published pages inside a module.
  // API: GET /learning/modules/:moduleId/pages
  {
   path: '/learning/module/:moduleId',
    name: 'LearningModule',
    component: () => import('@/views/LearningModule.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true, 
      title: 'Learning Module - EasyEcon' 
    }
  },

  // student - dashboard - learnig module - learning page: read a lesson page + submit mini quiz inside.
  // API: GET  /learning/pages/:pageId/study
  //      POST /learning/pages/mini-quiz       <- called inside this view
  //      GET  /learning/pages/:pageId/my-quiz <- called inside this view
  {
    path: '/learning/page/:pageId',
    name: 'LearningPage',
    component: () => import('@/views/Learning.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Learning - EasyEcon'
    }
  },

  // teacher - dashboard
  /* path: '/teacher' */

  // teacher - dashboard - lesson builder: create or edit a lesson page.
  // API: POST  /learning/pages        (no pageId = create)
  //      PATCH /learning/pages/:id    (with pageId = edit)
  {
    path: '/teacher/lesson-builder/:pageId?',
    name: 'TeacherLessonEditor',
    component: () => import('@/views/TeacherLessonEditor.vue'),
    meta: { 
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Lesson Builder - EasyEcon' 
    }
  },

  /* ---- Flashcard ---- */

  // student - dashboard: list all flashcard sets for a course.
  // API: GET /flashcards/sets?course_id=
  {
    path: '/flashcards',
    name: 'FlashcardsDashboard',
    component: () => import('@/views/FlashcardsDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      showDashboardHero: true,
      requiresAuth: true,
      title: 'Flashcards Dashboard - EasyEcon'
    }
  },

  // student - flashcard page: study a flashcard set.
  // API: GET  /flashcards/sets/:setId/study
  //      POST /flashcards/progress              <- called inside this view
  //      GET  /flashcards/sets/:setId/progress  <- called inside this view
  {
    path: '/flashcards/study/:setId',
    name: 'FlashcardStudy',
    component: () => import('@/views/FlashcardStudy.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Flashcards - EasyEcon'
    }
  },

  // teacher - flashcard editer: create or edit a flashcard set and its cards.
  // API: POST   /flashcards/sets            (no setId = create)
  //      PATCH  /flashcards/sets/:setId     (with setId = edit)
  //      POST   /flashcards/sets/:setId/cards
  //      PATCH  /flashcards/cards/:cardId
  //      DELETE /flashcards/cards/:cardId
  {
    path: '/flashcards/edit/:setId?',
    name: 'FlashcardEditor',
    component: () => import('@/views/FlashcardEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Edit Flashcards - EasyEcon'
    }
  },

  /* ---- Practice Exam ---- */

  // student - dashboard: list all open exam sessions for a course.
  // API: GET /exam/sessions?course_id=
  {
    path: '/exam',
    name: 'ExamDashboard',
    component: () => import('@/views/ExamDashboard.vue'),
    meta: { 
      showNavbar: true,
      showFooter: true,
      showDashboardHero: true,
      requiresAuth: true,
      title: 'Exam Dashboard - EasyEcon'
    }
  },

  // student - dashboard - session: see questions with answers stripped.
  // API: GET /exam/sessions/:sessionId/open
  {
    path: '/exam/session/:sessionId',
    name: 'ExamSession',
    component: () => import('@/views/ExamSets.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Exam Sets - EasyEcon'
    }
  },

  // student - dashboard - session - exam: answer and submit the exam.
  // API: POST /exam/attempts
  {
    path: '/exam/take/:sessionId',
    name: 'ExamTake',
    component: () => import('@/views/TestExam.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Take Exam - EasyEcon'
    }
  },

  // student - dashboard - session - exam - result: view graded result + weakness report
  // API: GET /exam/attempts/:attemptId
  {
    path: '/exam/result/:attemptId',
    name: 'ExamResult',
    component: () => import('@/views/ExamResult.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Exam Result - EasyEcon'
    }
  },

  // student - dashboard - session - exam - result - analysis : weakness analysis with suggested learning pages.
  // API: GET /exam/attempts/:attemptId  (reads weakness_report field)
  {
    path: '/exam/analysis/:attemptId',
    name: 'ExamAnalysis',
    component: () => import('@/views/ExamAnalysis.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Performance Analysis - EasyEcon'
    }
  },

  // student - history: list all my past attempts for a session.
  // API: GET /exam/sessions/:sessionId/my-attempts
  {
    path: '/exam/history/:sessionId',
    name: 'ExamHistory',
    component: () => import('@/views/ExamHistory.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Exam History - EasyEcon'
    }
  },

  // teacher - dashboard
  /* same as path: '/teacher' */

  // teacher - dashboard - create exam sets: create a new exam template.
  // API: POST /exam/templates
  {
    path: '/teacher/exam/new',
    name: 'TeacherExamNew',
    component: () => import('@/views/TeacherExamEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Create Exam - EasyEcon'
    }
  },

  // teacher - dashboard - exam sets editor: edit existing exam template.
  // API: GET   /exam/templates/:templateId
  //      PATCH /exam/templates/:templateId
  {
    path: '/teacher/exam/edit/:templateId',
    name: 'TeacherExamEdit',
    component: () => import('@/views/TeacherExamEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Edit Exam - EasyEcon'
    }
  },

  // teacher - dashboard - session: launch a session from a template.
  // API: POST /exam/sessions
  {
    path: '/teacher/exam/launch/:templateId',
    name: 'TeacherExamLaunch',
    component: () => import('@/views/TeacherExamEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Launch Exam - EasyEcon'
    }
  },

  // teacher - dashboard - session - overviews: view all student results for a session.
  // API: GET /exam/sessions/:sessionId/results
  {
    path: '/teacher/exam/results/:sessionId',
    name: 'TeacherExamResults',
    component: () => import('@/views/TeacherExamResults.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Exam Results - EasyEcon'
    }
  },

  /* ============ Error Page =========== */
  {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue')
  }
];

// register all routes, and reset scroll position to top ( or restore saved position when navigating back/forward)
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 };
  }
});

// Navigation Guards

router.beforeEach((to, from, next) => {
  const requiresAuth    = to.matched.some((r) => r.meta.requiresAuth);
  const requiresTeacher = to.matched.some((r) => r.meta.requiresTeacher);
  const requiresAdmin   = to.matched.some((r) => r.meta.requiresAdmin);
  const guest           = to.matched.some((r) => r.meta.guest);

  const isAuthenticated = authService.isAuthenticated();
  const user = authService.getUser();

  // update page title
  if (to.meta.title) {
    document.title = to.meta.title;
  }

  // already logged in -> skip guest pages
  if (guest && isAuthenticated) {
    return next({ name: 'Dashboard' });
  }

  // not logged in -> go to login
  if (requiresAuth && !isAuthenticated) {
    return next({ name: 'Login' });
  }

  // admin only
  if (requiresAdmin) {
    if (user?.role !== 'admin') {
      alert("Insufficient permission: Admin access only");
      return next({ name: 'Dashboard' });
    }
    return next();
  }

  // teacher or admin
  if (requiresTeacher) {
    if (!user || !['teacher', 'admin'].includes(user.role)) {
      alert("Access Denied: Teacher account required");
      return next({ name: 'Dashboard' });
    }
    return next();
  }

  next();
});

export default router;