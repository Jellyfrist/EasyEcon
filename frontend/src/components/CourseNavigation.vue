<template>
  <div class="course-navigation-space" :class="{ 'navigation-collapsed': collapsed }" :style="{ '--navigation-height': navigationHeight + 'px' }">
  <aside ref="navigation" class="feature-navigation" :class="{ 'navigation-collapsed': collapsed }" aria-label="Course navigation">
    <NavigationHeading :title="course?.title || 'Course'" :collapsed="collapsed" @toggle="collapsed = !collapsed" />
    <nav v-if="teacher">
      <router-link aria-label="My Courses" :title="collapsed ? 'My Courses' : undefined" :to="{ name: 'Teacher' }" :class="{ current: current === 'my-courses' }" :aria-current="current === 'my-courses' ? 'page' : undefined">
        <span class="material-symbols-outlined" aria-hidden="true">school</span><span v-show="!collapsed">My Courses</span>
      </router-link>
      <router-link aria-label="Manage Course" :title="collapsed ? 'Manage Course' : undefined" :to="{ name: 'CoursesEditor', params: { courseId } }" :class="{ current: current === 'overview' }" :aria-current="current === 'overview' ? 'page' : undefined">
        <span class="material-symbols-outlined" aria-hidden="true">edit_note</span><span v-show="!collapsed">Manage Course</span>
      </router-link>
      <router-link aria-label="Modules" :title="collapsed ? 'Modules' : undefined" :to="{ name: 'TeacherLearningDashboard', params: { courseId } }" :class="{ current: current === 'modules' }" :aria-current="current === 'modules' ? 'page' : undefined">
        <span class="material-symbols-outlined" aria-hidden="true">menu_book</span><span v-show="!collapsed">Modules</span> <span v-show="!collapsed" class="navigation-count">{{ course?.module_count ?? 0 }}</span>
      </router-link>
      <router-link aria-label="Exams" :title="collapsed ? 'Exams' : undefined" :to="{ name: 'TeacherExamDashboard', params: { courseId } }" :class="{ current: current === 'exams' }" :aria-current="current === 'exams' ? 'page' : undefined">
        <span class="material-symbols-outlined" aria-hidden="true">quiz</span><span v-show="!collapsed">Exams</span> <span v-show="!collapsed" class="navigation-count">{{ course?.exam_template_count ?? 0 }}</span>
      </router-link>
    </nav>
    <nav v-else>
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
import NavigationHeading from '@/components/NavigationHeading.vue'
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { useCourseNavigation } from '@/composables/useCourseNavigation'
import courseService from '@/services/courseService'
import { useCourseStore } from '@/store/courseStore'
const props = defineProps({ courseId: { type: [String, Number], required: true }, current: String, teacher: { type: Boolean, default: false } })
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
const teacherCourse = ref(null)
const course = computed(() => props.teacher ? teacherCourse.value : (String(store.currentCourse?.id) === String(props.courseId) ? store.currentCourse : null))
watch([() => props.courseId, () => props.teacher, () => store.currentCourse?.id], async ([id, isTeacher]) => {
  if (!id) return
  try {
    if (isTeacher) {
      const { data } = await courseService.getCourse(id)
      teacherCourse.value = data
    } else if (!course.value) {
      await store.viewCourse(id)
    }
  } catch {
    teacherCourse.value = null
  }
}, { immediate: true })
</script>

<style scoped>
.course-navigation-space { min-width: 0; }
.feature-navigation { position: fixed; left: 0; width: var(--course-navigation-width, 260px); z-index: 200; top: var(--feature-sticky-top, 160px); padding: 24px 0; border-right: 1px solid var(--card-border); height: calc(100dvh - var(--feature-sticky-top, 160px)); overflow-y: auto; background: var(--surface); }
.feature-navigation.navigation-collapsed { padding: 16px 8px; }
.navigation-collapsed nav { align-items: center; gap: 8px; }
.navigation-collapsed a { justify-content: center; width: 44px; height: 44px; padding: 0; border-radius: 8px; }
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
  .feature-navigation.navigation-collapsed { width: var(--course-navigation-width); height: calc(100dvh - var(--feature-sticky-top)); padding: 16px 8px; border-right: 1px solid var(--card-border); border-bottom: 0; }
  .navigation-collapsed nav { flex-direction: column; }
  .navigation-collapsed a { flex: none; }
  nav { flex-direction: row; flex-wrap: wrap; }
  a { flex: 1 1 auto; padding: 10px 16px; }
}
</style>
