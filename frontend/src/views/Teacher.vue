<template>
    <div class="t-page">
    
        <!-- hero header -->
        <div class="t-hero">
            <div class="t-hero-glow"></div>
            <div class="t-hero-inner">
                <div class="t-hero-text">
                    <span class="t-hero-label">{{ greeting }}</span>
                    <h1 class="t-hero-title">{{ authStore.fullName }}</h1>
                    <p class="t-hero-desc">Welcome back to your teaching dashboard.</p>
                </div>
                <button class="t-create-btn" @click="router.push('/teacher/courses/create')">
                        <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                            <path d="M7.5 2V13M2 7.5H13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        New Course
                    </button>
            </div>
        </div>
    
        <!-- main content -->
        <div class="t-content">
    
            <!-- section title row -->
            <div class="t-section-header">
                <h2 class="t-section-title">My Courses</h2>
                <span v-if="courseStore.courses.length > 0" class="t-course-count">
                        {{ courseStore.courses.length }} {{ courseStore.courses.length === 1 ? 'course' : 'courses' }}
                    </span>
            </div>
    
            <!-- loading -->
            <div v-if="courseStore.loading" class="t-state-box">
                <div class="t-spinner"></div>
                <p>Loading courses...</p>
            </div>
    
            <!-- error -->
            <div v-else-if="courseStore.error" class="t-state-card">
                <div class="t-state-icon t-icon-red">
                    <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                            <circle cx="11" cy="11" r="9" stroke="currentColor" stroke-width="1.75"/>
                            <path d="M11 7V11.5M11 14.5V15" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>
                        </svg>
                </div>
                <p class="t-state-msg">{{ courseStore.error }}</p>
                <button class="t-btn t-btn-primary" @click="courseStore.fetchMyCourses()">Try Again</button>
            </div>
    
            <!-- empty -->
            <div v-else-if="courseStore.courses.length === 0" class="t-state-card">
                <div class="t-state-icon t-icon-neutral">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <rect x="3" y="5" width="18" height="16" rx="3" stroke="currentColor" stroke-width="1.75"/>
                            <path d="M8 5V4C8 2.9 8.9 2 10 2H14C15.1 2 16 2.9 16 4V5" stroke="currentColor" stroke-width="1.75"/>
                            <path d="M9 12H15M9 15H13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                </div>
                <h3 class="t-state-title">No courses yet</h3>
                <p class="t-state-msg">Create your first course to get started.</p>
                <button class="t-btn t-btn-primary" @click="router.push('/teacher/courses/create')">
                        + Create Course
                    </button>
            </div>
    
            <!-- course grid -->
            <div v-else class="t-course-grid">
                <div v-for="course in courseStore.courses" :key="course.id" class="t-course-card">
                    <div class="t-course-card-top">
                        <div class="t-course-initial">{{ course.title.charAt(0).toUpperCase() }}</div>
                        <span class="t-course-label">Course</span>
                    </div>
    
                    <h3 class="t-course-title">{{ course.title }}</h3>
                    <p class="t-course-desc">{{ course.description || 'No description provided.' }}</p>
    
                    <div class="t-course-meta">
                        <span class="t-meta-pill">
                                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                                    <rect x="1" y="2.5" width="8" height="6" rx="1.25" stroke="currentColor" stroke-width="1.25"/>
                                    <rect x="3" y="1" width="8" height="6" rx="1.25" stroke="currentColor" stroke-width="1.25"/>
                                </svg>
                                {{ course.flashcard_set_count ?? 0 }} sets
                            </span>
                        <span class="t-meta-pill">
                                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                                    <rect x="1" y="1" width="10" height="10" rx="1.5" stroke="currentColor" stroke-width="1.25"/>
                                    <path d="M3.5 4H8.5M3.5 6H7M3.5 8H6" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/>
                                </svg>
                                {{ course.module_count ?? 0 }} modules
                            </span>
                        <span class="t-meta-pill">
                                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                                    <path d="M3 1H9C9.6 1 10 1.4 10 2V11L8 10L6 11L4 10L2 11V2C2 1.4 2.4 1 3 1Z" stroke="currentColor" stroke-width="1.25" stroke-linejoin="round"/>
                                </svg>
                                {{ course.exam_template_count ?? 0 }} exams
                            </span>
                    </div>
    
                    <button class="t-btn t-btn-edit" @click="router.push(`/teacher/courses/${course.id}/edit`)">
                            Manage Course
                            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                                <path d="M5 10L9 6.5L5 3" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                </div>
            </div>
    
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'
import { useCourseStore } from '@/store/courseStore'

const router = useRouter()
const authStore = useAuthStore()
const courseStore = useCourseStore()

// greeting based on time of day
const greeting = computed(() => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good Morning,'
    if (hour < 18) return 'Good Afternoon,'
    return 'Good Evening,'
})

// load teacher's own courses on mount
// store.fetchMyCourses -> GET /courses (teacher, returns CourseResponse with counts)
onMounted(async () => {
    await courseStore.fetchMyCourses()
})
</script>

<style scoped>
/* ---- page shell ---- */

.t-page {
    min-height: 100vh;
    background: #f8f9fb;
    font-family: 'DM Sans', 'Helvetica Neue', sans-serif;
}

/* ---- hero header ---- */

.t-hero {
    position: relative;
    width: 100%;
    background: linear-gradient(135deg, #130610 0%, #3b0d21 55%, #130610 100%);
    padding: 4.5rem 6vw 4rem;
    overflow: hidden;
    box-sizing: border-box;
}

.t-hero-glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 55% 90% at 75% 50%, rgba(233, 30, 99, 0.2) 0%, transparent 70%), radial-gradient(ellipse 35% 60% at 15% 30%, rgba(255, 77, 141, 0.1) 0%, transparent 60%);
    pointer-events: none;
}

.t-hero-inner {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1.5rem;
}

.t-hero-label {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #f06292;
    background: rgba(233, 30, 99, 0.15);
    border: 1px solid rgba(233, 30, 99, 0.35);
    border-radius: 4px;
    padding: 0.22rem 0.7rem;
    margin-bottom: 1.2rem;
}

.t-hero-title {
    font-size: clamp(1.75rem, 3.5vw, 2.8rem);
    font-weight: 800;
    color: #fff;
    line-height: 1.15;
    letter-spacing: -0.02em;
    margin: 0 0 1rem;
}

.t-hero-desc {
    font-size: 0.975rem;
    color: rgba(255, 255, 255, 0.55);
    line-height: 1.75;
    max-width: 560px;
    margin: 0;
}

/* ---- header create button ---- */

.t-create-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.65rem 1.3rem;
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
    border: 1.5px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
    white-space: nowrap;
    font-family: inherit;
    position: relative;
    z-index: 2;
}

.t-create-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.35);
}

/* ---- main content ---- */

.t-content {
    padding: 2.25rem 3rem 4rem;
}

/* ---- section header ---- */

.t-section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}

.t-section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    letter-spacing: -0.01em;
}

.t-course-count {
    font-size: 0.775rem;
    font-weight: 600;
    background: #fce7ef;
    color: #ed4081;
    padding: 3px 10px;
    border-radius: 999px;
}

/* ---- state boxes ---- */

.t-state-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 4rem;
    color: #94a3b8;
    font-size: 0.875rem;
}

.t-spinner {
    width: 32px;
    height: 32px;
    border: 2.5px solid #e2e8f0;
    border-top-color: #ed4081;
    border-radius: 50%;
    animation: t-spin 0.7s linear infinite;
}

@keyframes t-spin {
    to {
        transform: rotate(360deg);
    }
}

.t-state-card {
    background: #ffffff;
    border: 1px solid #e8edf3;
    border-radius: 16px;
    padding: 3rem 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.t-state-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.25rem;
}

.t-icon-red {
    background: #fff1f2;
    color: #e11d48;
}

.t-icon-neutral {
    background: #f1f5f9;
    color: #64748b;
}

.t-state-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
}

.t-state-msg {
    font-size: 0.85rem;
    color: #94a3b8;
    margin: 0;
}

/* ---- shared button ---- */

.t-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.2rem;
    font-size: 0.875rem;
    font-weight: 600;
    border-radius: 9px;
    border: none;
    cursor: pointer;
    transition: all 0.15s;
    font-family: inherit;
}

.t-btn-primary {
    background: #ed4081;
    color: #ffffff;
}

.t-btn-primary:hover {
    background: #d13570;
    box-shadow: 0 4px 12px rgba(237, 64, 129, 0.3);
    transform: translateY(-1px);
}

/* ---- course grid ---- */

.t-course-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.25rem;
}

/* ---- course card ---- */

.t-course-card {
    background: #ffffff;
    border: 1.5px solid #e8edf3;
    border-radius: 16px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
}

.t-course-card:hover {
    border-color: #ffc7db;
    border-color: #ffc7db;
    box-shadow: 0 6px 20px rgba(237, 64, 129, 0.1);
    transform: translateY(-2px);
}

.t-course-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.t-course-initial {
    width: 40px;
    height: 40px;
    border-radius: 11px;
    background: linear-gradient(135deg, #ed4081, #d13570);
    color: #ffffff;
    font-size: 1.1rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    letter-spacing: -0.02em;
}

.t-course-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.t-course-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    letter-spacing: -0.01em;
    line-height: 1.35;
}

.t-course-desc {
    font-size: 0.825rem;
    color: #94a3b8;
    margin: 0;
    line-height: 1.55;
    flex: 1;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* ---- meta pills ---- */

.t-course-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    padding: 0.75rem 0;
    border-top: 1px solid #f1f5f9;
    border-bottom: 1px solid #f1f5f9;
    margin: 0.25rem 0;
}

.t-meta-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 3px 9px;
    border-radius: 999px;
}

/* ---- card edit button ---- */

.t-btn-edit {
    background: #f8fafc;
    color: #374151;
    border: 1.5px solid #e2e8f0;
    padding: 0.55rem 1rem;
    font-size: 0.825rem;
    width: 100%;
    justify-content: center;
    margin-top: 0.25rem;
    border-radius: 9px;
}

.t-btn-edit:hover {
    border-color: #ffc7db;
    background: #f1f5f9;
    border-color: #ffc7db;
    color: #ed4081;
}

/* ---- responsive ---- */

@media (max-width: 768px) {
    .t-hero {
        padding: 2.5rem 1.25rem 2rem;
    }
    .t-hero-inner {
        flex-direction: column;
        align-items: flex-start;
    }
    .t-create-btn {
        width: 100%;
        justify-content: center;
    }
    .t-content {
        padding: 1.5rem 1.25rem 3rem;
    }
    .t-course-grid {
        grid-template-columns: 1fr;
    }
}
</style>