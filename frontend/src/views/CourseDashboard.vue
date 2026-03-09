<template>
  <div class="page-wrapper">
  
      <div v-if="store.loading" class="state-box text-center text-muted">
          <p>Loading course...</p>
      </div>
  
      <div v-else-if="store.error" class="state-box text-center">
          <p class="error-msg">{{ store.error }}</p>
          <button class="btn btn-primary mt-2" @click="router.back()">Go Back</button>
      </div>
  
      <template v-else-if="store.currentCourse">
  
        <div class="text-center mb-4">
          <span class="course-label">Course</span>
          <h1 class="course-title">{{ store.currentCourse.title }}</h1>
          <p v-if="store.currentCourse.description" class="text-muted course-description">
            {{ store.currentCourse.description }}
          </p>
        </div>
  
        <div class="grid-3 mb-4">
          <div class="card text-center">
            <div class="stat-icon">📚</div>
            <div class="stat-number">{{ store.currentCourse.module_count ?? 0 }}</div>
            <div class="text-muted">Modules</div>
          </div>
          <div class="card text-center">
            <div class="stat-icon">🃏</div>
            <div class="stat-number">{{ store.currentCourse.flashcard_set_count ?? 0 }}</div>
            <div class="text-muted">Flashcard Sets</div>
          </div>
          <div class="card text-center">
            <div class="stat-icon">📝</div>
            <div class="stat-number">{{ store.currentCourse.exam_template_count ?? 0 }}</div>
            <div class="text-muted">Exam Templates</div>
          </div>
        </div>
  
        <div class="grid-3">
  
          <div class="card feature-card green" @click="router.push(`/courses/${courseId}/modules`)">
            <div class="icon-wrapper"><span>📚</span></div>
            <h2>Modules</h2>
            <p>Work through ordered lessons with mini quizzes to test your understanding.</p>
          </div>
  
          <div class="card feature-card pink" @click="router.push(`/flashcards/${courseId}`)">
            <div class="icon-wrapper"><span>🃏</span></div>
            <h2>Flashcards</h2>
            <p>Master key concepts with flashcard sets made by your teacher.</p>
          </div>
  
          <div class="card feature-card yellow" @click="router.push(`/exam/${courseId}`)">
            <div class="icon-wrapper"><span>📝</span></div>
            <h2>Exams</h2>
            <p>Practice with past midterm and final exam question banks.</p>
          </div>
  
        </div>
      </template>

  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { onMounted, onUnmounted, computed } from 'vue'
import { useCourseStore } from '@/store/courseStore'

const route = useRoute()
const router = useRouter()
const store = useCourseStore()

// get course id from route: /courses/:courseId
const courseId = computed(() => route.params.courseId)

// load course on page open
// store.viewCourse -> GET /courses/:courseId/view (student endpoint)
onMounted(async () => {
    await store.viewCourse(courseId.value)
})

// clear currentCourse when leaving the page
onUnmounted(() => {
    store.clearCurrent()
})
</script>

<style scoped>
/* loading / error area */
.state-box { padding: 6rem 1rem; }
.error-msg {
    color: #ef4444; font-size: 1rem; background: #fef2f2;
    border-radius: var(--radius-md); padding: 0.75rem 1rem; display: inline-block;
}

/* hero */
.course-label {
    color: var(--primary-pink); font-weight: 700; font-size: 0.75rem;
    letter-spacing: 3px; text-transform: uppercase; display: block; margin-bottom: 1rem;
}
.course-title {
    font-size: 3rem; font-weight: 900; color: var(--text-main);
    line-height: 1.15; margin-bottom: 1rem;
}
.course-description { font-size: 1.1rem; max-width: 640px; margin: 0 auto; line-height: 1.7; }

/* stat cards */
.stat-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.stat-number { font-size: 2.2rem; font-weight: 900; color: var(--text-main); margin-bottom: 0.25rem; }

/* feature cards */
.feature-card {
    cursor: pointer; min-height: 260px; display: flex; flex-direction: column;
    align-items: flex-start; gap: 0.75rem; border: none;
    transition: transform 0.2s, box-shadow 0.2s; /* เพิ่ม Transition ให้กดสมูทขึ้น */
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.feature-card h2 { font-size: 1.5rem; font-weight: 800; }
.feature-card p { font-size: 0.95rem; line-height: 1.7; opacity: 0.9; }

/* icon inside feature card */
.icon-wrapper {
    width: 56px; height: 56px; border-radius: var(--radius-md); display: flex;
    align-items: center; justify-content: center; background: rgba(255, 255, 255, 0.25);
    backdrop-filter: blur(6px); margin-bottom: 0.5rem;
}

.icon-wrapper span { font-size: 1.8rem; }

.feature-card.green { background: linear-gradient(135deg, #0f7a3e, #0b5d30); color: white; }
.feature-card.pink { background: linear-gradient(135deg, #ff4d8d, #e91e63); color: white; }
.feature-card.yellow { background: linear-gradient(135deg, #ffe2a2, #f1d18c); color: var(--text-main); }

@media (max-width: 768px) {
    .course-title { font-size: 2rem; }
}
</style>