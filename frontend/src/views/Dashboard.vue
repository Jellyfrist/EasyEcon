<template>
    <div class="dashboard-wrapper">
    
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
                    Master theories with our practice past exams, <br> comprehensive study of each course, and interactive flashcards.
                </p>
            </div>
    
        </section>
    
    
        <!-- ================ COURSE SECTION ================= -->
        <section class="course-section">
    
            <!-- logged in: grid of course tiles -->
            <div v-if="isAuthenticated" class="course-auth">
                <!-- loading state -->
                <div v-if="store.loading" class="course-empty">
                    <span class="material-symbols-outlined course-empty-icon">hourglass_top</span>
                    <p>Loading your courses...</p>
                </div>
    
                <!-- error state -->
                <div v-else-if="store.error" class="course-empty">
                    <span class="material-symbols-outlined course-empty-icon">error</span>
                    <p>{{ store.error }}</p>
                </div>
    
                <!-- has courses: show tiles -->
                <div v-else-if="myCourses.length > 0" class="course-grid">
                    <div v-for="course in myCourses" :key="course.id" class="course-tile" @click="$router.push(`/courses/${course.id}`)">
                        <!-- decorative icon in background -->
                        <span class="material-symbols-outlined tile-bg-icon">school</span>
                        <div class="tile-content">
                            <span class="tile-label">Course</span>
                            <h3 class="tile-title">{{ course.title }}</h3>
                            <span class="tile-arrow material-symbols-outlined">arrow_forward</span>
                        </div>
                    </div>
                </div>
    
                <!-- no courses yet -->
                <div v-else class="course-empty">
                    <span class="material-symbols-outlined course-empty-icon">inbox</span>
                    <p>No courses yet.</p>
                </div>
    
            </div>
    
        </section>
    
        <!-- ================= FEATURE SECTION ================= -->
        <section class="features-wrapper">
    
            <!-- section header -->
            <div class="features-header">
                <span class="features-eyebrow">What you can do</span>
                <h4 class="features-title">Everything you need<br>to ace economics</h4>
            </div>
    
            <!-- lock overlay when user is not logged in -->
            <div v-if="!isAuthenticated" class="auth-overlay">
                <div class="overlay-card">
                    <h2>Unlock All Features</h2>
                    <p class="overlay-sub">
                        Please log in or create an account to continue learning.
                    </p>
                    <router-link to="/login" class="btn-enter">Log In</router-link>
                    <div class="divider-text">or</div>
                    <router-link to="/signup" class="text-login">Sign Up</router-link>
                </div>
            </div>
    
            <div :class="{ blurred: !isAuthenticated }">
    
    
                <!-- row 1: illustration left, text right -->
                <div class="feature-row">
                    <div class="feature-visual visual-pink">
                        <div class="visual-inner">
                            <div class="vi-chip">Question 3 of 10</div>
                            <div class="vi-question">What happens to price when supply increases?</div>
                            <div class="vi-options">
                                <div class="vi-option correct"><span class="material-symbols-outlined">check_circle</span> Price decreases</div>
                                <div class="vi-option"><span class="material-symbols-outlined">radio_button_unchecked</span> Price increases</div>
                                <div class="vi-option"><span class="material-symbols-outlined">radio_button_unchecked</span> Demand drops</div>
                            </div>
                        </div>
                    </div>
                    <div class="feature-text">
                        <span class="feat-num">01</span>
                        <h3>Past Exams</h3>
                        <p>Test your knowledge with past midterm and final exams to reinforce your learning.</p>
                    </div>
                </div>
    
                <!-- row 2: text left, illustration right -->
                <div class="feature-row reverse">
                    <div class="feature-visual visual-pink">
                        <img src="@/assets/Dashboard_learning.png" class="feature-img" />
                    </div>
                    <div class="feature-text">
                        <span class="feat-num">02</span>
                        <h3>Learning Modules</h3>
                        <p>Structured lessons with real-world examples to deepen your understanding step by step.</p>
                    </div>
                </div>
    
                <!-- row 3: illustration left, text right -->
                <div class="feature-row">
                    <div class="feature-visual visual-pink">
                        <!-- swap: replace inner content with <img src="@/assets/flashcard-preview.png" class="feature-img" /> -->
                        <img src="@/assets/Dashboard_flashcard.png" class="feature-img" />
                    </div>
                    <div class="feature-text">
                        <span class="feat-num">03</span>
                        <h3>Flashcards</h3>
                        <p>Master key economic concepts quickly with interactive flashcards designed for rapid memory retention.</p>
                    </div>
                </div>
    
            </div>
        </section>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { authService } from '../services/authService';
import { useCourseStore } from '@/store/courseStore';

// check protected feature access
import { useProtectedFeature } from '@/composables/useProtectedFeature';

const router = useRouter();
const store = useCourseStore();

// reactive state
const user = ref(null);
const loading = ref(true);

// storeToRefs keeps reactivity when destructuring from pinia store
const { courses: myCourses } = storeToRefs(store);

const { isAuthenticated } = useProtectedFeature();

onMounted(async () => {
    try {
        // this page is public - guests can see it too, no redirect needed
        if (authService.isAuthenticated()) {
            // get fresh user profile
            const freshUser = await authService.getProfile();
            if (freshUser) user.value = freshUser;

            // fetch all courses the student can see
            await store.browseCourses();
        }
    } catch (error) {
        // if token is expired or invalid, clear it but stay on this page
        console.error('auth check failed:', error);
        authService.removeToken();
    } finally {
        loading.value = false;
    }
});

// handle user logout
const handleLogout = () => {
    authService.logout();
    router.push('/login');
};
</script>

<style scoped>
.dashboard-wrapper {
    /* no background here - each section sets its own full-width background */
    width: 100%;
    overflow-x: hidden;
}

/* ---- Hero section (Top) ---- */

/* - hero section - */

.hero-section {
    position: relative;
    text-align: center;
    padding: 50px 20px 20px;
    background: linear-gradient(90deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
    width: 100%;
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

/* ---- Course section ---- */

.course-section {
    width: 100%;
}

.course-login-btn {
    display: inline-block;
    background: #f43f7f;
    color: white;
    font-size: 16px;
    font-weight: 700;
    padding: 14px 40px;
    border-radius: 999px;
    text-decoration: none;
    transition: all 0.25s ease;
    box-shadow: 0 8px 24px rgba(244, 63, 127, 0.25);
}

.course-login-btn:hover {
    background: #d81b60;
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(244, 63, 127, 0.35);
}

.course-teacher-link {
    display: block;
    margin-top: 16px;
    color: #9ca3af;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.2s;
}

.course-teacher-link:hover {
    color: #f43f7f;
}

/* logged in: grid of tiles */

.course-auth {
    padding: 48px 80px;
    width: 100%;
    box-sizing: border-box;
    display: flex;
    justify-content: center;
}

.course-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 20px;
    width: 100%;
    max-width: 1200px;
}

.course-tile {
    background: white;
    border: 1.5px solid #f0f0f0;
    border-radius: 20px;
    padding: 32px 28px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    width: 260px;
    flex-shrink: 0;
}

.course-tile:hover {
    background: #fff5f8;
    border-color: #f43f7f;
    transform: translateY(-4px);
    box-shadow: 0 16px 40px rgba(244, 63, 127, 0.12);
}

/* big icon sitting in the background of the tile */

.tile-bg-icon {
    position: absolute;
    font-size: 100px;
    color: #f43f7f;
    opacity: 0.05;
    right: -10px;
    bottom: -10px;
    pointer-events: none;
}

.tile-content {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.tile-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #f43f7f;
}

.tile-title {
    font-size: 20px;
    font-weight: 800;
    color: #111827;
    line-height: 1.3;
    margin: 0;
}

.tile-arrow {
    font-size: 20px;
    color: #f43f7f;
    margin-top: 12px;
    transition: transform 0.2s;
}

.course-tile:hover .tile-arrow {
    transform: translateX(4px);
}

/* empty state */

.course-empty {
    text-align: center;
    color: #6b7280;
    padding: 60px 0;
}

.course-empty-icon {
    font-size: 48px;
    opacity: 0.4;
    display: block;
    margin-bottom: 12px;
    color: #f43f7f;
}

.course-empty p {
    font-size: 17px;
    font-weight: 500;
}

/* ---- Features section ---- */

.features-wrapper {
    position: relative;
    background: #ffffff;
    padding: 80px 0 60px;
    border-top: 1px solid #f0f0f0;
    width: 100%;
}

/* section header */

.features-header {
    text-align: center;
    margin-bottom: 40px;
    padding: 0 24px;
}

.features-eyebrow {
    display: inline-block;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--primary-pink);
    margin-bottom: 16px;
}

.features-title {
    font-size: 48px;
    font-weight: 800;
    color: #111827;
    line-height: 1.15;
    margin: 0;
}

/* lock overlay */

.auth-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    backdrop-filter: blur(4px);
    z-index: 10;
}

.overlay-card {
    background: white;
    padding: 48px 52px;
    border-radius: 24px;
    text-align: center;
    max-width: 440px;
    width: 90%;
    box-shadow: 0 32px 80px rgba(0, 0, 0, 0.14);
}

.overlay-card h2 {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 12px;
    color: #111827;
}

.overlay-sub {
    font-size: 15px;
    margin-bottom: 32px;
    color: #6b7280;
    line-height: 1.6;
}

/* ---- alternating rows ---- */

.feature-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 64px;
    padding: 48px 80px;
    max-width: 1200px;
    margin: 0 auto;
}

/* reverse: illustration on right */

.feature-row.reverse {
    flex-direction: row-reverse;
}

/* ---- illustration side ---- */

.feature-visual {
    flex: 1;
    max-width: 480px;
    border-radius: 0px;
    padding: 20px;
    min-height: 340px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}

/* subtle noise texture overlay */

.feature-visual::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    border-radius: 28px;
}

.visual-green {
    background: linear-gradient(145deg, #0d6b37, #0a5229);
}

.visual-pink {
    background: linear-gradient(145deg, #ff649a, #fc4d8d);
}

.visual-yellow {
    background: linear-gradient(145deg, #f5ca0b, #efb001);
}

.visual-gray {
    background: linear-gradient(145deg, #bec7da, #b2bfd1);
}

/* the white card inside the illustration */

.visual-inner {
    background: rgba(255, 255, 255, 0.97);
    border-radius: 18px;
    padding: 24px 26px;
    width: 100%;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
    position: relative;
    z-index: 2;
}

/* small chip/badge at the top */

.vi-chip {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #9ca3af;
    background: #f3f4f6;
    padding: 4px 10px;
    border-radius: 999px;
    margin-bottom: 14px;
}

/* flashcard styles */

.vi-card-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #d1d5db;
    margin-bottom: 6px;
}

.vi-card-word {
    font-size: 20px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 10px;
}

.vi-card-def {
    font-size: 13px;
    color: #6b7280;
    line-height: 1.6;
    margin-bottom: 18px;
}

.vi-nav {
    display: flex;
    gap: 6px;
}

.vi-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #e5e7eb;
    display: inline-block;
}

.vi-dot.active {
    background: #111827;
    width: 22px;
    border-radius: 4px;
}

/* learning module styles */

.vi-module-title {
    font-size: 17px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 14px;
}

.vi-progress-wrap {
    margin-bottom: 18px;
}

.vi-progress-label {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    font-weight: 600;
    color: #9ca3af;
    margin-bottom: 6px;
}

.vi-progress-track {
    height: 6px;
    background: #f3f4f6;
    border-radius: 999px;
    overflow: hidden;
}

.vi-progress-bar {
    width: 45%;
    height: 100%;
    background: linear-gradient(90deg, #f43f7f, #d81b60);
    border-radius: 999px;
}

.vi-lessons {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.vi-lesson {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #9ca3af;
    font-weight: 500;
}

.vi-lesson .material-symbols-outlined {
    font-size: 16px;
}

.vi-lesson.done {
    color: #6b7280;
}

.vi-lesson.done .material-symbols-outlined {
    color: #10b981;
}

.vi-lesson.active {
    color: #111827;
    font-weight: 700;
}

.vi-lesson.active .material-symbols-outlined {
    color: #f43f7f;
}

/* past exam styles */

.vi-question {
    font-size: 15px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 16px;
    line-height: 1.45;
}

.vi-options {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.vi-option {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-radius: 10px;
    background: #f9fafb;
    font-size: 13px;
    font-weight: 600;
    color: #374151;
    border: 1.5px solid #f3f4f6;
}

.vi-option .material-symbols-outlined {
    font-size: 16px;
    color: #d1d5db;
}

.vi-option.correct {
    background: #f0fdf4;
    border-color: #bbf7d0;
    color: #065f46;
}

.vi-option.correct .material-symbols-outlined {
    color: #10b981;
}

/* ---- text side ---- */

.feature-text {
    flex: 1;
    max-width: 440px;
}

/* large muted number */

.feat-num {
    display: block;
    font-size: 72px;
    font-weight: 900;
    color: var(--primary-pink);
    line-height: 1;
    margin-bottom: 4px;
    letter-spacing: -2px;
    user-select: none;
}

.feature-text h3 {
    font-size: 36px;
    font-weight: 800;
    color: #111827;
    margin: 0 0 16px 0;
    line-height: 1.15;
}

.feature-text p {
    font-size: 17px;
    line-height: 1.75;
    color: #6b7280;
    margin: 0;
}

/* ---- dividers ---- */

.divider-text {
    margin-top: 20px;
    font-weight: 600;
    color: #9ca3af;
}

.course-divider {
    width: 40%;
    height: 4px;
    background: rgba(255, 77, 141, 0.3);
    margin: 0 auto 30px;
    border-radius: 10px;
}

/* ready for real image swap-in */

.feature-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 0px;
    position: relative;
    z-index: 2;
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

/* tablet: 768px - 1024px */

@media (max-width: 1024px) {
    /* hero */
    .hero-section h1 {
        font-size: 72px;
    }
    .hero-section h2 {
        font-size: 20px;
    }
    .hero-section p {
        font-size: 16px;
    }
    .icon-1 {
        font-size: 80px;
    }
    .icon-2 {
        font-size: 70px;
    }
    .icon-3 {
        font-size: 140px;
        right: -30px;
    }
    /* course */
    .title {
        font-size: 28px;
    }
    .description {
        font-size: 16px;
    }
    .course-auth {
        padding: 36px 40px;
    }
    /* features */
    .features-title {
        font-size: 36px;
    }
    .feature-row {
        gap: 40px;
        padding: 36px 48px;
    }
    .feature-visual {
        min-height: 280px;
        padding: 28px;
    }
    .feat-num {
        font-size: 52px;
    }
    .feature-text h3 {
        font-size: 28px;
    }
    .feature-text p {
        font-size: 15px;
    }
}

/* mobile: below 768px */

@media (max-width: 768px) {
    /* hero */
    .hero-section {
        padding: 40px 16px 20px;
    }
    .hero-section h1 {
        font-size: 52px;
    }
    .hero-section h2 {
        font-size: 17px;
    }
    .hero-section p {
        font-size: 14px;
    }
    /* hide background icons so they don't overlap content */
    .icon-1,
    .icon-2,
    .icon-3 {
        display: none;
    }
    .hero-divider {
        width: 90%;
        margin: 24px auto;
    }
    /* course */
    .course-guest {
        padding: 60px 20px;
    }
    .course-guest-box h2 {
        font-size: 26px;
    }
    .course-guest-box p {
        font-size: 15px;
    }
    .course-auth {
        padding: 28px 20px;
    }
    .course-grid {
        justify-content: center;
    }
    .course-tile {
        width: 100%;
        max-width: 400px;
    }
    .cta button {
        font-size: 16px;
        padding: 12px 24px;
    }
    /* features header */
    .features-wrapper {
        padding: 56px 0 40px;
    }
    .features-header {
        margin-bottom: 48px;
    }
    .features-title {
        font-size: 28px;
    }
    /* rows: stack vertically on mobile */
    .feature-row,
    .feature-row.reverse {
        flex-direction: column;
        gap: 28px;
        padding: 40px 20px;
    }
    /* illustration full width */
    .feature-visual {
        width: 100%;
        max-width: 100%;
        min-height: 240px;
        padding: 24px;
    }
    /* text full width, centered */
    .feature-text {
        max-width: 100%;
        text-align: center;
    }
    .feat-num {
        font-size: 48px;
    }
    .feature-text h3 {
        font-size: 24px;
    }
    .feature-text p {
        font-size: 15px;
    }
    /* overlay */
    .overlay-card {
        padding: 28px 24px;
    }
    .overlay-card h2 {
        font-size: 22px;
    }
}

/* small mobile: below 480px */

@media (max-width: 480px) {
    .hero-section h1 {
        font-size: 40px;
    }
    .hero-section h2 {
        font-size: 15px;
    }
    .features-title {
        font-size: 24px;
    }
    .feature-row,
    .feature-row.reverse {
        padding: 32px 16px;
    }
    .feat-num {
        font-size: 40px;
    }
    .feature-text h3 {
        font-size: 22px;
    }
}
</style>