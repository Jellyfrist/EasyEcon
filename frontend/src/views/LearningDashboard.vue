<template>
    <div class="layout-wrapper">
    
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="nav-links">
                    <button @click="goBack" class="nav-btn">
                <div class="back-icon-circle">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="19" y1="12" x2="5" y2="12"></line>
                    <polyline points="12 19 5 12 12 5"></polyline>
                  </svg>
                </div>
                <span class="nav-text">Back to Modules</span>
              </button>
                </div>
    
                <div class="title-group">
                    <p class="list-title">LESSONS ({{ courseModules.length }})</p>
                </div>
            </div>
    
            <nav class="module-list" v-if="courseModules.length > 0">
                <div v-for="(mod, index) in courseModules" :key="mod.id" :class="['module-card', { active: activeModuleId === mod.id }]" @click="goToModule(mod.id)">
                    <div class="module-info">
                        <div class="module-top-row">
                            <div class="icon-box">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                      </svg>
                            </div>
    
                            <span class="module-status" v-if="activeModuleId === mod.id">In Progress</span>
                        </div>
                        <p class="module-name">{{ mod.title }}</p>
                    </div>
    
                    <span class="action-icon">
                  <svg v-if="activeModuleId === mod.id" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                     <circle cx="12" cy="12" r="10"></circle>
                     <polygon points="10 8 16 12 10 16 10 8"></polygon>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="9 18 15 12 9 6"></polyline>
                  </svg>
              </span>
                </div>
            </nav>
            <div v-else class="sidebar-loading">Loading modules...</div>
        </aside>
    
        <main class="main-content">
    
            <div v-if="isLoading" class="loading-state">
                <div class="spinner"></div>
                <p>Loading lesson data...</p>
            </div>
    
            <div v-else-if="dashboardData" class="dashboard-container">
    
                <nav class="breadcrumb">
                    <span class="bc-link" @click="router.push(`/courses/${courseId}/modules`)">Course</span>
                    <span class="material-symbols-outlined bc-arrow">chevron_right</span>
                    <span class="bc-current">Module {{ currentModuleIndex + 1 }}</span>
                </nav>
    
                <section class="hero-section">
                    <div class="hero-text">
                        <h1 class="hero-title">
                            {{ dashboardData.module?.title }}
                        </h1>
                        <p class="hero-desc">
                            Explore the core concepts of this module and build your understanding step by step.
                        </p>
                    </div>
    
                    <div class="progress-card">
                        <div class="circle-wrap">
                            <svg class="circle-svg" viewBox="0 0 44 44">
                    <circle cx="22" cy="22" r="18" fill="none" stroke="#fce4ec" stroke-width="4"/>
                    <circle
                      cx="22" cy="22" r="18"
                      fill="none"
                      stroke="#df4a7d"
                      stroke-width="4"
                      stroke-linecap="round"
                      stroke-dasharray="113"
                      :stroke-dashoffset="113 - (113 * dashboardData.progress_percent / 100)"
                      transform="rotate(-90 22 22)"
                      style="transition: stroke-dashoffset 0.6s ease;"
                    />
                  </svg>
                            <span class="circle-pct">{{ dashboardData.progress_percent }}%</span>
                        </div>
                        <div class="progress-info">
                            <p class="progress-label">PROGRESS</p>
                            <p class="progress-value">{{ dashboardData.completed_pages }} / {{ dashboardData.total_pages }} topics</p>
                        </div>
                    </div>
                </section>
    
                <div class="section-header">
                    <h2 class="section-title">Lesson Plan</h2>
                </div>
    
                <div class="lesson-list">
                    <div v-for="(page, index) in dashboardData.pages" :key="page.id" class="lesson-card" :class="page.status">
                        <div class="status-icon" :class="page.status">
                            <svg v-if="page.status === 'completed'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                     <polyline points="20 6 9 17 4 12"></polyline>
                   </svg>
                            <svg v-else-if="page.status === 'active'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                     <polyline points="20 6 9 17 4 12"></polyline>
                   </svg>
                            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                   </svg>
                        </div>
    
                        <div class="lesson-details">
                            <div class="lesson-meta">
                                <span class="lesson-index">{{ currentModuleIndex + 1 }}.{{ index + 1 }}</span>
                                <span class="lesson-type-badge">Lesson</span>
                            </div>
                            <h3 class="lesson-title">{{ page.title }}</h3>
                            <p class="lesson-desc">Click to study this topic and complete the lesson.</p>
                        </div>
    
                        <button @click="goToLesson(page.id)" class="lesson-btn" :class="page.status" :disabled="page.status === 'locked'">
                  {{ page.status === 'completed' ? 'Review Again' : page.status === 'active' ? 'Start Lesson' : 'Locked' }}
                </button>
                    </div>
                </div>
    
            </div>
        </main>
    
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useLearningStore } from '@/store/learningStore';

const route = useRoute();
const router = useRouter();
const learningStore = useLearningStore();

const courseId = computed(() => route.params.courseId);
const moduleId = computed(() => route.params.moduleId);

const dashboardData = ref(null);
const isLoading = ref(true);
const courseModules = ref([]);

const currentModuleIndex = computed(() => {
    const idx = courseModules.value.findIndex(m => m.id == moduleId.value);
    return idx >= 0 ? idx : 0;
});

const loadDashboard = async (mId) => {
    isLoading.value = true;
    try {
        const res = await learningStore.fetchModuleDashboard(mId);
        if (res && res.chapterInfo) {
            dashboardData.value = {
                module: { title: res.chapterInfo.title, description: res.chapterInfo.description },
                progress_percent: res.chapterInfo.progressPercent,
                completed_pages: res.chapterInfo.completedCount,
                total_pages: res.chapterInfo.totalCount,
                pages: res.lessons
            };
        }
    } catch (error) {
        console.error("Dashboard Load Error:", error);
    } finally {
        isLoading.value = false;
    }
};

const loadSidebar = async () => {
    await learningStore.fetchModules(courseId.value);
    courseModules.value = learningStore.modules;
};

// Map URL moduleId to state activeModuleId for sidebar styling
const activeModuleId = computed(() => {
    return Number(moduleId.value);
});


onMounted(async () => {
    await loadSidebar();
    if (moduleId.value) {
        await loadDashboard(moduleId.value);
    } else if (courseModules.value.length > 0) {
        router.replace(`/courses/${courseId.value}/modules/${courseModules.value[0].id}`);
    }
});

watch(moduleId, async (newId) => {
    if (newId) await loadDashboard(newId);
});

const goToModule = (mId) => {
    if (moduleId.value == mId) return;
    router.push(`/courses/${courseId.value}/modules/${mId}`);
};

const goToLesson = (pageId) => {
    if (!pageId) {
        alert("Page ID not found.");
        return;
    }
    router.push({
        name: 'LearningChapter',
        params: {
            courseId: courseId.value,
            moduleId: moduleId.value,
            pageId: pageId
        }
    });
};

const goBack = () => {
    router.push(`/courses/${courseId.value}/modules`);
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap');
/* =====================================================
   Layout Wrapper
   ===================================================== */

.layout-wrapper {
    display: flex;
    min-height: 100vh;
    background: linear-gradient(90deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
    font-family: 'DM Sans', 'Sarabun', sans-serif;
    padding: 2rem;
    gap: 2rem;
    box-sizing: border-box;
}

.material-symbols-outlined {
    vertical-align: middle;
}

/* =====================================================
   Sidebar
   ===================================================== */

.sidebar {
    width: 300px;
    background-color: #df4a7d;
    border-radius: 24px;
    box-shadow: 0 10px 30px rgba(223, 74, 125, 0.2);
    border: none;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    height: calc(100vh - 4rem);
    position: sticky;
    top: 2rem;
    overflow: hidden;
}

.sidebar-header {
    padding: 2rem 1.5rem 1rem 1.5rem;
}

/* Navigation Buttons (Back to Modules) */

.nav-links {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 2rem;
}

.nav-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    background: transparent;
    border: none;
    padding: 0;
    color: #ffffff;
    cursor: pointer;
    transition: all 0.2s ease;
    width: 100%;
    text-align: left;
}

.back-icon-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.4);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.nav-text {
    font-weight: 700;
    font-size: 1rem;
}

.nav-btn:hover .back-icon-circle {
    background-color: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.8);
}

.nav-btn:hover .nav-text {
    opacity: 0.8;
}

/* Section Title */

.title-group {
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    margin-bottom: 0.5rem;
}

.list-title {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.8);
    font-weight: 800;
    margin: 0;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Module List */

.module-list {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem 1.25rem 1.5rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.module-list::-webkit-scrollbar {
    width: 4px;
}

.module-list::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
}

.module-list::-webkit-scrollbar-track {
    background-color: transparent;
}

/* Module Card Styles */

.module-card {
    padding: 1.25rem;
    border-radius: 16px;
    cursor: pointer;
    background-color: transparent;
    border: 1px solid transparent;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s ease;
    position: relative;
}

.module-card:hover:not(.active) {
    background-color: rgba(255, 255, 255, 0.1);
    transform: translateX(3px);
}

/* Active State */

.module-card.active {
    background-color: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.4);
}

.module-info {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    flex: 1;
}

.module-top-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.icon-box {
    color: rgba(255, 255, 255, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
}

.active .icon-box {
    color: #ffffff;
}

.module-status {
    font-size: 0.65rem;
    font-weight: 800;
    color: #df4a7d;
    background: #ffffff;
    padding: 2px 8px;
    border-radius: 20px;
    text-transform: uppercase;
}

.module-name {
    font-size: 0.95rem;
    margin: 0;
    color: rgba(255, 255, 255, 0.8);
    font-weight: 700;
    line-height: 1.4;
    padding-right: 10px;
}

.active .module-name {
    color: #ffffff;
    font-weight: 800;
}

/* Action Icon (Right Side) */

.action-icon {
    color: rgba(255, 255, 255, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.active .action-icon {
    color: #ffffff;
}

.sidebar-loading {
    text-align: center;
    padding: 3rem 1rem;
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.875rem;
    font-weight: 500;
}

/* =====================================================
   Main Content Area
   ===================================================== */

.main-content {
    flex: 1;
    overflow-y: auto;
    padding: 0;
}

.dashboard-container {
    max-width: 900px;
    margin: 0 auto;
}

/* Breadcrumb */

.breadcrumb {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 2rem;
}

.bc-link {
    color: #4b5563;
    cursor: pointer;
    transition: color 0.2s;
}

.bc-link:hover {
    color: #df4a7d;
}

.bc-arrow {
    font-size: 16px;
}

.bc-current {
    color: #1f2937;
    font-weight: 800;
}

/* =====================================================
   Hero Section
   ===================================================== */

.hero-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2.5rem;
    margin-bottom: 3rem;
    background: #ffffff;
    border: 1px solid #ffffff;
    border-radius: 24px;
    padding: 2.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
}

.hero-text {
    flex: 1;
    max-width: 600px;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #111827;
    margin: 0 0 1rem;
    line-height: 1.3;
    letter-spacing: -0.02em;
}

.hero-desc {
    font-size: 1rem;
    color: #6b7280;
    line-height: 1.6;
    margin: 0;
    font-weight: 500;
}

/* Progress Card in Hero */

.progress-card {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    flex-shrink: 0;
    background: #faf9f7;
    border: 1px solid #f3f4f6;
    border-radius: 16px;
    padding: 1.5rem 2rem;
}

.circle-wrap {
    position: relative;
    width: 56px;
    height: 56px;
    flex-shrink: 0;
}

.circle-svg {
    width: 56px;
    height: 56px;
}

.circle-pct {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.9rem;
    font-weight: 800;
    color: #df4a7d;
}

.progress-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.progress-label {
    font-size: 0.75rem;
    font-weight: 800;
    color: #9ca3af;
    letter-spacing: 0.05em;
    margin: 0;
}

.progress-value {
    font-size: 1.1rem;
    font-weight: 800;
    color: #111827;
    margin: 0;
}

/* =====================================================
   Lesson Plan List
   ===================================================== */

.section-header {
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #111827;
    margin: 0;
    letter-spacing: -0.01em;
}

.lesson-list {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.lesson-card {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    background: #ffffff;
    border: 1px solid #ffffff;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

/* State Styling for Lesson Cards */

.lesson-card.active {
    border-color: #fecdd3;
    box-shadow: 0 4px 20px rgba(223, 74, 125, 0.1);
}

.lesson-card.locked {
    opacity: 0.7;
    background: rgba(255, 255, 255, 0.6);
}

.lesson-card:not(.locked):hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.06);
}

.lesson-card.active:hover {
    border-color: #df4a7d;
}

/* Status Icon Circles */

.status-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.status-icon.completed {
    background: #dcfce7;
    color: #10b981;
}

.status-icon.active {
    background: #dcfce7;
    color: #10b981;
}

.status-icon.locked {
    background: #f3f4f6;
    color: #9ca3af;
}

.lesson-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
}

.lesson-meta {
    display: flex;
    align-items: center;
    gap: 10px;
}

.lesson-index {
    font-size: 0.8rem;
    font-weight: 800;
    color: #6b7280;
}

.lesson-type-badge {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 6px;
    background: #f3f4f6;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}

.lesson-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #111827;
    margin: 0;
}

.lesson-desc {
    font-size: 0.9rem;
    color: #6b7280;
    margin: 0;
    font-weight: 500;
}

/* Action Buttons */

.lesson-btn {
    padding: 0.6rem 1.5rem;
    border-radius: 99px;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    border: 1.5px solid transparent;
    transition: all 0.2s ease;
    white-space: nowrap;
    font-family: inherit;
}

.lesson-btn.completed,
.lesson-btn.active {
    background: transparent;
    color: #6b7280;
    border-color: #d1d5db;
}

.lesson-btn.completed:hover,
.lesson-btn.active:hover {
    border-color: #9ca3af;
    color: #374151;
    background: #f9fafb;
}

.lesson-btn.locked {
    background: transparent;
    color: #d1d5db;
    border-color: #e5e7eb;
    cursor: not-allowed;
}

/* loading */

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 60vh;
    gap: 1rem;
    color: #6b7280;
    font-weight: 600;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #fce4ec;
    border-top-color: #df4a7d;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    100% {
        transform: rotate(360deg);
    }
}

/* responsive */

@media (max-width: 1024px) {
    .hero-section {
        flex-direction: column;
        align-items: flex-start;
    }
}

@media (max-width: 768px) {
    .layout-wrapper {
        flex-direction: column;
        padding: 1rem;
        gap: 1rem;
    }
    .sidebar {
        width: 100%;
        height: auto;
        position: static;
        border-radius: 20px;
    }
    .lesson-card {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }
    .status-icon {
        margin: 0 auto;
    }
    .lesson-meta {
        justify-content: center;
    }
    .lesson-btn {
        width: 100%;
    }
}
</style>