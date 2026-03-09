<template>
  <div class="layout-wrapper">

    <!-- sidebar -->
    <aside class="sidebar" v-if="dashboardData">
      <div class="sidebar-header">
        <button class="back-btn" @click="router.push(`/courses/${courseId}/modules/${moduleId}`)">
          <span class="material-symbols-outlined">arrow_back</span> Back to Module
        </button>
      </div>

      <div class="module-info">
        <p class="info-label">ALL CHAPTERS</p>
        <h3 class="info-title">{{ dashboardData.module.title }}</h3>
        <div class="progress-bar-wrap">
          <div class="progress-bar-fill" :style="{ width: dashboardData.progress_percent + '%' }"></div>
        </div>
        <p class="progress-pct">PROGRESS: {{ dashboardData.progress_percent }}%</p>
      </div>

      <div class="lesson-nav">
        <p class="nav-label">CORE CONCEPTS</p>
        <div class="nav-list">
          <button
            v-for="(page, index) in dashboardData.pages"
            :key="page.id"
            class="nav-item"
            :class="{ active: page.id == pageId, completed: page.status === 'completed' }"
            @click="goToLesson(page.id)"
          >
            <span class="material-symbols-outlined nav-icon">
              {{ page.id == pageId ? 'radio_button_checked' : (page.status === 'completed' ? 'check_circle' : 'play_circle') }}
            </span>
            <span class="nav-text">{{ index + 1 }}. {{ page.title }}</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- main content -->
    <main class="main-content" id="main-scroll">

      <div v-if="pageData" class="study-container">

        <article class="content-article">
          <span class="topic-tag">TOPIC {{ currentIndex + 1 }}</span>
          <h1 class="page-title">{{ pageData.title }}</h1>

          <div v-for="block in pageData.content_blocks" :key="block.id" class="content-block">

            <!-- rich text section -->
            <div v-if="block.type === 'rich_text_section'" class="rich-text">
              <div v-html="block.data.html" class="html-content"></div>
            </div>

            <!-- mini quiz -->
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
                    <label
                      v-for="(opt, optIndex) in q.options"
                      :key="optIndex"
                      class="option-label"
                      :class="{
                        selected: studentAnswers[q.id] === optIndex && !isQuizSubmitted,
                        correct: isQuizSubmitted && optIndex === q.correct_index,
                        wrong: isQuizSubmitted && studentAnswers[q.id] === optIndex && optIndex !== q.correct_index,
                        disabled: isQuizSubmitted
                      }"
                    >
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
                    {{ calculateScore(block.data.questions) === block.data.questions.length
                      ? 'Perfect score!'
                      : `Score: ${calculateScore(block.data.questions)} / ${block.data.questions.length}` }}
                  </p>
                  <p v-else class="feedback-text text-muted">Please select an answer for every question.</p>

                  <button
                    @click="submitQuiz(block.data.questions)"
                    class="submit-btn"
                    :disabled="isQuizSubmitted || Object.keys(studentAnswers).length !== block.data.questions.length"
                  >
                    {{ isQuizSubmitted ? 'Submitted' : 'Submit Answer' }}
                  </button>
                </div>

              </div>
            </div>

          </div>
        </article>

        <!-- bottom navigation -->
        <footer class="bottom-nav">
          <button
            class="prev-btn"
            :class="{ invisible: currentIndex === 0 }"
            @click="goPrevLesson"
          >
            <span class="material-symbols-outlined">chevron_left</span> Previous
          </button>

          <div class="pagination-dots">
            <span
              v-for="(p, i) in dashboardData?.pages"
              :key="i"
              class="dot"
              :class="{ active: i === currentIndex }"
            ></span>
          </div>

          <button @click="handleNext" class="next-btn">
            {{ isLastPage ? 'Finish Module' : 'Next Lesson' }}
            <span class="material-symbols-outlined">chevron_right</span>
          </button>
        </footer>

      </div>

      <!-- loading state -->
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

const submitQuiz = async (questions) => {
  isQuizSubmitted.value = true;
  try {
    await learningStore.submitMiniQuiz(pageId.value, studentAnswers.value);
  } catch (error) {
    console.warn("Failed to save score, but answers checked on screen:", error);
  }
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

    timeSpent.value = 0;
    if (timer) clearInterval(timer);
    timer = setInterval(() => { timeSpent.value += 1; }, 1000);

    const mainScroll = document.getElementById('main-scroll');
    if (mainScroll) mainScroll.scrollTop = 0;

  } catch (err) {
    console.error("Failed to load lesson data", err);
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
      router.push(`/courses/${courseId.value}/modules/${moduleId.value}?completed=true&time=${timeSpent.value}`);
    }
  } catch (err) {
    console.error(err);
  }
};
</script>

<style scoped>
/* layout */
.layout-wrapper {
  display: flex;
  height: 100vh;
  background: white;
  font-family: 'DM Sans', 'Helvetica Neue', sans-serif;
  overflow: hidden;
}

.material-symbols-outlined { vertical-align: middle; }

/* sidebar */
.sidebar {
  width: 290px;
  background: #faf9f7;
  border-right: 1px solid #e8edf3;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
}

.sidebar-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e8edf3;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  color: #64748b;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  padding: 0;
  transition: color 0.18s;
  font-family: inherit;
}

.back-btn:hover { color: #1a1a1a; }

.module-info {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e8edf3;
}

.info-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.08em;
  margin: 0 0 6px;
}

.info-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #1a1a1a;
  margin: 0 0 1rem;
  line-height: 1.4;
}

.progress-bar-wrap {
  height: 4px;
  background: #e8edf3;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 6px;
}

.progress-bar-fill {
  height: 100%;
  background: #ed4081;
  border-radius: 4px;
  transition: width 0.4s ease;
}

.progress-pct {
  font-size: 0.68rem;
  font-weight: 700;
  color: #94a3b8;
  text-align: right;
  margin: 0;
  letter-spacing: 0.05em;
}

.lesson-nav {
  padding: 1.25rem 0;
}

.nav-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.08em;
  margin: 0 1.5rem 10px;
}

.nav-list {
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 11px 1.5rem;
  background: transparent;
  border: none;
  border-left: 3px solid transparent;
  cursor: pointer;
  text-align: left;
  transition: all 0.18s;
  color: #64748b;
  font-family: inherit;
}

.nav-item:hover {
  background: #f1f5f9;
  color: #1a1a1a;
}

.nav-item.active {
  background: #fce7ef;
  color: #ed4081;
  border-left-color: #ed4081;
}

.nav-item.completed .nav-icon { color: #0A703C; }
.nav-item.active .nav-icon { color: #ed4081; }

.nav-icon {
  font-size: 18px;
  flex-shrink: 0;
  margin-top: 2px;
}

.nav-text {
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.4;
}

/* main content */
.main-content {
  flex: 1;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.study-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 3.5rem 3rem 7rem;
}

/* article */
.topic-tag {
  display: inline-block;
  background: #fce7ef;
  color: #ed4081;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  padding: 4px 12px;
  border-radius: 99px;
  margin-bottom: 1.25rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 900;
  color: #1a1a1a;
  margin: 0 0 2rem;
  line-height: 1.3;
  letter-spacing: -0.5px;
  border-bottom: 2px solid #f1f5f9;
  padding-bottom: 1.5rem;
}

.content-block { margin-bottom: 2rem; }

/* rich text */
.html-content :deep(h1) { font-size: 1.6rem; font-weight: 800; margin: 2rem 0 1rem; color: #1a1a1a; }
.html-content :deep(h2) { font-size: 1.35rem; font-weight: 800; margin: 1.5rem 0 0.75rem; color: #1a1a1a; }
.html-content :deep(p) { line-height: 1.8; color: #475569; margin-bottom: 1rem; font-size: 1.03rem; }
.html-content :deep(ul), .html-content :deep(ol) { padding-left: 1.5rem; margin-bottom: 1rem; color: #475569; line-height: 1.8; font-size: 1.03rem; }
.html-content :deep(img) { max-width: 100%; height: auto; border-radius: 14px; margin: 2rem 0; box-shadow: 0 8px 24px -8px rgba(0,0,0,0.1); }

/* quiz card */
.quiz-card {
  background: white;
  border: 1.5px solid #e8edf3;
  border-radius: 20px;
  padding: 2rem;
  margin-top: 3rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.03);
}

.quiz-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.75rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #f1f5f9;
}

.quiz-icon-box {
  width: 52px;
  height: 52px;
  background: #c7ffc7;
  color: #0A703C;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quiz-icon-box .material-symbols-outlined { font-size: 28px; }

.quiz-title {
  margin: 0 0 4px;
  font-size: 1.2rem;
  font-weight: 800;
  color: #1a1a1a;
}

.quiz-subtitle {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.08em;
}

/* questions */
.question-block {
  margin-bottom: 2.25rem;
}

.question-text {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 1rem;
  line-height: 1.6;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-label {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border: 1.5px solid #e8edf3;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.18s;
  background: white;
}

.option-label:hover:not(.disabled) {
  border-color: #ffc7db;
  background: #fff9fb;
  transform: translateX(3px);
}

.option-label.selected {
  border-color: #0A703C;
  background: #f0fff4;
  box-shadow: 0 2px 10px rgba(10,112,60,0.10);
}

.option-label.correct {
  border-color: #0A703C;
  background: #c7ffc7;
  color: #065c30;
  font-weight: 700;
}

.option-label.wrong {
  border-color: #f87171;
  background: #fff5f5;
  color: #991b1b;
}

.option-label.disabled { cursor: default; }

.option-text {
  flex: 1;
  font-size: 1rem;
}

.icon-check { color: #0A703C; font-size: 22px; }
.icon-wrong { color: #ef4444; font-size: 22px; }

input[type="radio"] {
  width: 18px;
  height: 18px;
  accent-color: #0A703C;
  cursor: pointer;
  flex-shrink: 0;
}

.disabled input[type="radio"] { cursor: default; }

/* explanation */
.explanation-box {
  margin-top: 12px;
  padding: 14px 18px;
  background: #f0fff4;
  border-left: 4px solid #0A703C;
  border-radius: 0 10px 10px 0;
  font-size: 0.93rem;
  color: #065c30;
  animation: slideDown 0.25s ease-out;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* quiz footer */
.quiz-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f1f5f9;
  gap: 1rem;
}

.feedback-text {
  font-size: 1rem;
  font-weight: 700;
  margin: 0;
}

.text-muted { color: #94a3b8; }
.text-green { color: #0A703C; }
.text-amber { color: #ffc14d; }

.submit-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #0A703C;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 99px;
  font-weight: 800;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.18s;
  box-shadow: 0 4px 12px rgba(10,112,60,0.20);
  font-family: inherit;
}

.submit-btn:hover:not(:disabled) {
  background: #065c30;
  transform: translateY(-1px);
}

.submit-btn:disabled {
  background: #cbd5e1;
  box-shadow: none;
  cursor: not-allowed;
  transform: none;
}

/* bottom nav */
.bottom-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4rem;
  padding-top: 2rem;
  border-top: 1px solid #e8edf3;
}

.invisible { visibility: hidden; }

.prev-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: white;
  border: 1.5px solid #e2e8f0;
  color: #475569;
  padding: 11px 20px;
  border-radius: 99px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.18s;
  font-family: inherit;
}

.prev-btn:hover {
  background: #f8f9fb;
  color: #1a1a1a;
  border-color: #94a3b8;
}

.pagination-dots {
  display: flex;
  gap: 5px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e2e8f0;
  transition: all 0.3s;
}

.dot.active {
  width: 24px;
  border-radius: 4px;
  background: #ed4081;
}

.next-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #ed4081;
  color: white;
  border: none;
  padding: 11px 22px;
  border-radius: 99px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(237,64,129,0.22);
  transition: all 0.18s;
  font-family: inherit;
}

.next-btn:hover {
  background: #d13570;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(237,64,129,0.30);
}

/* loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80vh;
  gap: 1rem;
  color: #94a3b8;
  font-weight: 600;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e8edf3;
  border-top-color: #ed4081;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { 100% { transform: rotate(360deg); } }

/* responsive */
@media (max-width: 768px) {
  .layout-wrapper { flex-direction: column; overflow: auto; }
  .sidebar { width: 100%; height: auto; flex-shrink: 0; border-right: none; border-bottom: 1px solid #e8edf3; overflow: visible; }
  .main-content { overflow: visible; }
  .study-container { padding: 2rem 1.25rem; }
  .quiz-card { padding: 1.5rem; }
  .bottom-nav { flex-direction: column-reverse; gap: 1.25rem; }
  .prev-btn, .next-btn { width: 100%; justify-content: center; }
  .quiz-footer { flex-direction: column; align-items: stretch; }
  .submit-btn { width: 100%; justify-content: center; }
}
</style>