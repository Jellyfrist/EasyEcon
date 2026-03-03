<template>
    <div class="page-wrapper">
    
        <!-- ================= HERO SECTION (PUBLIC) ================= -->
        <section class="hero-section">
    
            <!-- icon on the back -->
            <span class="material-symbols-outlined decor icon-1 highlight-icon">account_balance</span>
            <span class="material-symbols-outlined decor icon-2 highlight-icon">monetization_on</span>
            <span class="material-symbols-outlined decor icon-3 highlight-icon">public</span>
    
            <div class="hero-content">
                <h1>Easy<span class="highlight">Econ</span></h1>
                <h2>Elevate Your Economics Grade</h2>
                <p>
                    Master complex theories with our interactive flashcards, simulated practice tests, and comprehensive study guides tailored for economics students.
                </p>
            </div>
    
            <div class="hero-divider"></div>
    
        </section>
    
    
        <!-- ================ COURSE SECTION ================= -->
        <section class="course-section">
    
            <!-- 
                    If the user is NOT authenticated:
                    Show a public preview (beginner course teaser)
                -->
            <div v-if="!isAuthenticated" class="course-container">
                <div class="course-card">
    
                    <span class="label">
                            Course Overview
                        </span>
    
                    <h3 class="title">
                        751100 - Economics for Everyday Life
                    </h3>
    
                    <div class="course-divider"></div>
    
                    <p class="description">
                        This course provides a comprehensive introduction to fundamental economic principles tailored for practical application. Explore how supply, demand, and market forces shape our daily decisions, while gaining a deeper understanding of national and global
                        economic trends. Designed to empower students with critical thinking skills for a complex world.
                    </p>
    
                    <!-- Require the user to log in or sign up -->
                    <div class="cta-wrapper">
                        <router-link to="/login" class="cta"><button>Learn This Course</button></router-link>
                    </div>
    
                    <div>
                        <router-link to="/teacher" class="text-login">I'm professor</router-link>
                    </div>
    
                </div>
            </div>
    
            <!-- 
                    If the user is authenticated:
                    Show all courses the user is enrolled in.
                -->
            <div v-else class="course-container">
    
                <h1>My Courses</h1>
    
                <div v-for="course in myCourses" :key="course.id">
                    <div class="course-card">
                        <span class="label">
                                Course Overview
                            </span>
    
                        <h3 class="title">{{ course.title }}</h3>
    
                        <div class="course-divider"></div>
    
                        <p class="description">
                            {{ course.description }}
                        </p>
    
                        <button class="btn-enter" @click="$router.push(`/learning/${course.id}`)">
                                Enter Course
                            </button>
                    </div>
                </div>
    
                <!-- 
                        Show message when no enrolled courses exist.
                    -->
                <div v-if="myCourses.length === 0">
                    <div class="course-card">
                        <h2>You are not enrolled in any course yet.</h2>
                    </div>
                </div>
    
            </div>
    
        </section>
    
        <div class="divider">
            <span>You can Learn by</span>
        </div>
    
        <!-- ================= FEATURE SECTION ================= -->
        <section class="features-wrapper">
    
            <!--
                    If the user is NOT authenticated:
                    Blurred this section.
                -->
    
            <section class="features" :class="{ blurred: !isAuthenticated }">
    
                <!-- Flashcards -->
                <div class="card green" @click="goToFlashcards">
                    <h1>Flashcards</h1>
                    <div class="icon-wrapper">
                        <span class="material-symbols-outlined">style</span>
                    </div>
                    <p>
                        Master key economic concepts quickly with interactive flashcards designed for rapid memory retention.
                    </p>
                </div>
    
                <!-- Learn -->
                <div class="card pink" @click="goToLearn">
                    <h1>Learn</h1>
                    <div class="icon-wrapper">
                        <span class="material-symbols-outlined">school</span>
                    </div>
                    <p>
                        Structured lessons with real-world examples to deepen your understanding step by step.
                    </p>
                </div>
    
                <!-- Practice Tests -->
                <div class="card yellow" @click="goToTest">
                    <h1>Practice Tests</h1>
                    <div class="icon-wrapper">
                        <span class="material-symbols-outlined">quiz</span>
                    </div>
                    <p>
                        Test your knowledge with quizzes and scenario-based challenges to reinforce your learning.
                    </p>
                </div>
    
            </section>
    
            <div v-if="!isAuthenticated" class="auth-overlay">
                <div class="overlay-card">
                    <h2>Unlock All Features</h2>
                    <p class="overlay-sub">
                        Please log in or create an account to continue learning.
                    </p>
    
                    <router-link to="/login" class="btn-enter">
                        Log In
                    </router-link>
    
                    <div class="divider-text">or</div>
    
                    <router-link to="/signup" class="text-login">
                        Sign Up
                    </router-link>
                </div>
            </div>
    
        </section>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { authService } from '../services/authService';

// Import composable to check protected feature access
import { useProtectedFeature } from '@/composables/useProtectedFeature';

const router = useRouter(); // Router instance for programmatic navigation

// Reactive state variables
const user = ref(null); // Stores current user profile data
const loading = ref(true); // Controls loading state while checking auth
const myCourses = ref([]); // Stores user's enrolled courses (currently unused)

// isAuthenticated can be used to conditionally render protected UI sections
const { isAuthenticated } = useProtectedFeature();

onMounted(async () => {
    try {
        if (authService.isAuthenticated()) {
            myCourses.value = await learningService.getCourses();
        }
    } catch (err) {
        console.error(err);
    }
});

// Lifecycle hook: runs when component is mounted
onMounted(async () => {
    try {
        // We intentionally DO NOT redirect unauthenticated users.
        // This page is accessible to both guests and logged-in users.

        if (authService.isAuthenticated()) {
            // STEP 1: Load cached user profile from localStorage (if available)
            // This makes the UI feel faster before fetching fresh data.
            const savedUser = localStorage.getItem('user_profile');
            if (savedUser) {
                user.value = JSON.parse(savedUser);
            }

            // STEP 2: Fetch the latest user data from backend API
            // This ensures data consistency with the server.
            const freshUser = await authService.getCurrentUser();

            if (freshUser) {
                user.value = freshUser;

                // Update localStorage cache with fresh data
                localStorage.setItem('user_profile', JSON.stringify(freshUser));
            }
        }
    } catch (error) {
        // If token is invalid or API fails,
        // remove token but DO NOT redirect user away from this page.
        console.error("Auth check failed:", error);
        authService.removeToken();
    } finally {
        // Stop loading spinner regardless of success/failure
        loading.value = false;
    }
});

// Handle user logout
// Clears authentication state and redirects to login page
const handleLogout = () => {
    authService.logout();
    router.push('/login');
};

// Navigation handlers for different features

// Navigate to Flashcards study page
// Note: ':pageId' should be replaced with a real dynamic value
const goToFlashcards = () => {
    router.push('/flashcards')
}

// Navigate to Learning module page
// Note: ':id' should be replaced with actual module ID
const goToLearn = () => {
    router.push('/learning')
}

// Navigate to Test/Exam page
// Note: ':moduleId' should be replaced with actual module ID
const goToTest = () => {
    router.push('/test')
}
</script>

<style scoped>
.page-wrapper {
    background: linear-gradient( 90deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
}

/* ---- Hero section (Top) ---- */

/* - hero section - */

.hero-section {
    position: relative;
    text-align: center;
    padding: 50px 20px 20px;
}

.hero-content {
    position: relative;
    z-index: 2;
}

.hero-section h1 {
    color: black;
    font-size: 110px;
}

.hero-section h1 span {
    color: var(--primary-pink);
}

.hero-section h2 {
    margin-top: 20px;
    color: var(--text-main);
    font-size: 25px;
    font-weight: 700;
}

.hero-section p {
    margin-top: 20px;
    font-size: 18px;
    color: var(--text-muted);
    max-width: 700px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.6;
}

/* - icon (On background) - */

.decor {
    position: absolute;
    z-index: 0;
    color: var(--primary-pink);
    opacity: 0.35;
    pointer-events: none;
}

.icon-1 {
    top: 5%;
    left: 10%;
    font-size: 120px;
}

.icon-2 {
    bottom: 30%;
    left: 1%;
    font-size: 100px;
}

.icon-3 {
    top: 15%;
    right: -50px;
    font-size: 210px;
}

/* ---- Button ---- */

.cta-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 10px 0;
}

.cta {
    text-align: center;
    margin-top: 40px;
}

.cta button {
    background: var(--primary-pink);
    color: white;
    padding: 15px 35px;
    border-radius: 999px;
    border: none;
    font-weight: 700;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 10px 25px rgba(244, 63, 127, 0.3);
    transition: 0.3s;
}

.cta button:hover {
    transform: translateY(1px);
}

.cta a {
    margin-left: 25px;
    color: var(--primary-pink);
    font-weight: 600;
    text-decoration: none;
}

.btn-enter {
    margin-top: 40px;
    padding: 14px 32px;
    border-radius: 999px;
    border: none;
    cursor: pointer;
    font-size: 16px;
    font-weight: 700;
    background: var(--primary-pink);
    color: white;
    transition: all 0.3s ease;
}

.btn-enter:hover {
    transform: translateY(1px);
    box-shadow: 0 2px 10px rgba(233, 30, 99, 0.35);
}

.btn-enter:active {
    transform: scale(0.97);
}

/* ---- text login ---- */

.text-login {
    display: inline-block;
    padding-top: 10px;
    padding-bottom: 10px;
    color: var(--primary-pink);
    font-size: 20px;
    font-weight: 700;
    text-decoration: none;
}

.text-login:hover {
    transform: translateY(1px);
    color: var(--primary-hover);
}

.text-login:active {
    transform: scale(0.95);
}

/* ---- Courses section ---- */

.course-section {
    display: flex;
    justify-content: center;
    padding: 10px 5px;
}

.course-section h1 {
    font-size: 2rem;
    color: #ffe2a2;
    text-align: center;
    background: linear-gradient(135deg, #ff4d8d, #e91e63);
    border-radius: 15px;
    margin-bottom: 8px;
}

.course-container {
    width: 90%;
}

/* Course */

.course-card {
    background: white;
    border-radius: 24px;
    padding: 40px 50px;
    text-align: center;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.08);
    margin-bottom: 20px;
}

/* Label */

.label {
    color: var(--primary-pink);
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
    display: block;
    margin-bottom: 20px;
}

/* Title */

.title {
    font-size: 42px;
    font-weight: 900;
    margin-bottom: 30px;
    line-height: 1.2;
}

/* Description */

.description {
    font-size: 18px;
    line-height: 1.8;
    max-width: 750px;
    margin: auto;
    color: var(--text-muted);
}

/* ---- Features (lock) ---- */

.features-wrapper {
    position: relative;
}

.features {
    display: flex;
    justify-content: center;
    gap: 50px;
    padding: 80px 60px;
}

.auth-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(3px);
    z-index: 10;
}

.overlay-card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    padding: 40px 50px 40px 50px;
    border-radius: 32px;
    text-align: center;
    max-width: 480px;
    width: 90%;
    box-shadow: 0 40px 100px rgba(0, 0, 0, 0.25);
}

.overlay-card h2 {
    font-size: 32px;
    font-weight: 800;
    margin-bottom: 15px;
    color: #1f2937;
}

.overlay-sub {
    font-size: 16px;
    margin-bottom: 35px;
    color: #6b7280;
}

/* ---- Card Base (Feature) ---- */

.card {
    flex: 1;
    padding: 50px 40px;
    border-radius: 32px;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    min-height: 420px;
    transition: all 0.35s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.card:hover {
    transform: translateY(-12px) scale(1.02);
    box-shadow: 0 40px 90px rgba(0, 0, 0, 0.15);
}

/* title */

.card h1 {
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 15px;
}

/* description */

.card p {
    font-size: 18px;
    line-height: 1.7;
    opacity: 0.9;
    max-width: 85%;
}

/* icon */

.icon-wrapper {
    width: 70px;
    height: 70px;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 25px;
    backdrop-filter: blur(6px);
}

.icon-wrapper span {
    font-size: 38px;
}

/* Colors */

.card.green {
    background: linear-gradient(135deg, #0f7a3e, #0b5d30);
    color: white;
}

.card.pink {
    background: linear-gradient(135deg, #ff4d8d, #e91e63);
    color: white;
}

.card.yellow {
    background: linear-gradient(135deg, #ffe2a2, #f1d18c);
    color: #0f172a;
}

/* ---- divider ---- */

.divider-text {
    margin-top: 20px;
    font-weight: 600;
    color: #9ca3af;
}

.divider {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: auto;
    padding-top: 60px;
    padding-bottom: 5px;
    max-width: 1000px;
    width: 70%;
    color: var(--text-muted);
    font-size: 15px;
    letter-spacing: 1px;
}

.hero-divider {
    width: 75%;
    height: 3px;
    margin: 40px auto;
    border-radius: 999px;
    background: #ffffff;
}

.course-divider {
    width: 40%;
    height: 4px;
    background: rgba(255, 77, 141, 0.3);
    margin: 0 auto 30px;
    border-radius: 10px;
}

.divider::before,
.divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--text-muted);
}

.divider span {
    padding: 0 20px;
}

/* ---- Effect ---- */

.blurred {
    filter: blur(3px);
    opacity: 0.6;
}

.highlight {
    background: linear-gradient( 90deg, var(--primary-hover), var(--primary-pink), #fde047);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 4s ease-in-out infinite;
}

.highlight-icon {
    background: linear-gradient( 90deg, rgb(255, 185, 65), var(--primary-pink));
    background-size: 150% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s ease-in-out infinite, floatRotate 4s ease-in-out infinite;
}

@keyframes shine {
    0% {
        background-position: 0% center;
    }
    50% {
        background-position: 100% center;
    }
    100% {
        background-position: 0% center;
    }
}

@keyframes floatRotate {
    0% {
        transform: translateY(0px) rotate(0deg);
    }
    50% {
        transform: translateY(-15px) rotate(10deg);
    }
    100% {
        transform: translateY(0px) rotate(0deg);
    }
}

/* ---- Responsive Design ---- */

/* Mobile */

@media (max-width: 768px) {}
</style>