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
      showNavbar: false,
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

  // teacher/admin: manage flashcard sets for a course (edit, delete, create)
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

  // student: browse and study flashcard sets for a course
  {
    path: '/course/:moduleId',
    component: () => import('@/components/LearningLayout.vue'),
    children: [
      {
        path: 'dashboard', 
        name: 'LearningDashboard',
        component: () => import('@/views/LearningDashboard.vue'),
        meta: {
          requiresAuth: true,
          title: 'Learning Dashboard - EasyEcon'
        }
      },
      {
        path: 'lesson/:pageId',
        name: 'LearningChapter',
        component: () => import('@/views/LearningChapter.vue'),
        meta: {
          requiresAuth: true,
          title: 'Learning Chapter - EasyEcon'
        }
      },
      {
        path: 'complete/learn/:pageId',
        name: 'LearningMiniquizPoint',
        component: () => import('@/views/LearningMiniquizPoint.vue'),
        meta: {
          requiresAuth: true,
          title: 'Complete Learning - EasyEcon'
        }
      }
    ]
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