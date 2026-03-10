<template>
    <div class="layout-wrapper">
    
        <aside class="sidebar" v-if="dashboardData">
            <div class="sidebar-header">
                <button class="nav-btn" @click="router.push(`/courses/${courseId}/modules/${moduleId}`)">
              <div class="back-icon-circle">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="19" y1="12" x2="5" y2="12"></line>
                  <polyline points="12 19 5 12 12 5"></polyline>
                </svg>
              </div>
              <span class="nav-text">Back to Module</span>
            </button>
            </div>
    
            <div class="module-info">
                <p class="info-label">CURRENT MODULE</p>
                <h3 class="info-title">{{ dashboardData.module.title }}</h3>
                <div class="progress-bar-wrap">
                    <div class="progress-bar-fill" :style="{ width: dashboardData.progress_percent + '%' }"></div>
                </div>
                <p class="progress-pct">PROGRESS: {{ dashboardData.progress_percent }}%</p>
            </div>
    
            <div class="lesson-nav">
                <p class="nav-label">LESSONS</p>
                <div class="nav-list">
                    <button v-for="(page, index) in dashboardData.pages" :key="page.id" class="nav-item" :class="{ active: page.id == pageId, completed: page.status === 'completed' }" @click="goToLesson(page.id)">
                <span class="material-symbols-outlined nav-icon">
                  {{ page.id == pageId ? 'radio_button_checked' : (page.status === 'completed' ? 'check_circle' : 'play_circle') }}
                </span>
                <span class="nav-item-text">{{ index + 1 }}. {{ page.title }}</span>
              </button>
                </div>
            </div>
        </aside>
    
        <main class="main-content" id="main-scroll">
    
            <div v-if="pageData" class="study-container">
    
                <div class="content-card">
                    <article class="content-article">
                        <span class="topic-tag">TOPIC {{ currentIndex + 1 }}</span>
                        <h1 class="page-title">{{ pageData.title }}</h1>
    
                        <div v-for="block in pageData.content_blocks" :key="block.id" class="content-block">
    
                            <div v-if="block.type === 'rich_text_section'" class="rich-text">
                                <div v-html="block.data.html" class="html-content"></div>
                            </div>
    
                            <div v-else-if="block.type === 'mini_quiz' && hasValidQuiz(block.data)" class="quiz-card">
    
                                <div class="quiz-header">
                                    <div class="quiz-icon-box">
                                        <span class="material-symbols-outlined">quiz</span>
                                    </div>
                                    <div>
                                        <h3 class="quiz-title">{{ block.data.title || 'Mini Quiz' }}</h3>
                                        <p class="quiz-subtitle">CHECK YOUR UNDERSTANDING</p>
                                    </div>
                                </div>
    
                                <div class="quiz-body">
                                    <div v-for="(q, qIndex) in block.data.questions" :key="q.id || qIndex" class="question-block">
                                        <p class="question-text"><strong>Q{{ qIndex + 1 }}:</strong> {{ q.text }}</p>
    
                                        <div class="options-list">
                                            <label v-for="(opt, optIndex) in q.options" :key="optIndex" class="option-label" :class="{
                              selected: studentAnswers[q.id] === optIndex && !isQuizSubmitted,
                              correct: isQuizSubmitted && optIndex === q.correct_index,
                              wrong: isQuizSubmitted && studentAnswers[q.id] === optIndex && optIndex !== q.correct_index,
                              disabled: isQuizSubmitted
                            }">
                            <input
                              type="radio"
                              :name="'quiz_' + q.id"
                              :value="optIndex"
                              v-model="studentAnswers[q.id]"
                              :disabled="isQuizSubmitted"
                            >
                            <span class="option-text">{{ opt }}</span>
                            <span v-if="isQuizSubmitted && optIndex === q.correct_index" class="material-symbols-outlined icon-check">check_circle</span>
                            <span v-if="isQuizSubmitted && studentAnswers[q.id] === optIndex && optIndex !== q.correct_index" class="material-symbols-outlined icon-wrong">cancel</span>
                          </label>
                                        </div>
    
                                        <div v-if="isQuizSubmitted && q.explanation" class="explanation-box">
                                            <strong>Explanation:</strong> {{ q.explanation }}
                                        </div>
                                    </div>
    
                                    <div class="quiz-footer">
                                        <p v-if="isQuizSubmitted" class="feedback-text" :class="calculateScore(block.data.questions) === block.data.questions.length ? 'text-green' : 'text-amber'">
                                            {{ calculateScore(block.data.questions) === block.data.questions.length ? 'Perfect score!' : `Score: ${calculateScore(block.data.questions)} / ${block.data.questions.length}` }}
                                        </p>
                                        <p v-else class="feedback-text text-muted">Please select an answer for every question.</p>
    
                                        <button @click="submitQuiz(block.data.questions)" class="submit-btn" :disabled="isQuizSubmitted || Object.keys(studentAnswers).length !== block.data.questions.length">
                          {{ isQuizSubmitted ? 'Submitted' : 'Submit Answer' }}
                        </button>
                                    </div>
    
                                </div>
                            </div>
    
                        </div>
                    </article>
    
                    <footer class="bottom-nav">
                        <button class="prev-btn" :class="{ invisible: currentIndex === 0 }" @click="goPrevLesson">
                  <span class="material-symbols-outlined">chevron_left</span> Previous
                </button>
    
                        <div class="pagination-dots">
                            <span v-for="(p, i) in dashboardData?.pages" :key="i" class="dot" :class="{ active: i === currentIndex }"></span>
                        </div>
    
                        <button @click="handleNext" class="next-btn">
                  {{ isLastPage ? 'Finish Module' : 'Next Lesson' }}
                  <span class="material-symbols-outlined">chevron_right</span>
                </button>
                    </footer>
                </div>
    
            </div>
    
            <div v-else class="loading-state">
                <div class="spinner"></div>
                <p>Preparing lesson...</p>
            </div>
    
        </main>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import learningService from '@/services/learningService';
import { useLearningStore } from '@/store/learningStore';

const route = useRoute();
const router = useRouter();
const learningStore = useLearningStore();

const courseId = computed(() => route.params.courseId);
const moduleId = computed(() => route.params.moduleId);
const pageId = computed(() => route.params.pageId);

const pageData = ref(null);
const dashboardData = ref(null);
const timeSpent = ref(0);
let timer = null;

/* mini quiz state */
const studentAnswers = ref({});
const isQuizSubmitted = ref(false);

const hasValidQuiz = (data) => {
    if (!data) return false;
    if (data.questions && Array.isArray(data.questions)) return data.questions.length > 0;
    return false;
};

const calculateScore = (questions) => {
    let score = 0;
    questions.forEach(q => {
        if (studentAnswers.value[q.id] === q.correct_index) score++;
    });
    return score;
};

const currentIndex = computed(() => {
    if (!dashboardData.value || !dashboardData.value.pages) return 0;
    return dashboardData.value.pages.findIndex(p => p.id == pageId.value);
});

const isLastPage = computed(() => {
    if (!dashboardData.value || !dashboardData.value.pages) return true;
    return currentIndex.value >= dashboardData.value.pages.length - 1;
});

const loadSidebarData = async () => {
    try {
        const res = await learningStore.fetchModuleDashboard(moduleId.value);
        if (res && res.chapterInfo) {
            dashboardData.value = {
                module: { title: res.chapterInfo.title },
                progress_percent: res.chapterInfo.progressPercent,
                pages: res.lessons
            };
        }
    } catch (error) {
        console.error("Sidebar Load Error:", error);
    }
};

const loadLesson = async (pId) => {
    pageData.value = null;
    studentAnswers.value = {};
    isQuizSubmitted.value = false;

    try {
        const res = await learningService.studyPage(pId);
        pageData.value = res.data;

        try {
            const quizRes = await learningService.getMyQuizResult(pId);
            if (quizRes && quizRes.data && quizRes.data.answers) {
                studentAnswers.value = quizRes.data.answers;
                isQuizSubmitted.value = true;
            }
        } catch (e) {
            console.log("No previous quiz data for this page.");
        }

        timeSpent.value = 0;
        if (timer) clearInterval(timer);
        timer = setInterval(() => { timeSpent.value += 1; }, 1000);

        const mainScroll = document.getElementById('main-scroll');
        if (mainScroll) mainScroll.scrollTop = 0;

    } catch (err) {
        console.error("Failed to load lesson data", err);
    }
};

const submitQuiz = async (questions) => {
    isQuizSubmitted.value = true;
    try {
        await learningStore.submitMiniQuiz(pageId.value, studentAnswers.value);
        await loadSidebarData();
    } catch (error) {
        console.warn("Failed to save quiz result:", error);
    }
};

onMounted(async () => {
    await loadSidebarData();
    if (pageId.value) {
        loadLesson(pageId.value);
    }
});

onUnmounted(() => {
    if (timer) clearInterval(timer);
});

watch(pageId, async (newId) => {
    if (newId) {
        loadLesson(newId);
        await loadSidebarData();
    }
});

const goToLesson = (pId) => {
    if (pId == pageId.value) return;
    router.push({
        name: 'LearningChapter',
        params: {
            courseId: courseId.value,
            moduleId: moduleId.value,
            pageId: pId
        }
    });
};

const goPrevLesson = () => {
    if (currentIndex.value > 0) {
        const prevId = dashboardData.value.pages[currentIndex.value - 1].id;
        goToLesson(prevId);
    }
};

const handleNext = async () => {
    try {
        try {
            await learningStore.completePage(pageId.value);
        } catch (apiErr) {}

        if (!isLastPage.value) {
            const nextId = dashboardData.value.pages[currentIndex.value + 1].id;
            goToLesson(nextId);
        } else {
            router.push(`/student/courses/${courseId.value}/modules/${moduleId.value}?completed=true&time=${timeSpent.value}`);
        }
    } catch (err) {
        console.error(err);
    }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap');
/* =====================================================
   Layout Wrapper
   ===================================================== */

.layout-wrapper {
    display: flex;
    height: 100vh;
    background: linear-gradient(90deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
    font-family: 'DM Sans', 'Sarabun', sans-serif;
    overflow: hidden;
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
    box-shadow: 0 10px 30px rgba(223, 74, 125, 0.1);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    overflow-y: auto;
    height: 100%;
}

.sidebar-header {
    padding: 2rem 1.5rem 1rem 1.5rem;
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
    color: rgba(255, 255, 255, 0.8);
}

.nav-btn:hover .nav-text {
    color: #e6e6e6;
}

.module-info {
    padding: 1rem 1.5rem 1.5rem 1.5rem;
    border-bottom: 1px solid #fce4ec;
}

.info-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: #e6e6e6;
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
    background: #fce4ec;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #ffc6da, #ffffff);
    border-radius: 6px;
    transition: width 0.4s ease;
}

.progress-pct {
    font-size: 0.7rem;
    font-weight: 800;
    color: #e6e6e6;
    text-align: right;
    margin: 0;
    letter-spacing: 0.05em;
}

.lesson-nav {
    padding: 1.5rem 1rem;
    flex: 1;
}

.nav-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: #e6e6e6;
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
    background: transparent;
    border-radius: 12px;
    border: 1px solid transparent;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s ease;
    color: #ffffff;
    font-family: inherit;
}

.nav-item:hover:not(.active) {
    background: rgba(255, 255, 255, 0.1);
    transform: translateX(2px);
}

.nav-item.active {
    background: rgba(255, 255, 255, 0.2);
    /* color: #1f2937; */
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-shadow: 0 4px 12px rgba(223, 74, 125, 0.08);
}

.nav-item.completed .nav-icon {
    color: #00ffaa;
}

.nav-item.active .nav-icon {
    color: #ff006a;
}

.nav-icon {
    font-size: 20px;
    flex-shrink: 0;
    color: #9ca3af;
}

.nav-item-text {
    font-size: 0.9rem;
    font-weight: 700;
    line-height: 1.4;
}

/* Custom Scrollbar for Sidebar */

.sidebar::-webkit-scrollbar {
    width: 4px;
}

.sidebar::-webkit-scrollbar-thumb {
    background-color: #f1c3d3;
    border-radius: 4px;
}

.sidebar::-webkit-scrollbar-track {
    background-color: transparent;
}

/* =====================================================
   Main Content
   ===================================================== */

.main-content {
    flex: 1;
    overflow-y: auto;
    scroll-behavior: smooth;
    border-radius: 24px;
}

.main-content::-webkit-scrollbar {
    width: 6px;
}

.main-content::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
}

.study-container {
    max-width: 860px;
    margin: 0 auto;
}

/* White Content Card */

.content-card {
    background: #ffffff;
    border-radius: 24px;
    padding: 3.5rem 4rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
    min-height: 100%;
    box-sizing: border-box;
}

/* article */

.topic-tag {
    display: inline-block;
    background: #fce4ec;
    color: #df4a7d;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    padding: 6px 14px;
    border-radius: 99px;
    margin-bottom: 1.25rem;
}

.page-title {
    font-size: 2.2rem;
    font-weight: 900;
    color: #111827;
    margin: 0 0 2rem;
    line-height: 1.3;
    letter-spacing: -0.02em;
    border-bottom: 2px dashed #f3f4f6;
    padding-bottom: 1.5rem;
}

.content-block {
    margin-bottom: 2.5rem;
}

/* rich text */

.html-content :deep(h1) {
    font-size: 1.8rem;
    font-weight: 800;
    margin: 2rem 0 1rem;
    color: #111827;
}

.html-content :deep(h2) {
    font-size: 1.4rem;
    font-weight: 800;
    margin: 1.5rem 0 0.75rem;
    color: #111827;
}

.html-content :deep(p) {
    line-height: 1.8;
    color: #4b5563;
    margin-bottom: 1.2rem;
    font-size: 1.05rem;
}

.html-content :deep(ul),
.html-content :deep(ol) {
    padding-left: 1.5rem;
    margin-bottom: 1.2rem;
    color: #4b5563;
    line-height: 1.8;
    font-size: 1.05rem;
}

.html-content :deep(img) {
    max-width: 100%;
    height: auto;
    border-radius: 16px;
    margin: 2rem 0;
    box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.1);
}

/* =====================================================
   Quiz Card
   ===================================================== */

.quiz-card {
    background: #ffffff;
    border: 1.5px solid #fce4ec;
    border-radius: 20px;
    padding: 2.5rem;
    margin-top: 3rem;
    box-shadow: 0 8px 24px rgba(223, 74, 125, 0.06);
}

.quiz-header {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #f3f4f6;
}

.quiz-icon-box {
    width: 56px;
    height: 56px;
    background: #fce4ec;
    color: #df4a7d;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.quiz-icon-box .material-symbols-outlined {
    font-size: 30px;
}

.quiz-title {
    margin: 0 0 6px;
    font-size: 1.3rem;
    font-weight: 800;
    color: #111827;
}

.quiz-subtitle {
    margin: 0;
    font-size: 0.75rem;
    font-weight: 800;
    color: #9ca3af;
    letter-spacing: 0.08em;
}

/* questions */

.question-block {
    margin-bottom: 2.5rem;
}

.question-text {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 1.25rem;
    line-height: 1.6;
}

.options-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.option-label {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 20px;
    border: 1.5px solid #e5e7eb;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.2s ease;
    background: white;
}

.option-label:hover:not(.disabled) {
    border-color: #ffc7db;
    background: #fffafb;
    transform: translateX(4px);
}

.option-label.selected {
    border-color: #df4a7d;
    background: #fff0f5;
    box-shadow: 0 4px 12px rgba(223, 74, 125, 0.1);
}

.option-label.correct {
    border-color: #10b981;
    background: #dcfce7;
    color: #065f46;
    font-weight: 700;
}

.option-label.wrong {
    border-color: #ef4444;
    background: #fee2e2;
    color: #991b1b;
}

.option-label.disabled {
    cursor: default;
}

.option-text {
    flex: 1;
    font-size: 1.05rem;
}

.icon-check {
    color: #10b981;
    font-size: 24px;
}

.icon-wrong {
    color: #ef4444;
    font-size: 24px;
}

input[type="radio"] {
    width: 20px;
    height: 20px;
    accent-color: #df4a7d;
    cursor: pointer;
    flex-shrink: 0;
}

.disabled input[type="radio"] {
    cursor: default;
}

/* explanation */

.explanation-box {
    margin-top: 16px;
    padding: 16px 20px;
    background: #dcfce7;
    border-left: 4px solid #10b981;
    border-radius: 0 12px 12px 0;
    font-size: 0.95rem;
    color: #065f46;
    line-height: 1.6;
    animation: slideDown 0.25s ease-out;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-6px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* quiz footer */

.quiz-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #f3f4f6;
    gap: 1rem;
}

.feedback-text {
    font-size: 1.05rem;
    font-weight: 800;
    margin: 0;
}

.text-muted {
    color: #9ca3af;
}

.text-green {
    color: #10b981;
}

.text-amber {
    color: #f59e0b;
}

.submit-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #df4a7d 0%, #c83264 100%);
    color: white;
    border: none;
    padding: 14px 28px;
    border-radius: 99px;
    font-weight: 800;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(223, 74, 125, 0.25);
    font-family: inherit;
}

.submit-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(223, 74, 125, 0.35);
}

.submit-btn:disabled {
    background: #d1d5db;
    box-shadow: none;
    cursor: not-allowed;
    transform: none;
}

/* =====================================================
   Bottom Navigation
   ===================================================== */

.bottom-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 4rem;
    padding-top: 2rem;
    border-top: 2px dashed #f3f4f6;
}

.invisible {
    visibility: hidden;
}

.prev-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: white;
    border: 1.5px solid #e5e7eb;
    color: #4b5563;
    padding: 12px 24px;
    border-radius: 99px;
    font-weight: 700;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: inherit;
}

.prev-btn:hover {
    background: #f9fafb;
    color: #111827;
    border-color: #9ca3af;
}

.pagination-dots {
    display: flex;
    gap: 6px;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #e5e7eb;
    transition: all 0.3s;
}

.dot.active {
    width: 24px;
    border-radius: 4px;
    background: #df4a7d;
}

.next-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: #df4a7d;
    color: white;
    border: none;
    padding: 12px 26px;
    border-radius: 99px;
    font-weight: 700;
    font-size: 0.95rem;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(223, 74, 125, 0.25);
    transition: all 0.2s ease;
    font-family: inherit;
}

.next-btn:hover {
    background: #c83264;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(223, 74, 125, 0.35);
}

/* loading */

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 1rem;
    color: #9ca3af;
    font-weight: 600;
}

.spinner {
    width: 44px;
    height: 44px;
    border: 4px solid #fce4ec;
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
    .content-card {
        padding: 2.5rem 2rem;
    }
}

@media (max-width: 768px) {
    .layout-wrapper {
        flex-direction: column;
        padding: 1rem;
        gap: 1rem;
        overflow: auto;
        height: auto;
    }
    .sidebar {
        width: 100%;
        height: auto;
        position: static;
        border-radius: 20px;
    }
    .main-content {
        overflow: visible;
    }
    .content-card {
        padding: 2rem 1.5rem;
        border-radius: 20px;
    }
    .quiz-card {
        padding: 1.5rem;
    }
    .bottom-nav {
        flex-direction: column-reverse;
        gap: 1.5rem;
    }
    .prev-btn,
    .next-btn {
        width: 100%;
        justify-content: center;
    }
    .quiz-footer {
        flex-direction: column;
        align-items: stretch;
    }
    .submit-btn {
        width: 100%;
        justify-content: center;
    }
}
</style>