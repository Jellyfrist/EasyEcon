<template>
  <div class="cd-root">
    <div v-if="store.loading" class="cd-state-box"><div class="cd-spinner"></div><p>Loading course...</p></div>
    <div v-else-if="store.error" class="cd-state-box">
      <p class="cd-error-msg">{{ store.error }}</p>
      <button class="cd-btn-back" @click="goToDashboard">Go Back</button>
    </div>
    <template v-else-if="store.currentCourse">
      <div class="course-workspace">
        <aside class="course-outline">
          <h2>{{ store.currentCourse.title }}</h2>
          <nav aria-label="Course navigation">
            <router-link :to="{ name: 'Courses', params: { courseId } }" class="outline-link current" aria-current="page">
              <span class="material-symbols-outlined">home</span> Course Overview
            </router-link>
            <router-link :to="{ name: 'ModulesList', params: { courseId } }" class="outline-link">
              <span class="material-symbols-outlined">menu_book</span> Modules <span class="outline-count">{{ store.currentCourse.module_count ?? 0 }}</span>
            </router-link>
            <router-link :to="`/flashcards/${courseId}`" class="outline-link">
              <span class="material-symbols-outlined">style</span> Flashcards <span class="outline-count">{{ store.currentCourse.flashcard_set_count ?? 0 }}</span>
            </router-link>
            <router-link :to="`/exam/${courseId}`" class="outline-link">
              <span class="material-symbols-outlined">quiz</span> Exams <span class="outline-count">{{ store.currentCourse.exam_template_count ?? 0 }}</span>
            </router-link>
          </nav>
        </aside>
        <main class="course-content">
          <nav class="course-breadcrumb" aria-label="Breadcrumb">
            <router-link :to="{ name: 'Dashboard' }">Home</router-link><span>/</span>
            <router-link :to="{ name: 'Courses', params: { courseId } }" aria-current="page">Course Overview</router-link>
          </nav>
          <h1>{{ store.currentCourse.title }}</h1>
          <p v-if="store.currentCourse.description" class="course-description">{{ store.currentCourse.description }}</p>
          <dl class="course-stats">
            <div><dt>Total Modules</dt><dd>{{ store.currentCourse.module_count ?? 0 }}</dd></div>
            <div><dt>Flashcard Sets</dt><dd>{{ store.currentCourse.flashcard_set_count ?? 0 }}</dd></div>
            <div><dt>Total Exams</dt><dd>{{ store.currentCourse.exam_template_count ?? 0 }}</dd></div>
          </dl>
          <h2 class="study-heading">Study Tools</h2>
          <div class="study-tools">
            <router-link :to="{ name: 'ModulesList', params: { courseId } }" class="study-tool modules">
              <span class="material-symbols-outlined tool-icon">menu_book</span>
              <div><span class="tool-label">LEARN</span><h3>Modules</h3><p>Work through ordered lessons with mini quizzes to test your understanding.</p><span class="tool-count">{{ store.currentCourse.module_count ?? 0 }} available</span></div>
              <span class="material-symbols-outlined tool-arrow">arrow_forward</span>
            </router-link>
            <router-link :to="`/flashcards/${courseId}`" class="study-tool flashcards">
              <span class="material-symbols-outlined tool-icon">style</span>
              <div><span class="tool-label">REVIEW</span><h3>Flashcards</h3><p>Master key concepts with flashcard sets made by your teacher for fast revision.</p><span class="tool-count">{{ store.currentCourse.flashcard_set_count ?? 0 }} sets</span></div>
              <span class="material-symbols-outlined tool-arrow">arrow_forward</span>
            </router-link>
            <router-link :to="`/exam/${courseId}`" class="study-tool exams">
              <span class="material-symbols-outlined tool-icon">quiz</span>
              <div><span class="tool-label">PRACTICE TEST</span><h3>Exams</h3><p>Practice with past midterm and final exam question banks to build confidence.</p><span class="tool-count">{{ store.currentCourse.exam_template_count ?? 0 }} exams</span></div>
              <span class="material-symbols-outlined tool-arrow">arrow_forward</span>
            </router-link>
          </div>
        </main>
      </div>
      <nav class="course-bottom-nav" aria-label="Course actions">
        <button @click="goToDashboard"><span class="material-symbols-outlined">chevron_left</span> Home</button>
        <router-link :to="{ name: 'ModulesList', params: { courseId } }">Modules <span class="material-symbols-outlined">chevron_right</span></router-link>
      </nav>
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

// get course id from url: /courses/:courseId
const courseId = computed(() => route.params.courseId)

const goToDashboard = () => {
    router.push('/dashboard')
}

// fetch course data when page loads
onMounted(async () => {
    await store.viewCourse(courseId.value)
})

// clean up when leaving the page
onUnmounted(() => {
    store.clearCurrent()
})
</script>

<style scoped>
.cd-root { background: var(--white); min-height: 100vh; font-family: 'DM Sans', 'Outfit', 'Segoe UI', sans-serif; }
.course-workspace { display: grid; grid-template-columns: 240px minmax(0, 1fr); min-height: calc(100vh - 110px); }
.course-outline { border-right: 1px solid var(--card-border); padding: 1.5rem 0; background: var(--white); }
.course-outline h2 { font-size: 1.1rem; line-height: 1.5; font-weight: 600; padding: 0 1.25rem 1rem; overflow-wrap: anywhere; }
.course-outline nav { position: sticky; top: 80px; }
.outline-link { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.25rem; text-decoration: none; font-size: 0.85rem; color: var(--text-muted); }
.outline-link .material-symbols-outlined { font-size: 18px; flex-shrink: 0; }
.outline-count { margin-left: auto; }
.outline-link.current { background: var(--primary-pink); color: var(--white); }
.outline-link:not(.current):hover { background: var(--gray-light); color: var(--primary-pink); }
.course-content { width: 100%; max-width: 760px; justify-self: center; padding: 2.5rem 2.5rem 4rem; min-width: 0; }
.course-breadcrumb { display: flex; gap: 0.5rem; flex-wrap: wrap; font-size: 0.75rem; margin-bottom: 1rem; color: var(--text-muted); }
.course-breadcrumb a { color: var(--primary-pink); text-decoration: none; }
.course-content h1 { font-size: 1.8rem; line-height: 1.4; font-weight: 600; overflow-wrap: anywhere; }
.course-description { margin: 1.5rem 0; padding-left: 1rem; border-left: 3px solid var(--primary-pink); font-size: 0.95rem; line-height: 1.8; }
.course-stats { display: flex; flex-wrap: wrap; gap: 1.5rem; padding: 1.5rem 0; border-bottom: 1px solid var(--card-border); margin-bottom: 2rem; }
.course-stats div { display: flex; flex-direction: column-reverse; }
.course-stats dt { color: var(--text-muted); font-size: 0.8rem; }
.course-stats dd { color: var(--primary-pink); font-size: 1.5rem; font-weight: 600; }
.study-heading { font-size: 1.1rem; margin-bottom: 1rem; }
.study-tools { display: flex; flex-direction: column; gap: 1rem; }
.study-tool { display: flex; gap: 1rem; align-items: flex-start; padding: 1.5rem; border: 1px solid var(--card-border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); color: var(--text-main); text-decoration: none; }
.study-tool:hover { border-color: var(--primary-pink); }
.tool-icon { font-size: 28px; margin-top: 0.25rem; }
.modules .tool-icon, .modules .tool-label { color: var(--forest-green); }
.flashcards .tool-icon, .flashcards .tool-label { color: var(--primary-pink); }
.exams .tool-icon, .exams .tool-label { color: #c97924; }
.tool-label { font-size: 0.65rem; letter-spacing: 0.08em; font-weight: 700; }
.study-tool h3 { font-size: 1rem; margin: 0.25rem 0 0.5rem; }
.study-tool p { font-size: 0.85rem; line-height: 1.7; color: var(--text-muted); }
.tool-count { display: block; font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem; }
.tool-arrow { margin-left: auto; font-size: 20px; color: var(--primary-pink); }
.course-bottom-nav { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1.25rem; border-top: 1px solid var(--card-border); background: var(--white); }
.course-bottom-nav :is(a, button) { display: flex; align-items: center; gap: 0.25rem; font-family: inherit; font-size: 0.8rem; text-decoration: none; color: var(--primary-pink); border: 0; background: transparent; cursor: pointer; }
.course-bottom-nav .material-symbols-outlined { font-size: 18px; }
.cd-root :is(a, button):focus-visible { outline: 2px solid var(--primary-pink); outline-offset: 3px; }
.cd-state-box { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; gap: 1rem; }
.cd-spinner { width: 36px; height: 36px; border: 3px solid var(--light-pink); border-top-color: var(--primary-pink); border-radius: 50%; animation: cd-spin 0.8s linear infinite; }
@keyframes cd-spin { to { transform: rotate(360deg); } }
.cd-error-msg { color: #ef4444; }
.cd-btn-back { padding: 0.6rem 1.5rem; border-radius: 10px; border: none; background: var(--primary-pink); color: var(--white); cursor: pointer; }
@media (max-width: 768px) {
  .course-workspace { display: flex; flex-direction: column; }
  .course-outline { border-right: 0; border-bottom: 1px solid var(--card-border); padding: 1rem 0 0; }
  .course-outline h2 { font-size: 1rem; padding-bottom: 0.75rem; }
  .course-outline nav { position: static; display: flex; flex-wrap: wrap; }
  .outline-link { flex: 1 1 50%; padding: 0.75rem 1rem; }
  .course-content { padding: 1.5rem 1.25rem 2.5rem; }
  .course-content h1 { font-size: 1.4rem; }
  .study-tool { padding: 1.25rem; gap: 0.75rem; }
}
</style>
