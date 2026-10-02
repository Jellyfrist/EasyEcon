<template>
  <aside class="feature-navigation" :class="{ 'navigation-collapsed': collapsed }" aria-label="Course navigation">
    <button type="button" class="navigation-toggle" :aria-expanded="!collapsed"
      :aria-label="collapsed ? 'Open course navigation' : 'Close course navigation'"
      :title="collapsed ? 'Open navigation' : 'Close navigation'" @click="collapsed = !collapsed">
      <span class="material-symbols-outlined" aria-hidden="true">{{ collapsed ? 'chevron_right' : 'chevron_left' }}</span>
    </button>
    <h2 v-show="!collapsed">{{ course?.title || 'Course' }}</h2>
    <nav v-show="!collapsed">
      <router-link :to="{ name: 'Courses', params: { courseId } }" :class="{ current: current === 'overview' }" :aria-current="current === 'overview' ? 'page' : undefined">
        <span class="material-symbols-outlined" aria-hidden="true">home</span> Course Overview
      </router-link>
      <router-link :to="{ name: 'ModulesList', params: { courseId } }" :class="{ current: current === 'modules' }" :aria-current="current === 'modules' ? 'page' : undefined">
        <span class="material-symbols-outlined" aria-hidden="true">menu_book</span> Modules <span class="navigation-count">{{ course?.module_count ?? 0 }}</span>
      </router-link>
      <router-link :to="{ name: 'ExamDashboard', params: { courseId } }" :class="{ current: current === 'exams' }" :aria-current="current === 'exams' ? 'page' : undefined">
        <span class="material-symbols-outlined" aria-hidden="true">quiz</span> Exams <span class="navigation-count">{{ course?.exam_template_count ?? 0 }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useCourseStore } from '@/store/courseStore'
const props = defineProps({ courseId: { type: [String, Number], required: true }, current: String })
const collapsed = ref(false)
const store = useCourseStore()
const course = computed(() => String(store.currentCourse?.id) === String(props.courseId) ? store.currentCourse : null)
watch([() => props.courseId, () => store.currentCourse?.id], async ([id]) => {
  if (!course.value) await store.viewCourse(id)
}, { immediate: true })
</script>

<style scoped>
.feature-navigation { position: sticky; top: var(--feature-sticky-top, 160px); align-self: start; padding: 24px 0; border-right: 1px solid var(--card-border); min-height: calc(100dvh - var(--feature-sticky-top, 160px)); background: var(--surface); }
.navigation-toggle { display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; margin: 0 0 8px auto; border: 0; background: var(--surface); color: var(--text-muted); cursor: pointer; }
.navigation-toggle:hover { background: var(--gray-light); color: var(--primary-pink); }
.navigation-toggle:focus-visible { outline: 2px solid var(--primary-pink); outline-offset: -2px; }
.navigation-collapsed { padding-top: 8px; }
h2 { font-size: 1.05rem; line-height: 1.5; font-weight: 600; padding: 0 20px 20px; overflow-wrap: anywhere; }
nav { display: flex; flex-direction: column; }
a { display: flex; align-items: center; gap: 8px; min-height: 44px; padding: 10px 20px; text-decoration: none; color: var(--text-muted); font-size: 0.85rem; }
a.current { background: var(--primary-pink); color: var(--white); }
a:not(.current):hover { background: var(--gray-light); color: var(--primary-pink); }
a:focus-visible { outline: 2px solid var(--primary-pink); outline-offset: -2px; }
.material-symbols-outlined { font-size: 18px; }
.navigation-count { margin-left: auto; }
@media (max-width: 768px) {
  .feature-navigation { position: static; min-height: 0; border-right: 0; border-bottom: 1px solid var(--card-border); padding: 16px 0 0; }
  h2 { padding-bottom: 12px; font-size: 0.95rem; }
  nav { flex-direction: row; flex-wrap: wrap; }
  a { flex: 1 1 auto; padding: 10px 16px; }
}
</style>
