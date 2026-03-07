<template>
  <div class="layout-wrapper">
    
    <aside class="sidebar" v-if="dashboardData">
      <div class="sidebar-header">
        <button class="back-btn" @click="router.push(`/student/courses/${courseId}/modules/${moduleId}`)">
          <span class="material-symbols-outlined">arrow_back</span> กลับไปหน้าโมดูล
        </button>
      </div>

      <div class="module-info">
        <p class="module-subtitle">ALL CHAPTERS</p>
        <h3 class="module-title">{{ dashboardData.module.title }}</h3>
        <div class="progress-bar-container">
          <div class="progress-fill" :style="{ width: dashboardData.progress_percent + '%' }"></div>
        </div>
        <p class="progress-text">PROGRESS: {{ dashboardData.progress_percent }}%</p>
      </div>

      <div class="lesson-nav">
        <p class="nav-section-title">CORE CONCEPTS</p>
        <div class="nav-list">
          <button 
            v-for="(page, index) in dashboardData.pages" 
            :key="page.id"
            class="nav-item"
            :class="{ 'active': page.id == pageId, 'completed': page.status === 'completed' }"
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

    <main class="main-content" id="main-scroll">
      <div v-if="pageData" class="study-container">
        
        <article class="content-render">
          <span class="topic-badge">TOPIC {{ currentIndex + 1 }}</span>
          <h1 class="page-title">{{ pageData.title }}</h1>
          
          <div v-for="block in pageData.content_blocks" :key="block.id" class="content-block">
            
            <div v-if="block.type === 'rich_text_section'" class="rich-text-section">
              <div v-html="block.data.html" class="html-content"></div>
            </div>

            <div v-else-if="block.type === 'mini_quiz' && hasValidQuiz(block.data)" class="quiz-card">
              <div class="quiz-header">
                <div class="quiz-icon-wrapper">
                  <span class="material-symbols-outlined">quiz</span>
                </div>
                <div>
                  <h3 class="quiz-title">{{ block.data.title || 'Mini Quiz' }}</h3>
                  <p class="quiz-subtitle">CHECK YOUR UNDERSTANDING</p>
                </div>
              </div>
              
              <div class="quiz-body">
                <div v-for="(q, qIndex) in block.data.questions" :key="q.id || qIndex" class="question-box">
                  <p class="quiz-question"><strong>ข้อที่ {{ qIndex + 1 }}:</strong> {{ q.text }}</p>
                  
                  <div class="options-list">
                    <label 
                      v-for="(opt, optIndex) in q.options" 
                      :key="optIndex" 
                      class="option-label"
                      :class="{ 
                        'selected': studentAnswers[q.id] === optIndex && !isQuizSubmitted,
                        'correct': isQuizSubmitted && optIndex === q.correct_index,
                        'wrong': isQuizSubmitted && studentAnswers[q.id] === optIndex && optIndex !== q.correct_index,
                        'disabled': isQuizSubmitted 
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
                      
                      <span v-if="isQuizSubmitted && optIndex === q.correct_index" class="material-symbols-outlined check-icon">check_circle</span>
                      <span v-if="isQuizSubmitted && studentAnswers[q.id] === optIndex && optIndex !== q.correct_index" class="material-symbols-outlined cross-icon">cancel</span>
                    </label>
                  </div>
                  
                  <div v-if="isQuizSubmitted && q.explanation" class="explanation-box">
                    <strong>💡 คำอธิบาย:</strong> {{ q.explanation }}
                  </div>
                </div>

                <div class="quiz-footer">
                  <p v-if="isQuizSubmitted" class="feedback-msg" :class="calculateScore(block.data.questions) === block.data.questions.length ? 'text-green' : 'text-orange'">
                    {{ calculateScore(block.data.questions) === block.data.questions.length ? 'GRATE' : `ได้คะแนน ${calculateScore(block.data.questions)} / ${block.data.questions.length}` }}
                  </p>
                  <p v-else class="feedback-msg text-gray">กรุณาเลือกคำตอบให้ครบทุกข้อ</p>

                  <button 
                    @click="submitQuiz(block.data.questions)" 
                    class="submit-quiz-btn"
                    :disabled="isQuizSubmitted || Object.keys(studentAnswers).length !== block.data.questions.length"
                  >
                    {{ isQuizSubmitted ? 'ส่งคำตอบแล้ว' : 'Submit Answer' }}
                  </button>
                </div>

              </div>
            </div>

          </div>
        </article>

        <footer class="bottom-nav">
          <button 
            class="prev-btn" 
            :class="{ 'invisible': currentIndex === 0 }"
            @click="goPrevLesson"
          >
            <span class="material-symbols-outlined">chevron_left</span> Previous
          </button>
          
          <div class="pagination-dots">
            <span 
              v-for="(p, i) in dashboardData?.pages" 
              :key="i" 
              class="dot"
              :class="{ 'active': i === currentIndex }"
            ></span>
          </div>

          <button @click="handleNext" class="next-btn">
            {{ isLastPage ? 'เรียนจบแล้ว' : 'Next Lesson' }} 
            <span class="material-symbols-outlined">chevron_right</span>
          </button>
        </footer>

      </div>
      <div v-else class="loading-state">
        <div class="spinner"></div>
        <p>กำลังเตรียมบทเรียน...</p>
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

// ================= Mini Quiz =================
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
    if (studentAnswers.value[q.id] === q.correct_index) {
      score++;
    }
  });
  return score;
};

const submitQuiz = async (questions) => {
  isQuizSubmitted.value = true;
  try {
    await learningStore.submitMiniQuiz(pageId.value, studentAnswers.value);
  } catch (error) {
    console.warn("เซฟคะแนนไม่สำเร็จ แต่ตรวจคำตอบบนหน้าจอเรียบร้อยแล้ว:", error);
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
    if(mainScroll) mainScroll.scrollTop = 0;

  } catch (err) {
    console.error("โหลดข้อมูลบทเรียนล้มเหลว", err);
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
      router.push(`/student/courses/${courseId.value}/modules/${moduleId.value}/summary?time=${timeSpent.value}`);
    }
  } catch (err) {
    console.error(err);
  }
};
</script>

<style scoped>
/* ================= Base Layout ================= */
.layout-wrapper { display: flex; height: 100vh; background-color: white; font-family: 'Sarabun', 'Inter', sans-serif; overflow: hidden; }
.material-symbols-outlined { vertical-align: middle; }

/* ================= SIDEBAR ================= */
.sidebar { width: 300px; background-color: #fafbfc; border-right: 1px solid #e2e8f0; display: flex; flex-direction: column; flex-shrink: 0; overflow-y: auto; }
.sidebar-header { padding: 1.5rem; }
.back-btn { display: flex; align-items: center; gap: 8px; background: transparent; border: none; color: #64748b; font-weight: 700; font-size: 0.9rem; cursor: pointer; padding: 0; transition: color 0.2s; }
.back-btn:hover { color: #0f172a; }
.module-info { padding: 0 1.5rem 1.5rem; border-bottom: 1px solid #e2e8f0; }
.module-subtitle { font-size: 0.75rem; font-weight: 800; color: #94a3b8; letter-spacing: 0.5px; margin: 0 0 6px 0; }
.module-title { font-size: 1.25rem; font-weight: 800; color: #0f172a; margin: 0 0 1rem 0; line-height: 1.4; }
.progress-bar-container { height: 4px; background-color: #e2e8f0; border-radius: 4px; margin-bottom: 8px; overflow: hidden; }
.progress-fill { height: 100%; background-color: #e11d48; border-radius: 4px; transition: width 0.3s ease; }
.progress-text { font-size: 0.7rem; font-weight: 800; color: #94a3b8; text-align: right; margin: 0; }

.lesson-nav { padding: 1.5rem 0; }
.nav-section-title { font-size: 0.75rem; font-weight: 800; color: #94a3b8; letter-spacing: 0.5px; margin: 0 1.5rem 12px; }
.nav-list { display: flex; flex-direction: column; }
.nav-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px 1.5rem; background: transparent; border: none; border-left: 3px solid transparent; cursor: pointer; text-align: left; transition: all 0.2s; color: #64748b; }
.nav-item:hover { background-color: #f1f5f9; color: #0f172a; }
.nav-item.active { background-color: #fff1f2; color: #e11d48; border-left-color: #e11d48; }
.nav-item.completed .nav-icon { color: #e11d48; }
.nav-icon { font-size: 20px; flex-shrink: 0; margin-top: 2px; }
.nav-text { font-size: 0.9rem; font-weight: 600; line-height: 1.4; }

/* ================= MAIN CONTENT ================= */
.main-content { flex: 1; overflow-y: auto; scroll-behavior: smooth; position: relative; }
.study-container { max-width: 850px; margin: 0 auto; padding: 4rem 3rem 8rem; }

.topic-badge { display: inline-block; background: #fff1f2; color: #e11d48; padding: 4px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 1.5rem; }
.page-title { font-size: 2.25rem; font-weight: 900; color: #0f172a; margin: 0 0 2rem 0; line-height: 1.3; letter-spacing: -0.5px; border-bottom: 2px solid #f1f5f9; padding-bottom: 1.5rem; }

.content-block { margin-bottom: 2rem; }
.html-content :deep(h1) { font-size: 1.75rem; font-weight: 800; margin: 2rem 0 1rem; color: #0f172a; }
.html-content :deep(h2) { font-size: 1.5rem; font-weight: 800; margin: 1.5rem 0 1rem; color: #1e293b; }
.html-content :deep(p) { line-height: 1.8; color: #475569; margin-bottom: 1rem; font-size: 1.05rem; }
.html-content :deep(ul), .html-content :deep(ol) { padding-left: 1.5rem; margin-bottom: 1rem; color: #475569; line-height: 1.8; font-size: 1.05rem; }
.html-content :deep(img) { max-width: 100%; height: auto; border-radius: 16px; margin: 2rem 0; box-shadow: 0 10px 30px -10px rgba(0,0,0,0.1); }

/* ================= Mini Quiz Card ================= */
.quiz-card { background: white; border: 1px solid #e2e8f0; border-radius: 20px; padding: 2.5rem; margin-top: 3.5rem; box-shadow: 0 10px 30px -5px rgba(0,0,0,0.03); }
.quiz-header { display: flex; align-items: center; gap: 1.25rem; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid #f1f5f9; }
.quiz-icon-wrapper { width: 56px; height: 56px; background: #ecfdf5; color: #10b981; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.quiz-icon-wrapper span { font-size: 32px; }
.quiz-title { margin: 0; font-size: 1.35rem; font-weight: 800; color: #0f172a; }
.quiz-subtitle { margin: 0; font-size: 0.8rem; font-weight: 800; color: #94a3b8; letter-spacing: 1px; }

.question-box { margin-bottom: 2.5rem; }
.quiz-question { font-size: 1.15rem; font-weight: 700; color: #1e293b; margin-bottom: 1.25rem; line-height: 1.6; }

/* Options */
.options-list { display: flex; flex-direction: column; gap: 12px; }
.option-label { display: flex; align-items: center; gap: 14px; padding: 16px 20px; border: 2px solid #e2e8f0; border-radius: 14px; cursor: pointer; transition: all 0.2s ease; background: white; }
.option-label:hover:not(.disabled) { border-color: #cbd5e1; background: #f8fafc; transform: translateX(4px); }
.option-label.selected { border-color: #10b981; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15); }
.option-label.correct { border-color: #10b981; background: #ecfdf5; color: #065f46; font-weight: 700; }
.option-label.wrong { border-color: #ef4444; background: #fef2f2; color: #991b1b; }
.option-label.disabled { cursor: default; }

.option-text { flex: 1; font-size: 1.05rem; }
.check-icon { color: #10b981; font-size: 24px; }
.cross-icon { color: #ef4444; font-size: 24px; }

input[type="radio"] { width: 20px; height: 20px; accent-color: #10b981; cursor: pointer; }
.disabled input[type="radio"] { cursor: default; }

/* Explanation */
.explanation-box { margin-top: 16px; padding: 16px 20px; background: #f0fdf4; border-left: 4px solid #10b981; border-radius: 0 12px 12px 0; font-size: 0.95rem; color: #065f46; animation: slideDown 0.3s ease-out; }
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

/* Footer Quiz */
.quiz-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 2rem; padding-top: 2rem; border-top: 1px solid #f1f5f9; }
.feedback-msg { font-size: 1.05rem; font-weight: 700; margin: 0; }
.text-gray { color: #94a3b8; }
.text-green { color: #10b981; }
.text-orange { color: #f59e0b; }

.submit-quiz-btn { display: flex; align-items: center; gap: 8px; background: #10b981; color: white; border: none; padding: 14px 28px; border-radius: 99px; font-weight: 800; font-size: 1rem; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25); }
.submit-quiz-btn:hover:not(:disabled) { background: #059669; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35); }
.submit-quiz-btn:disabled { background: #cbd5e1; color: white; cursor: not-allowed; box-shadow: none; transform: none; }

/* ================= FOOTER NAV (Main) ================= */
.bottom-nav { display: flex; justify-content: space-between; align-items: center; margin-top: 4rem; padding-top: 2rem; border-top: 1px solid #e2e8f0; }
.invisible { visibility: hidden; }

.prev-btn { display: flex; align-items: center; gap: 4px; background: white; border: 1px solid #cbd5e1; color: #475569; padding: 12px 20px; border-radius: 99px; font-weight: 700; font-size: 0.95rem; cursor: pointer; transition: all 0.2s; }
.prev-btn:hover { background: #f8fafc; color: #0f172a; border-color: #94a3b8; }

.pagination-dots { display: flex; gap: 6px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background-color: #e2e8f0; transition: all 0.3s; }
.dot.active { width: 24px; border-radius: 4px; background-color: #e11d48; }

.next-btn { display: flex; align-items: center; gap: 4px; background: #e11d48; color: white; border: none; padding: 12px 24px; border-radius: 99px; font-weight: 700; font-size: 0.95rem; cursor: pointer; box-shadow: 0 4px 15px rgba(225, 29, 72, 0.25); transition: all 0.2s; }
.next-btn:hover { background: #be123c; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(225, 29, 72, 0.35); }

.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; color: #64748b; font-weight: 700; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: #e11d48; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .layout-wrapper { flex-direction: column; overflow: auto; }
  .sidebar { width: 100%; height: auto; flex-shrink: 0; border-right: none; border-bottom: 1px solid #e2e8f0; overflow: visible; }
  .main-content { overflow: visible; }
  .study-container { padding: 2rem 1.5rem; }
  .quiz-card { padding: 1.5rem; }
  .bottom-nav { flex-direction: column-reverse; gap: 1.5rem; }
  .prev-btn, .next-btn { width: 100%; justify-content: center; }
}
</style>