<template>
    <div class="layout-wrapper" :style="{ '--navbar-offset': `${navbarOffset}px` }">
        <button class="outline-toggle" :aria-expanded="showOutline" aria-controls="lesson-outline" @click="showOutline = !showOutline">
            <span class="material-symbols-outlined" aria-hidden="true">menu_book</span> Lessons
            <span class="material-symbols-outlined" aria-hidden="true">{{ showOutline ? 'close' : 'expand_more' }}</span>
        </button>
    
        <LearningLessonSidebar v-if="dashboardData" id="lesson-outline" reader :class="{ 'outline-open': showOutline }"
            :dashboard="dashboardData" :page-id="pageId"
            @back="router.push({ name: 'ModulesList', params: { courseId } })"
            @select="goToLesson" />
    
        <main class="main-content" id="main-scroll">
    
            <div v-if="pageData" class="study-container">
    
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

            </div>
    
            <div v-else-if="dashboardData && dashboardData.pages.length === 0" class="loading-state">
                <span class="material-symbols-outlined" aria-hidden="true">menu_book</span>
                <p>No published lessons in this module yet.</p>
                <router-link :to="{ name: 'ModulesList', params: { courseId } }">Back to modules</router-link>
            </div>
            <div v-else class="loading-state">
                <div class="spinner"></div>
                <p>Preparing lesson...</p>
            </div>
    
        </main>
        <footer v-if="pageData" class="bottom-nav" aria-label="Lesson navigation">
            <button class="prev-btn" :class="{ invisible: currentIndex === 0 }" @click="goPrevLesson">
                <span class="material-symbols-outlined" aria-hidden="true">chevron_left</span> Previous
            </button>
            <span class="lesson-position">{{ currentIndex + 1 }} / {{ dashboardData?.pages.length || 0 }}</span>
            <button @click="handleNext" class="next-btn">
                {{ isLastPage ? 'Finish Module' : 'Next Lesson' }}
                <span class="material-symbols-outlined" aria-hidden="true">chevron_right</span>
            </button>
        </footer>
    </div>
</template>

<script setup>
import { useNavbarOffset } from '@/composables/useNavbarOffset';
import LearningLessonSidebar from '@/components/LearningLessonSidebar.vue';
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import learningService from '@/services/learningService';
import { useLearningStore } from '@/store/learningStore';

const route = useRoute();
const router = useRouter();
const learningStore = useLearningStore();
const navbarOffset = useNavbarOffset();
const showOutline = ref(false);

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

const openModule = async () => {
    pageData.value = null;
    if (timer) clearInterval(timer);
    await loadSidebarData();
    if (pageId.value) {
        await loadLesson(pageId.value);
    } else {
        const firstPage = dashboardData.value?.pages.find(page => page.status !== 'locked');
        if (firstPage) {
            router.replace({ name: 'LearningChapter', params: {
                courseId: courseId.value, moduleId: moduleId.value, pageId: firstPage.id,
            } });
        }
    }
};

onMounted(openModule);

onUnmounted(() => {
    if (timer) clearInterval(timer);
});

watch([moduleId, pageId], openModule);

const goToLesson = (pId) => {
    showOutline.value = false;
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
    position: fixed;
    inset: var(--navbar-offset, 64px) 0 0;
    display: grid;
    grid-template-columns: 260px minmax(0, 1fr);
    grid-template-rows: minmax(0, 1fr) 60px;
    background: white;
    font-family: 'DM Sans', 'Sarabun', sans-serif;
    overflow: hidden;
}
.material-symbols-outlined { vertical-align: middle; }
.outline-toggle { display: none; }
.main-content {
    grid-column: 2;
    grid-row: 1;
    min-width: 0;
    overflow-y: auto;
    scroll-behavior: smooth;
}
.study-container {
    width: min(100%, 800px);
    margin: 0 auto;
    padding: 36px 48px 64px;
}
.topic-tag {
    display: block;
    color: var(--primary-pink);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
}
.page-title {
    font-size: 1.8rem;
    font-weight: 600;
    color: var(--text-main);
    margin: 0 0 28px;
    line-height: 1.4;
    overflow-wrap: anywhere;
}
.content-block { margin-bottom: 32px; }
.html-content { overflow-wrap: anywhere; }
.html-content :deep(table) { display: block; max-width: 100%; overflow-x: auto; }
.html-content :deep(iframe) { max-width: 100%; }
.html-content :deep(blockquote) {
    border-left: 2px solid var(--primary-pink);
    padding-left: 16px;
    margin: 24px 0;
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
    white-space: pre-wrap;
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
    white-space: pre-wrap;
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
    grid-column: 1 / -1;
    grid-row: 2;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 8px 20px;
    border-top: 1px solid var(--card-border);
    background: white;
    z-index: 2;
}
.invisible { visibility: hidden; }
.prev-btn, .next-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    min-height: 44px;
    padding: 8px 14px;
    border: 0;
    border-radius: 8px;
    font-family: inherit;
    font-size: 0.85rem;
    cursor: pointer;
}
.prev-btn { background: white; color: var(--primary-pink); }
.prev-btn:hover { background: #fff0f5; }
.next-btn { background: var(--primary-pink); color: white; }
.next-btn:hover { background: #c83264; }
.lesson-position { font-size: 0.8rem; color: var(--text-muted); }
.prev-btn:focus-visible, .next-btn:focus-visible, .outline-toggle:focus-visible {
    outline: 2px solid var(--primary-pink);
    outline-offset: 2px;
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
@media (max-width: 768px) {
    .layout-wrapper {
        grid-template-columns: minmax(0, 1fr);
        grid-template-rows: 48px minmax(0, 1fr) 60px;
    }
    .outline-toggle {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0 20px;
        border: 0;
        border-bottom: 1px solid var(--card-border);
        background: white;
        color: var(--primary-pink);
        font: inherit;
        cursor: pointer;
    }
    .outline-toggle span:last-child { margin-left: auto; }
    .layout-wrapper > .sidebar {
        display: none;
        position: absolute;
        top: 48px;
        bottom: 60px;
        left: 0;
        width: min(320px, 90%);
        height: auto;
        z-index: 3;
        box-shadow: 8px 0 24px rgba(0, 0, 0, 0.08);
    }
    .layout-wrapper > .sidebar.outline-open { display: flex; }
    .main-content { grid-column: 1; grid-row: 2; }
    .bottom-nav { grid-row: 3; padding-inline: 12px; }
    .study-container { padding: 24px 20px 40px; }
    .page-title { font-size: 1.5rem; }
    .quiz-card { padding: 20px; }
    .quiz-footer { flex-direction: column; align-items: stretch; }
    .submit-btn { width: 100%; justify-content: center; }
}
@media (prefers-reduced-motion: reduce) {
    .main-content { scroll-behavior: auto; }
}
</style>
