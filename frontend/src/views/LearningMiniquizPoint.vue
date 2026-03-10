<template>
    <div class="layout-wrapper">
    
        <aside class="sidebar" v-if="dashboardData">
            <div class="sidebar-header">
                <button class="nav-btn" @click="router.push(`/courses/${courseId}/modules`)">
              <div class="back-icon-circle">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="19" y1="12" x2="5" y2="12"></line>
                  <polyline points="12 19 5 12 12 5"></polyline>
                </svg>
              </div>
              <span class="nav-text">Back to Modules</span>
            </button>
            </div>
    
            <div class="module-info">
                <p class="info-label">MODULE COMPLETE</p>
                <h3 class="info-title">{{ dashboardData.module.title }}</h3>
                <div class="progress-bar-wrap">
                    <div class="progress-bar-fill" style="width: 100%"></div>
                </div>
                <p class="progress-pct">PROGRESS: 100%</p>
            </div>
    
            <div class="lesson-nav">
                <p class="nav-label">LESSONS</p>
                <div class="nav-list">
                    <button v-for="(page, index) in dashboardData.pages" :key="page.id" class="nav-item">
                <span class="material-symbols-outlined nav-icon">check_circle</span>
                <span class="nav-item-text">{{ index + 1 }}. {{ page.title }}</span>
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
                <h1 class="result-title">Module Complete!</h1>
                <p class="result-desc">You have successfully studied all lessons and completed the quizzes in this module.</p>
    
                <!-- <div class="score-circle">
              <div class="circle-chart" :style="{ background: `conic-gradient(#df4a7d ${accuracy}%, #fce4ec 0)` }">
                <div class="circle-inner">
                  <h1 class="score-text">{{ totalScore }}/{{ maxScore }}</h1>
                  <span class="score-label">TOTAL SCORE</span>
                </div>
              </div>
            </div> -->
    
                <div class="stats-row">
                    <div class="stat-box">
                        <span class="stat-title"><span class="material-symbols-outlined text-sm">schedule</span> Time Spent</span>
                        <strong class="stat-value">{{ formattedTime }}</strong>
                    </div>
                    <!-- <div class="stat-box">
                <span class="stat-title"><span class="material-symbols-outlined text-sm">ads_click</span> Accuracy</span>
                <strong class="stat-value">{{ accuracy }}%</strong>
              </div> -->
                </div>
    
                <div class="action-buttons">
                    <!-- <button @click="goToNextModule" class="btn-primary"> -->
                    <template v-if="hasNextModule">
                        <button @click="goToNextModule" class="btn-primary">
                            Go to Next Module 
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                            <polyline points="12 5 19 12 12 19"></polyline>
                            </svg>
                        </button>
</template>

<template v-else>
    <button @click="goToLearningModule" class="btn-primary">
                            Back to Learning Modules 
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                            <polyline points="9 22 9 12 15 12 15 22"></polyline>
                            </svg>
                        </button>
</template>
            <!-- </button> -->
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

    rawTimeSeconds.value = route.query.time ? parseInt(route.query.time, 10) : 0;

    totalScore.value = 0;
    maxScore.value = 0;
    accuracy.value = 0;

    try {
        const [resDashboard, resModules] = await Promise.all([
            learningStore.fetchModuleDashboard(moduleId.value),
            learningStore.fetchModules(courseId.value)
        ]);

        if (resDashboard && resDashboard.lessons) {
            dashboardData.value = {
                module: { title: resDashboard.chapterInfo ?.title || 'Module Complete' },
                pages: resDashboard.lessons
            };

            let accumulatedScore = 0;
            let accumulatedMax = 0;

            const quizPromises = resDashboard.lessons.map(lesson =>
                learningService.getMyQuizResult(lesson.id).catch(() => null)
            );

            const quizResults = await Promise.all(quizPromises);

            quizResults.forEach((quizRes) => {
                const result = quizRes ?.data || quizRes;

                if (result && result.total_points > 0) {
                    accumulatedScore += Number(result.score || 0);
                    accumulatedMax += Number(result.total_points || 0);
                }
            });

            totalScore.value = accumulatedScore;
            maxScore.value = accumulatedMax;

            if (accumulatedMax > 0) {
                accuracy.value = Math.round((accumulatedScore / accumulatedMax) * 100);
            } else {
                accuracy.value = 100;
            }
        }
    } catch (error) {
        console.error("Calculation Error:", error);
    } finally {
        isLoading.value = false;
    }
});

const hasNextModule = computed(() => {
    const modules = learningStore.modules;
    if (!modules || modules.length === 0) return false;

    const currentIndex = modules.findIndex(m => m.id == moduleId.value);
    return currentIndex !== -1 && currentIndex < modules.length - 1;
});

const goToNextModule = () => {
    const modules = learningStore.modules;
    const currentIndex = modules.findIndex(m => m.id == moduleId.value);

    const nextModuleId = modules[currentIndex + 1].id;
    router.push(`/courses/${courseId.value}/modules/${nextModuleId}`);
};

const goToLearningModule = () => {
    router.push(`/courses/${courseId.value}/modules`);
};

const reviewLessons = () => {
    router.push(`/courses/${courseId.value}/modules/${moduleId.value}`);
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap');
/* =====================================================
   Layout Wrapper
   ===================================================== */

.layout-wrapper {
    height: calc(100vh - 64px);
    display: flex;
    background: linear-gradient(90deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
    font-family: 'DM Sans', 'Sarabun', sans-serif;
    padding: 2rem;
    gap: 2rem;
    box-sizing: border-box;
    overflow: hidden;
    align-items: stretch;
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

/* Back to Modules */

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

.module-info {
    padding: 1rem 1.5rem 1.5rem 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.info-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: rgba(255, 255, 255, 0.8);
    letter-spacing: 0.05em;
    margin: 0 0 6px;
}

.info-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 1rem;
    line-height: 1.4;
}

.progress-bar-wrap {
    height: 6px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-bar-fill {
    height: 100%;
    background: #ffffff;
    border-radius: 6px;
}

.progress-pct {
    font-size: 0.7rem;
    font-weight: 800;
    color: #ffffff;
    text-align: right;
    margin: 0;
    letter-spacing: 0.05em;
}

.lesson-nav {
    padding: 1.5rem 1rem;
    flex: 1;
    overflow-y: auto;
}

.lesson-nav::-webkit-scrollbar {
    width: 4px;
}

.lesson-nav::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
}

.nav-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: rgba(255, 255, 255, 0.8);
    letter-spacing: 0.05em;
    margin: 0 0.5rem 10px;
}

.nav-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

/* Sidebar Lesson Items */

.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 1rem 1.25rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    border: 1px solid transparent;
    text-align: left;
    color: #ffffff;
    font-family: inherit;
}

.nav-icon {
    font-size: 20px;
    flex-shrink: 0;
    color: #ffffff;
}

.nav-item-text {
    font-size: 0.9rem;
    font-weight: 700;
    line-height: 1.4;
    opacity: 0.9;
}

/* =====================================================
   Main Content Area
   ===================================================== */

.main-content {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    padding: 0;
}

.main-content::-webkit-scrollbar {
    width: 6px;
}

.main-content::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
}

.center-content {
    display: flex;
    justify-content: center;
    align-items: center;
}

/* =====================================================
   Result Card
   ===================================================== */

.result-card {
    background: #ffffff;
    padding: 3.5rem 4rem;
    border-radius: 24px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.05);
    text-align: center;
    max-width: 800px;
    width: 100%;
    margin: auto;
    animation: slideUp 0.4s ease-out;
    border: 1px solid #ffffff;
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
    font-size: 4.5rem;
    margin-bottom: 1rem;
    animation: pop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 140px;
    height: 140px;
    background: #fce4ec;
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

.result-title {
    color: #111827;
    margin-bottom: 0.75rem;
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: -0.02em;
}

.result-desc {
    color: #6b7280;
    font-size: 1.05rem;
    margin-bottom: 3rem;
    line-height: 1.6;
}

/* Score Circle */

.score-circle {
    display: flex;
    justify-content: center;
    margin: 0 0 3rem 0;
}

.circle-chart {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 1s ease-out;
    box-shadow: 0 8px 25px rgba(223, 74, 125, 0.15);
    /* เงาสีชมพู */
}

.circle-inner {
    width: 160px;
    height: 160px;
    background: white;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 4px 15px rgba(0, 0, 0, 0.02);
}

.score-text {
    color: #df4a7d !important;
    font-size: 3.5rem !important;
    margin: 0 !important;
    font-weight: 900 !important;
    line-height: 1;
    letter-spacing: -2px;
}

.score-label {
    color: #9ca3af;
    font-size: 0.8rem;
    margin-top: 8px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Stats Row */

.stats-row {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 3rem;
    justify-content: center;
}

.stat-box {
    flex: 1;
    max-width: 250px;
    background: #faf9f7;
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid #f3f4f6;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}

.stat-title {
    color: #6b7280;
    font-size: 0.85rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    gap: 6px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stat-value {
    font-size: 1.6rem;
    color: #111827;
    font-weight: 900;
}

/* Buttons */

.action-buttons {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.btn-primary {
    width: 100%;
    background: linear-gradient(135deg, #df4a7d 0%, #c83264 100%);
    color: white;
    padding: 16px;
    border: none;
    border-radius: 99px;
    font-size: 1.1rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 15px rgba(223, 74, 125, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(223, 74, 125, 0.35);
}

.btn-outline {
    width: 100%;
    background: white;
    color: #6b7280;
    padding: 16px;
    border: 2px solid #e5e7eb;
    border-radius: 99px;
    font-size: 1.1rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-outline:hover {
    background: #f9fafb;
    color: #111827;
    border-color: #d1d5db;
}

/* Loading */

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: #6b7280;
    font-weight: 700;
}

.spinner {
    width: 44px;
    height: 44px;
    border: 4px solid #fce4ec;
    border-top-color: #df4a7d;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    100% {
        transform: rotate(360deg);
    }
}

/* Responsive */

@media (max-width: 768px) {
    .layout-wrapper {
        flex-direction: column;
        overflow: auto;
        padding: 1rem;
        gap: 1rem;
    }
    .sidebar {
        width: 100%;
        height: auto;
        flex-shrink: 0;
        border-radius: 20px;
    }
    .main-content {
        height: auto;
        display: block;
        padding: 0;
    }
    .result-card {
        padding: 2.5rem 1.5rem;
        border-radius: 20px;
    }
    .circle-chart {
        width: 160px;
        height: 160px;
    }
    .circle-inner {
        width: 128px;
        height: 128px;
    }
    .score-text {
        font-size: 2.5rem !important;
    }
}
</style>