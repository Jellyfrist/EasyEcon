<template>
    <div class="layout-wrapper">
    
        <aside class="sidebar" v-if="dashboardData">
            <div class="sidebar-header">
                <button class="back-btn" @click="router.push(`/student/courses/${courseId}`)">
              <span class="material-symbols-outlined">arrow_back</span> Back to Modules
            </button>
            </div>
    
            <div class="module-info">
                <p class="module-subtitle">ALL CHAPTERS</p>
                <h3 class="module-title">{{ dashboardData.module.title }}</h3>
                <div class="progress-bar-container">
                    <div class="progress-fill" style="width: 100%"></div>
                </div>
                <p class="progress-text">PROGRESS: 100%</p>
            </div>
    
            <div class="lesson-nav">
                <p class="nav-section-title">CORE CONCEPTS</p>
                <div class="nav-list">
                    <button v-for="(page, index) in dashboardData.pages" :key="page.id" class="nav-item completed">
                <span class="material-symbols-outlined nav-icon">check_circle</span>
                <span class="nav-text">{{ index + 1 }}. {{ page.title }}</span>
              </button>
                </div>
            </div>
        </aside>
    
        <main class="main-content center-content">
    
            <div v-if="isLoading" class="loading-state">
                <div class="spinner"></div>
                <p>Calculating your score...</p>
            </div>
    
            <div v-else class="result-card">
                <div class="icon-confetti">🎉</div>
                <h1>Congratulations! Module Complete</h1>
                <p>You have studied all lessons and completed the quizzes in this module.</p>
    
                <div class="score-circle">
                    <div class="circle-chart" :style="{ background: `conic-gradient(#10b981 ${accuracy}%, #e2e8f0 0)` }">
                        <div class="circle-inner">
                            <h1 class="score-text">{{ totalScore }}/{{ maxScore }}</h1>
                            <span class="score-label">TOTAL SCORE</span>
                        </div>
                    </div>
                </div>
    
                <div class="stats-row">
                    <div class="stat-box">
                        <span class="stat-title"><span class="material-symbols-outlined text-sm">schedule</span> Time Spent</span>
                        <strong class="stat-value">{{ formattedTime }}</strong>
                    </div>
                    <div class="stat-box">
                        <span class="stat-title"><span class="material-symbols-outlined text-sm">ads_click</span> Accuracy</span>
                        <strong class="stat-value">{{ accuracy }}%</strong>
                    </div>
                </div>
    
                <div class="action-buttons">
                    <button @click="goToNextModule" class="btn-primary">
                Go to Next Module <span class="material-symbols-outlined ml-1">arrow_forward</span>
              </button>
                    <button @click="reviewLessons" class="btn-outline">
                Review This Module
              </button>
                </div>
            </div>
    
        </main>
    
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import learningService from '@/services/learningService';
import { useLearningStore } from '@/store/learningStore';

const route = useRoute();
const router = useRouter();
const learningStore = useLearningStore();

const courseId = computed(() => route.params.courseId);
const moduleId = computed(() => route.params.moduleId);

const dashboardData = ref(null);
const isLoading = ref(true);

const totalScore = ref(0);
const maxScore = ref(0);
const accuracy = ref(0);

const rawTimeSeconds = ref(0);
const formattedTime = computed(() => {
    const m = Math.floor(rawTimeSeconds.value / 60).toString().padStart(2, '0');
    const s = (rawTimeSeconds.value % 60).toString().padStart(2, '0');
    return `${m}:${s} min`;
});

onMounted(async () => {
    isLoading.value = true;

    if (route.query.time) {
        rawTimeSeconds.value = parseInt(route.query.time, 10);
    } else {
        rawTimeSeconds.value = 1245;
    }

    try {
        const res = await learningStore.fetchModuleDashboard(moduleId.value);
        if (res && res.chapterInfo) {
            dashboardData.value = {
                module: { title: res.chapterInfo.title },
                pages: res.lessons
            };

            let tempScore = 0;
            let tempMax = 0;

            for (const lesson of res.lessons) {
                try {
                    const quizRes = await learningService.getMyQuizResult(lesson.id);
                    if (quizRes.data && quizRes.data.total_points > 0) {
                        tempScore += quizRes.data.score || 0;
                        tempMax += quizRes.data.total_points;
                    }
                } catch (e) {}
            }

            if (tempMax === 0) {
                totalScore.value = 10;
                maxScore.value = 10;
                accuracy.value = 100;
            } else {
                totalScore.value = tempScore;
                maxScore.value = tempMax;
                accuracy.value = Math.round((tempScore / tempMax) * 100);
            }
        }
    } catch (error) {
        console.error("Failed to load summary data:", error);
    } finally {
        isLoading.value = false;
    }
});

const goToNextModule = async () => {
    await learningStore.fetchModules(courseId.value);
    const modules = learningStore.modules;

    const currentIndex = modules.findIndex(m => m.id == moduleId.value);

    if (currentIndex !== -1 && currentIndex < modules.length - 1) {
        const nextModuleId = modules[currentIndex + 1].id;
        router.push(`/courses/${courseId.value}/modules/${nextModuleId}`);
    } else {
        alert("Congratulations! You have completed all modules in this course.");
        router.push(`/courses/${courseId.value}/modules`);
    }
};

const reviewLessons = () => {
    router.push(`/courses/${courseId.value}/modules/modules/${moduleId.value}`);
};
</script>

<style scoped>
/* ================= Base Layout ================= */

.layout-wrapper {
    display: flex;
    height: 100vh;
    background-color: #f8fafc;
    font-family: 'Sarabun', 'Inter', sans-serif;
    overflow: hidden;
}

.material-symbols-outlined {
    vertical-align: middle;
}

/* ================= SIDEBAR ================= */

.sidebar {
    width: 300px;
    background-color: white;
    border-right: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    overflow-y: auto;
}

.sidebar-header {
    padding: 1.5rem;
}

.back-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background: transparent;
    border: none;
    color: #64748b;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    padding: 0;
    transition: color 0.2s;
}

.back-btn:hover {
    color: #0f172a;
}

.module-info {
    padding: 0 1.5rem 1.5rem;
    border-bottom: 1px solid #e2e8f0;
}

.module-subtitle {
    font-size: 0.75rem;
    font-weight: 800;
    color: #94a3b8;
    letter-spacing: 0.5px;
    margin: 0 0 6px 0;
}

.module-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0 0 1rem 0;
    line-height: 1.4;
}

.progress-bar-container {
    height: 4px;
    background-color: #e2e8f0;
    border-radius: 4px;
    margin-bottom: 8px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background-color: #10b981;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.progress-text {
    font-size: 0.7rem;
    font-weight: 800;
    color: #10b981;
    text-align: right;
    margin: 0;
}

.lesson-nav {
    padding: 1.5rem 0;
}

.nav-section-title {
    font-size: 0.75rem;
    font-weight: 800;
    color: #94a3b8;
    letter-spacing: 0.5px;
    margin: 0 1.5rem 12px;
}

.nav-list {
    display: flex;
    flex-direction: column;
}

.nav-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 1.5rem;
    background: transparent;
    border: none;
    text-align: left;
    color: #64748b;
}

.nav-item.completed {
    color: #0f172a;
}

.nav-item.completed .nav-icon {
    color: #10b981;
}

.nav-icon {
    font-size: 20px;
    flex-shrink: 0;
    margin-top: 2px;
}

.nav-text {
    font-size: 0.9rem;
    font-weight: 600;
    line-height: 1.4;
}

/* ================= MAIN CONTENT ================= */

.main-content {
    flex: 1;
    overflow-y: auto;
    background-color: #f8fafc;
}

.center-content {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
}

/* Card */

.result-card {
    background: white;
    padding: 3.5rem 3rem;
    border-radius: 24px;
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.05);
    text-align: center;
    max-width: 500px;
    width: 100%;
    border: 1px solid #f1f5f9;
    animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.icon-confetti {
    font-size: 4rem;
    margin-bottom: 1rem;
    animation: pop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    display: inline-block;
    background: #fffbeb;
    padding: 1rem;
    border-radius: 50%;
}

@keyframes pop {
    0% {
        transform: scale(0);
    }
    100% {
        transform: scale(1);
    }
}

.result-card h1 {
    color: #0f172a;
    margin-bottom: 0.5rem;
    font-size: 1.8rem;
    font-weight: 800;
}

.result-card p {
    color: #64748b;
    font-size: 1rem;
    margin-bottom: 2.5rem;
}

/* Score Circle */

.score-circle {
    display: flex;
    justify-content: center;
    margin: 2rem 0 3rem 0;
}

.circle-chart {
    width: 180px;
    height: 180px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 1s ease-out;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
}

.circle-inner {
    width: 144px;
    height: 144px;
    background: white;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.03);
}

.score-text {
    color: #10b981 !important;
    font-size: 3.2rem !important;
    margin: 0 !important;
    font-weight: 900 !important;
    line-height: 1;
    letter-spacing: -1px;
}

.score-label {
    color: #94a3b8;
    font-size: 0.75rem;
    margin-top: 8px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Stats Row */

.stats-row {
    display: flex;
    gap: 15px;
    margin-bottom: 2.5rem;
}

.stat-box {
    flex: 1;
    background: #f8fafc;
    padding: 1.25rem;
    border-radius: 16px;
    border: 1px solid #f1f5f9;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}

.stat-title {
    color: #64748b;
    font-size: 0.8rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stat-value {
    font-size: 1.4rem;
    color: #0f172a;
    font-weight: 800;
}

/* Buttons */

.action-buttons {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.btn-primary {
    width: 100%;
    background: #10b981;
    color: white;
    padding: 14px;
    border: none;
    border-radius: 99px;
    font-size: 1.05rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-primary:hover {
    background: #059669;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35);
}

.btn-outline {
    width: 100%;
    background: white;
    color: #64748b;
    padding: 14px;
    border: 2px solid #e2e8f0;
    border-radius: 99px;
    font-size: 1.05rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-outline:hover {
    background: #f8fafc;
    color: #0f172a;
    border-color: #cbd5e1;
}

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: #64748b;
    font-weight: 700;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f1f5f9;
    border-top-color: #10b981;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    100% {
        transform: rotate(360deg);
    }
}

@media (max-width: 768px) {
    .layout-wrapper {
        flex-direction: column;
        overflow: auto;
    }
    .sidebar {
        width: 100%;
        height: auto;
        flex-shrink: 0;
        border-right: none;
        border-bottom: 1px solid #e2e8f0;
    }
    .main-content {
        padding: 2rem 1.5rem;
        height: auto;
        display: block;
    }
    .result-card {
        padding: 2rem;
        margin: 0 auto;
    }
}
</style>