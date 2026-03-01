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
    // LoginSuccess.vue calls authStore.handleSSOCallback() on mount
    path: '/login-success',
    name: 'LoginSuccess',
    component: () => import('@/views/LoginSuccess.vue'),
    meta: {
      showNavbar: false,
      showFooter: false,
      title: 'Logging in... - EasyEcon'
    }
  },

  /* =========== Dashboard =========== */
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      title: 'Elevate Your Economics Grade - EasyEcon'
    }
  }
];

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