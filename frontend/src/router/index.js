import { createRouter, createWebHistory } from 'vue-router';
import { authService } from '@/services/authService';


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
    path: '/verify-email',
    name: 'VerifyEmail',
    component: () => import('@/views/VerifyEmail.vue'),
    meta: { title: 'กำลังยืนยันอีเมล... - EasyEcon' }
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
      guest: true, // Allow unauthenticated access for SSO callback
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
      requiresAuth: false,
      requiresTeacher: true,
      title: 'Teacher Dashboard - EasyEcon'
    }
  },
  // Admin
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/AdminPage.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Admin - EasyEcon'
    }
  },

  /* ---- Course ---- */
  // student
  {
    path: '/courses/:courseId',
    name: 'Courses',
    component: () => import('@/views/CourseDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Cours - EasyEcon'
    }
  },
  
  // teacher
  {
    path: '/teacher/courses/create',
    name: 'CreateCourses',
    component: () => import('@/views/CourseEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Create Course - EasyEcon'
    }
  },
  {
    path: '/teacher/courses/:courseId/edit',
    name: 'CoursesEditor',
    component: () => import('@/views/CourseEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Edit Course - EasyEcon'
    }
  },

  /* ---- Flashcard ---- */

  // teacher/admin: manage flashcard sets for a course (edit, delete, create)
  {
    path: '/teacher/flashcards/:courseId',
    name: 'TeacherFlashcardDashboard',
    component: () => import('@/views/TeacherFlashcardDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Manage Flashcards - EasyEcon'
    }
  },

  // student: browse and study flashcard sets for a course
  {
    path: '/flashcards/:courseId',
    name: 'FlashcardsDashboard',
    component: () => import('@/views/FlashcardDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      showDashboardHero: true,
      requiresAuth: true,
      title: 'Flashcards Dashboard - EasyEcon'
    }
  },

  // student - flashcard study: study a flashcard set.
  // courseId kept in the url so the back button can return to the right dashboard.
  // API: GET  /flashcards/sets/:setId/study
  //      POST /flashcards/progress              <- called inside this view
  //      GET  /flashcards/sets/:setId/progress  <- called inside this view
  {
    path: '/flashcards/:courseId/study/:setId',
    name: 'FlashcardStudy',
    component: () => import('@/views/FlashcardStudy.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Flashcards - EasyEcon'
    }
  },

  // teacher - flashcard editor: create or edit a flashcard set and its cards.
  // courseId is required (no ?) so POST /flashcards/sets always has course_id.
  // setId is optional: no setId = create mode, with setId = edit mode.
  // API: POST   /flashcards/sets                <- create mode
  //      PATCH  /flashcards/sets/:setId         <- edit mode
  //      POST   /flashcards/sets/:setId/cards
  //      PATCH  /flashcards/cards/:cardId
  //      DELETE /flashcards/cards/:cardId
  {
    path: '/flashcards/:courseId/edit/:setId?',
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

  /* ---- Learn ---- */

  // teacher
  {
    path: '/teacher/learning/:courseId',
    name: 'TeacherLearningDashboard',
    component: () => import('@/views/TeacherLearningDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Manage Learn - EasyEcon'
    }
  },
  // teacher - flashcard editor: create or edit a flashcard set and its cards.
  // courseId is required (no ?) so POST /flashcards/sets always has course_id.
  // setId is optional: no setId = create mode, with setId = edit mode.
  // API: POST   /flashcards/sets                <- create mode
  //      PATCH  /flashcards/sets/:setId         <- edit mode
  //      POST   /flashcards/sets/:setId/cards
  //      PATCH  /flashcards/cards/:cardId
  //      DELETE /flashcards/cards/:cardId
  {
    path: '/learning/:courseId/:moduleId/edit/:pageId?',
    name: 'LearningEditor',
    component: () => import('@/views/LearningEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Edit Learning - EasyEcon'
    }
  },
  {
    path: '/teacher/modules/:courseId',
    name: 'LearningModule',
    component: () => import('@/views/LearningModule.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Learning Module - EasyEcon'
    }
  },

  // student: browse and study flashcard sets for a course
  {
    path: '/courses/:courseId/modules',
    name: 'ModulesList',
    component: () => import('@/views/ModulesList.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Course Modules - EasyEcon'
    }
  },
  {
    path: '/courses/:courseId/studydashboard/:moduleId', 
    name: 'LearningDashboard',
    component: () => import('@/views/LearningDashboard.vue'),
    meta: {
      requiresAuth: true,
      title: 'Learning Dashboard - EasyEcon'
    }
  },
  {
    path: '/courses/:courseId/study/lesson/:moduleId/:pageId',
    name: 'LearningChapter',
    component: () => import('@/views/LearningChapter.vue'),
    meta: {
      requiresAuth: true,
      title: 'Learning Chapter - EasyEcon'
    }
  },
  {
    path: '/student/courses/:courseId/modules/:moduleId/summary',
    name: 'LearningMiniquizPoint', // คุณสามารถใช้ชื่อเดิม หรือเปลี่ยนเป็น 'ModuleSummary' ก็ได้ครับ
    component: () => import('@/views/LearningMiniquizPoint.vue'), // ชี้ไปที่ไฟล์หน้าสรุปผลที่คุณสร้างไว้
    meta: {
      requiresAuth: true,
      title: 'Complete Learning - EasyEcon'
    }
  },
  // {
  //   path: '/courses/:courseId/study',
  //   component: () => import('@/components/LearningLayout.vue'),
  //   children: [
      
  //     {
  //       path: 'lesson/:moduleId/:pageId',
  //       name: 'LearningChapter',
  //       component: () => import('@/views/LearningChapter.vue'),
  //       meta: {
  //         requiresAuth: true,
  //         title: 'Learning Chapter - EasyEcon'
  //       }
  //     },
  //     {
  //       path: 'complete/learn/:moduleId/:pageId',
  //       name: 'LearningMiniquizPoint',
  //       component: () => import('@/views/LearningMiniquizPoint.vue'),
  //       meta: {
  //         requiresAuth: true,
  //         title: 'Complete Learning - EasyEcon'
  //       }
  //     }
  //   ]
  // },
  /* ---- Practice Exam ---- */

  // student: browse all exam sets for a course. (see all exam session)
  // API: GET /exam/sessions?course_id=
  {
    path: '/exam/:courseId',
    name: 'ExamDashboard',
    component: () => import('@/views/ExamDashboard.vue'),
    meta: { 
      showNavbar: true,
      showFooter: true,
      showDashboardHero: false,
      requiresAuth: true,
      title: 'Exam Dashboard - EasyEcon'
    }
  },

  // student - session: see exam template for session. (Get raedy for the exam)
  // API: GET /exam/sessions/:sessionId
  {
    path: '/exam/session/:sessionId',
    name: 'ExamSession',
    component: () => import('@/views/ExamSet.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Exam Sets - EasyEcon'
    }
  },

  // student - session - exam: answer and submit the exam. (Take the exam)
  // API: POST /exam/attempts
  {
    path: '/exam/take/:sessionId',
    name: 'TakeExam',
    component: () => import('@/views/TakeExam.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Take Exam - EasyEcon'
    }
  },

  // student - session - exam - result: view graded result.
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

  /*
    POST /exam/templates                -> /teacher/exam/new
          PATCH/DELETE /exam/templates/:id    -> /teacher/exam/edit/:templateId
          POST /exam/sessions                 -> /teacher/exam/launch/:templateId
          GET  /exam/sessions/:id/results     -> /teacher/exam/results/:sessionId
  */

  // teacher/admin: manage exam sets for a course (edit, delete, create)
  {
    path: '/teacher/exam/:courseId',
    name: 'TeacherExamDashboard',
    component: () => import('@/views/TeacherExamDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: false,
      requiresTeacher: false,
      title: 'Manage Exam - EasyEcon'
    }
  },

  // teacher - course - exam editor: create or edit a exam template.
  {
    // path: '/flashcards/:courseId/edit/:setId?',
    path: '/teacher/exam/:courseId/edit/:templateId?',
    name: 'ExamEditor',
    component: () => import('@/views/ExamEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: false,
      requiresTeacher: false,
      title: 'Edit Exam - EasyEcon'
    }
  },

  // teacher - dashboard - session: launches ExamSession  (snapshot frozen at launch)
  // API: POST /exam/sessions
  {
    path: '/teacher/exam/launch/:templateId',
    name: 'TeacherExamLaunch',
    component: () => import('@/views/ExamLaunch.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: false,
      requiresTeacher: false,
      title: 'Launch Exam - EasyEcon'
    }
  },

  // teacher - dashboard - session - overviews: view all student results for a session.
  // API: GET /exam/sessions/:sessionId/results
  {
    path: '/teacher/exam/results/:sessionId',
    name: 'TeacherExamResults',
    component: () => import('@/views/SessionExamResults.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: false,
      requiresTeacher: false,
      title: 'Exam Results - EasyEcon'
    }
  },

  /* =========== User Setting =========== */
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/UserSetting.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: false,
      title: 'User Settings - EasyEcon'
    }
  },

  /* ============ Error Page =========== */
  // {
  //     path: '/:pathMatch(.*)*',
  //     name: 'NotFound',
  //     component: () => import('@/views/NotFound.vue')
  // }
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
  const requiresAuth = to.matched.some((r) => r.meta.requiresAuth);
  const requiresTeacher = to.matched.some((r) => r.meta.requiresTeacher);
  const requiresAdmin = to.matched.some((r) => r.meta.requiresAdmin);
  const guest = to.matched.some((r) => r.meta.guest);

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