<template>
  <FeaturePage class="cd-root" fluid>
    <template #navigation><CourseNavigation :course-id="courseId" current="overview" /></template>
    <template #header>
        <EditorHeader :title="store.currentCourse?.title || 'Course'" :back-to="{ name: 'Dashboard' }" :breadcrumbs="[{ label: 'Courses', to: { name: 'Dashboard' } }, { label: 'Course', to: route.fullPath }]"></EditorHeader>
    </template>

    <div v-if="store.loading" class="cd-state-box"><div class="cd-spinner"></div><p>Loading course...</p></div>
    <div v-else-if="store.error" class="cd-state-box">
      <p class="cd-error-msg">{{ store.error }}</p>
      <button class="cd-btn-back" @click="goToDashboard">Go Back</button>
    </div>
    <template v-else-if="store.currentCourse">

      <div class="course-workspace">

        <main class="course-content">

          <p v-if="store.currentCourse.description" class="course-description">{{ store.currentCourse.description }}</p>
          <dl class="course-stats">
            <div><dt>Total Modules</dt><dd>{{ store.currentCourse.module_count ?? 0 }}</dd></div>
            <div><dt>Total Exams</dt><dd>{{ store.currentCourse.exam_template_count ?? 0 }}</dd></div>
          </dl>
          <h2 class="study-heading">Study Tools</h2>
          <div class="study-tools">
            <router-link :to="{ name: 'ModulesList', params: { courseId } }" class="study-tool modules">
              <span class="material-symbols-outlined tool-icon">menu_book</span>
              <div><span class="tool-label">LEARN</span><h3>Modules</h3><p>Work through ordered lessons with mini quizzes to test your understanding.</p><span class="tool-count">{{ store.currentCourse.module_count ?? 0 }} available</span></div>
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
  </FeaturePage>
</template>

<script setup>
import CourseNavigation from '@/components/CourseNavigation.vue'
import EditorHeader from '@/components/EditorHeader.vue'
import FeaturePage from '@/components/FeaturePage.vue'
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

.course-workspace { display: grid;  min-height: calc(100vh - 110px); }

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

  .course-content { padding: 1.5rem 1.25rem 2.5rem; }
  .course-content h1 { font-size: 1.4rem; }
  .study-tool { padding: 1.25rem; gap: 0.75rem; }
}
</style>
