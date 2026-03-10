import { createRouter, createWebHistory } from 'vue-router';
import { authService } from '../services/authService';

const routes = [

  /* =========== initial page =========== */
  {
    path: '/',
    redirect: () => {
      const user = authService.getUser()
      if (['teacher', 'admin'].includes(user?.role)) return '/teacher'
      return '/dashboard'
    }
  },

  /* =========== auth =========== */
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      showNavbar: false,
      showFooter: false,
      guest: true,
      title: 'Log in'
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
      title: 'Sign up'
    }
  },
  {
    path: '/verify-email',
    name: 'VerifyEmail',
    component: () => import('@/views/VerifyEmail.vue'),
    meta: { title: 'Verify Email' }
  },
  {
    path: '/login-success',
    name: 'LoginSuccess',
    component: () => import('@/views/LoginSuccess.vue'),
    meta: {
      showNavbar: false,
      showFooter: false,
      guest: true,
      title: 'Login Successfully'
    }
  },

  /* =========== dashboards =========== */
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      title: 'Dashboard'
    }
  },
  {
    path: '/teacher',
    name: 'Teacher',
    component: () => import('@/views/Teacher.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Teacher Dashboard'
    }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresAdmin: true,
      title: 'Admin Page'
    }
  },

  /* =========== course =========== */
  {
    path: '/courses/:courseId',
    name: 'Courses',
    component: () => import('@/views/CourseDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Course'
    }
  },
  {
    path: '/teacher/courses/create',
    name: 'CreateCourses',
    component: () => import('@/views/CourseEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Create Course'
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
      title: 'Edit Course'
    }
  },

  /* =========== flashcard =========== */

  // teacher: manage sets for a course
  {
    path: '/teacher/flashcards/:courseId',
    name: 'TeacherFlashcardDashboard',
    component: () => import('@/views/TeacherFlashcardDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Manage Flashcards'
    }
  },

  // student: browse sets for a course
  {
    path: '/flashcards/:courseId',
    name: 'FlashcardsDashboard',
    component: () => import('@/views/FlashcardDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Flashcards'
    }
  },

  // student: study a set
  {
    path: '/flashcards/:courseId/study/:setId',
    name: 'FlashcardStudy',
    component: () => import('@/views/FlashcardStudy.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Flashcards'
    }
  },

  // teacher: create or edit a set
  {
    path: '/flashcards/:courseId/edit/:setId?',
    name: 'FlashcardEditor',
    component: () => import('@/views/FlashcardEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Edit Flashcards'
    }
  },

  /* ---- Practice Past Exam ---- */

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
      title: 'Exam Dashboard'
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
      title: 'Exam Sets'
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
      title: 'Take Exam'
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
      title: 'Exam Result'
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
      title: 'Performance Analysis'
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
      title: 'Exam History'
    }
  },

  /*
    POST /exam/templates                      -> /teacher/exam/new
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
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Manage Exam'
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
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Edit Exam'
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
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Launch Exam'
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
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Exam Results'
    }
  },

  /* =========== settings =========== */
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/UserSetting.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'User Settings'
    }
  },

  /* =========== learning (teacher) =========== */

  // teacher: overview of all modules + pages for a course
  {
    path: '/teacher/learning/:courseId',
    name: 'TeacherLearningDashboard',
    component: () => import('@/views/TeacherLearningDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Learning Lessons'
    }
  },

  // teacher: manage module structure (create/delete modules and pages)
  {
    path: '/teacher/modules/:courseId',
    name: 'LearningModule',
    component: () => import('@/views/LearningModule.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Manage Modules'
    }
  },

  // teacher: create or edit a learning page (rich text editor)
  {
    path: '/learning/:courseId/:moduleId/edit/:pageId?',
    name: 'LearningEditor',
    component: () => import('@/views/LearningEditor.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      requiresTeacher: true,
      title: 'Lesson Editor'
    }
  },

  /* =========== learning (student) =========== */

  // student: list all modules for a course
  {
    path: '/courses/:courseId/modules',
    name: 'ModulesList',
    component: () => import('@/views/ModulesList.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Learning Modules'
    }
  },

  // student: module dashboard — lesson list + progress for one module
  {
    path: '/courses/:courseId/modules/:moduleId',
    name: 'LearningDashboard',
    component: () => import('@/views/LearningDashboard.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Module Dashboard'
    }
  },

  // student: study a single learning page inside a module
  {
    path: '/courses/:courseId/modules/:moduleId/pages/:pageId',
    name: 'LearningChapter',
    component: () => import('@/views/LearningChapter.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Learning Chapter'
    }
  },

  {
    path: '/student/courses/:courseId/modules/:moduleId',
    name: 'LearningMiniquizPoint',
    component: () => import('@/views/LearningMiniquizPoint.vue'),
    meta: {
      showNavbar: true,
      showFooter: true,
      requiresAuth: true,
      title: 'Complete Learning - EasyEcon'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)
  const requiresTeacher = to.matched.some((r) => r.meta.requiresTeacher)
  const requiresAdmin = to.matched.some((r) => r.meta.requiresAdmin)
  const guest = to.matched.some((r) => r.meta.guest)

  const isAuthenticated = authService.isAuthenticated()
  const user = authService.getUser()
  const isTeacher = ['teacher', 'admin'].includes(user?.role)

  // update page title
  if (to.meta.title) document.title = to.meta.title

  // already logged in -> skip guest pages, redirect based on role
  if (guest && isAuthenticated) {
    return next({ name: isTeacher ? 'Teacher' : 'Dashboard' })
  }

  // not logged in -> go to login
  if (requiresAuth && !isAuthenticated) {
    return next({ name: 'Login' })
  }

  // admin only
  if (requiresAdmin) {
    if (user?.role !== 'admin') {
      alert('Insufficient permission: Admin access only')
      return next({ name: isTeacher ? 'Teacher' : 'Dashboard' })
    }
    return next()
  }

  // teacher or admin
  if (requiresTeacher) {
    if (!isTeacher) {
      alert('Access Denied: Teacher account required')
      return next({ name: 'Dashboard' })
    }
    return next()
  }

  next()
})

export default router