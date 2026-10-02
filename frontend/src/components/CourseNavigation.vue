<template>
  <div class="course-navigation-space" :class="{ 'navigation-collapsed': collapsed }" :style="{ '--navigation-height': navigationHeight + 'px' }">
  <aside ref="navigation" class="feature-navigation" :class="{ 'navigation-collapsed': collapsed }" aria-label="Course navigation">
    <div class="navigation-heading">
      <h2 v-show="!collapsed">{{ course?.title || 'Course' }}</h2>
      <button type="button" class="navigation-toggle" :aria-expanded="!collapsed"
        :aria-label="collapsed ? 'Open course navigation' : 'Close course navigation'"
        :title="collapsed ? 'Open navigation' : 'Close navigation'" @click="collapsed = !collapsed">
        <span class="material-symbols-outlined" aria-hidden="true">{{ collapsed ? 'menu' : 'chevron_left' }}</span>
      </button>
    </div>
    <nav>
      <router-link aria-label="Course Overview" :title="collapsed ? 'Course Overview' : undefined" :to="{ name: 'Courses', params: { courseId } }" :class="{ current: current === 'overview' }" :aria-current="current === 'overview' ? 'page' : undefined">
        <span class="material-symbols-outlined" aria-hidden="true">home</span><span v-show="!collapsed">Course Overview</span>
      </router-link>
      <router-link aria-label="Modules" :title="collapsed ? 'Modules' : undefined" :to="{ name: 'ModulesList', params: { courseId } }" :class="{ current: current === 'modules' }" :aria-current="current === 'modules' ? 'page' : undefined">
        <span class="material-symbols-outlined" aria-hidden="true">menu_book</span><span v-show="!collapsed">Modules</span> <span v-show="!collapsed" class="navigation-count">{{ course?.module_count ?? 0 }}</span>
      </router-link>
      <router-link aria-label="Exams" :title="collapsed ? 'Exams' : undefined" :to="{ name: 'ExamDashboard', params: { courseId } }" :class="{ current: current === 'exams' }" :aria-current="current === 'exams' ? 'page' : undefined">
        <span class="material-symbols-outlined" aria-hidden="true">quiz</span><span v-show="!collapsed">Exams</span> <span v-show="!collapsed" class="navigation-count">{{ course?.exam_template_count ?? 0 }}</span>
      </router-link>
    </nav>
  </aside>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useCourseNavigation } from '@/composables/useCourseNavigation'
import { useCourseStore } from '@/store/courseStore'
const props = defineProps({ courseId: { type: [String, Number], required: true }, current: String })
const { collapsed } = useCourseNavigation()
const navigation = ref(null)
const navigationHeight = ref(0)
let navigationObserver
onMounted(() => {
  const measureNavigation = () => { navigationHeight.value = navigation.value.getBoundingClientRect().height }
  navigationObserver = new ResizeObserver(measureNavigation)
  navigationObserver.observe(navigation.value)
  measureNavigation()
})
onUnmounted(() => navigationObserver?.disconnect())
const store = useCourseStore()
const course = computed(() => String(store.currentCourse?.id) === String(props.courseId) ? store.currentCourse : null)
watch([() => props.courseId, () => store.currentCourse?.id], async ([id]) => {
  if (!course.value) await store.viewCourse(id)
}, { immediate: true })
</script>

<style scoped>
.course-navigation-space { min-width: 0; }
.feature-navigation { position: fixed; left: 0; width: var(--course-navigation-width, 260px); z-index: 200; top: var(--feature-sticky-top, 160px); padding: 24px 0; border-right: 1px solid var(--card-border); height: calc(100dvh - var(--feature-sticky-top, 160px)); overflow-y: auto; background: var(--surface); }
.navigation-heading { display: flex; align-items: center; gap: 4px; padding: 0 8px 20px 20px; }
.navigation-toggle { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 44px; height: 44px; margin: 0; border: 0; border-radius: 8px; background: var(--surface); color: var(--text-muted); cursor: pointer; }
.navigation-toggle:hover { background: var(--gray-light); color: var(--primary-pink); }
.navigation-toggle:focus-visible { outline: 2px solid var(--primary-pink); outline-offset: -2px; }
.feature-navigation.navigation-collapsed { padding: 16px 8px; }
.navigation-collapsed .navigation-heading { justify-content: center; padding: 0 0 16px; }
.navigation-collapsed nav { align-items: center; gap: 8px; }
.navigation-collapsed a { justify-content: center; width: 44px; height: 44px; padding: 0; border-radius: 8px; }
h2 { font-size: 1.05rem; line-height: 1.5; font-weight: 600; flex: 1; min-width: 0; margin: 0; padding: 0; overflow-wrap: anywhere; }
nav { display: flex; flex-direction: column; }
a { display: flex; align-items: center; gap: 8px; min-height: 44px; padding: 10px 20px; text-decoration: none; color: var(--text-muted); font-size: 0.85rem; }
a.current { background: var(--primary-pink); color: var(--white); }
a:not(.current):hover { background: var(--gray-light); color: var(--primary-pink); }
a:focus-visible { outline: 2px solid var(--primary-pink); outline-offset: -2px; }
.material-symbols-outlined { font-size: 18px; }
.navigation-count { margin-left: auto; }
@media (max-width: 768px) {
  .course-navigation-space { height: var(--navigation-height); }
  .course-navigation-space.navigation-collapsed { height: auto; }
  .feature-navigation { width: 100%; height: auto; max-height: calc(100dvh - var(--feature-sticky-top)); border-right: 0; border-bottom: 1px solid var(--card-border); padding: 16px 0 0; }
  .navigation-heading { padding-bottom: 12px; }
  .feature-navigation.navigation-collapsed { width: var(--course-navigation-width); height: calc(100dvh - var(--feature-sticky-top)); padding: 16px 8px; border-right: 1px solid var(--card-border); border-bottom: 0; }
  .navigation-collapsed nav { flex-direction: column; }
  .navigation-collapsed a { flex: none; }
  h2 { font-size: 0.95rem; }
  nav { flex-direction: row; flex-wrap: wrap; }
  a { flex: 1 1 auto; padding: 10px 16px; }
}
</style>
