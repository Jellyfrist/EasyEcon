<template>
  <div class="ml-root">

    <!-- topbar -->
    <header class="ml-topbar">
      <button class="ml-back-btn" @click="router.push({ name: 'Courses', params: { courseId } })">
        <span class="material-symbols-outlined">arrow_back</span>
        Back to Course
      </button>
    </header>

    <div class="ml-body">

      <!-- page header -->
      <div class="ml-page-header">
        <span class="ml-course-tag">Course #{{ courseId }}</span>
        <h1 class="ml-page-title">Learning Modules</h1>
        <p class="ml-page-sub">Select a module to start learning.</p>
      </div>

      <!-- loading -->
      <div v-if="loading" class="ml-state">
        <div class="ml-spinner"></div>
        <p>Loading modules...</p>
      </div>

      <!-- error -->
      <div v-else-if="error" class="ml-error">
        <span class="material-symbols-outlined">error_outline</span>
        {{ error }}
      </div>

      <!-- empty -->
      <div v-else-if="modules.length === 0" class="ml-empty">
        <div class="ml-empty-icon">
          <span class="material-symbols-outlined">menu_book</span>
        </div>
        <h3>No content yet</h3>
        <p>No modules have been added to this course.<br>Check back later when your instructor publishes content.</p>
      </div>

      <!-- module grid -->
      <div v-else class="ml-grid">
        <div
          v-for="(mod, index) in modules"
          :key="mod.id"
          class="ml-card"
          @click="goToLesson(mod.id)"
        >
          <!-- card accent bar color cycles through palette -->
          <div class="ml-card-bar" :style="{ background: barColors[index % barColors.length] }"></div>

          <div class="ml-card-body">
            <div class="ml-card-top">
              <span class="ml-module-num">Module {{ index + 1 }}</span>
              <span class="ml-lesson-pill">
                <span class="material-symbols-outlined">auto_stories</span>
                {{ mod.learning_pages?.length || 0 }} lessons
              </span>
            </div>

            <h2 class="ml-card-title">{{ mod.title }}</h2>

            <div class="ml-card-footer">
              <span class="ml-start-link">
                Start module
                <span class="material-symbols-outlined">arrow_forward</span>
              </span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import learningService from '@/services/learningService'

const route    = useRoute()
const router   = useRouter()
const courseId = computed(() => route.params.courseId)

const modules = ref([])
const loading = ref(false)
const error   = ref(null)

// accent bar colors using the brand palette
const barColors = [
  '#ed4081',
  '#0A703C',
  '#ffc14d',
  '#ed4081',
  '#0A703C',
  '#ffc14d',
]

const loadModules = async () => {
  loading.value = true
  error.value   = null
  try {
    const res = await learningService.listModules(courseId.value)
    const fetched = res.data || []

    for (const mod of fetched) {
      try {
        const pRes = await learningService.listPages(mod.id)
        mod.learning_pages = (pRes.data || []).filter(p => p.is_published)
      } catch {
        mod.learning_pages = []
      }
      mod.isExpanded = false
    }
    modules.value = fetched
  } catch (err) {
    console.error('Failed to fetch modules:', err)
    error.value = 'Failed to load modules. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(loadModules)

const goToLesson = moduleId => {
  router.push({ name: 'LearningDashboard', params: { courseId: courseId.value, moduleId } })
}
</script>

<style scoped>
/* tokens */
.ml-root {
  --pink:         #ed4081;
  --pink-h:       #d13570;
  --pink-light:   #ffc7db;
  --pink-bg:      #fff0f6;
  --green:        #0A703C;
  --green-light:  #c7ffc7;
  --yellow:       #ffc14d;
  --yellow-light: #fff4c7;
  --ink:          #1a1a2e;
  --ink2:         #374151;
  --muted:        #6b7280;
  --border:       #e5e7eb;
  --bg:           #faf9f7;
  --white:        #ffffff;
  font-family: 'DM Sans', 'Helvetica Neue', sans-serif;
  background: var(--bg);
  min-height: 100vh;
}

/* topbar */
.ml-topbar {
  background: var(--white);
  border-bottom: 1px solid var(--border);
  padding: 0 2rem;
  height: 56px;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 50;
}

.ml-back-btn {
  display: flex; align-items: center; gap: 6px;
  background: none; border: none; cursor: pointer;
  font-family: inherit; font-size: 0.88rem; font-weight: 600;
  color: var(--muted); padding: 0;
  transition: color 0.15s;
}
.ml-back-btn .material-symbols-outlined { font-size: 18px; }
.ml-back-btn:hover { color: var(--pink); }

/* body */
.ml-body { max-width: 1000px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }

/* page header */
.ml-page-header { margin-bottom: 2rem; }
.ml-course-tag {
  display: inline-block;
  font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--pink); background: var(--pink-bg);
  padding: 3px 10px; border-radius: 99px;
  margin-bottom: 0.6rem;
}
.ml-page-title {
  font-size: 1.9rem; font-weight: 800;
  color: var(--ink); margin: 0 0 0.35rem;
  letter-spacing: -0.5px;
}
.ml-page-sub { font-size: 0.95rem; color: var(--muted); margin: 0; }

/* states */
.ml-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 1rem; padding: 5rem 0; color: var(--muted);
}
.ml-spinner {
  width: 36px; height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--pink);
  border-radius: 50%;
  animation: ml-spin 0.8s linear infinite;
}
@keyframes ml-spin { to { transform: rotate(360deg); } }

.ml-error {
  display: flex; align-items: center; gap: 10px;
  background: #fff0f0; color: #c0392b;
  border: 1px solid #fecaca; border-radius: 12px;
  padding: 1rem 1.25rem; font-weight: 600; font-size: 0.9rem;
}

.ml-empty {
  text-align: center; padding: 5rem 2rem;
  background: var(--white); border: 1px solid var(--border);
  border-radius: 20px;
}
.ml-empty-icon {
  width: 64px; height: 64px; border-radius: 16px;
  background: var(--pink-bg); color: var(--pink);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 1.25rem;
}
.ml-empty-icon .material-symbols-outlined { font-size: 32px; }
.ml-empty h3 { font-size: 1.15rem; font-weight: 700; color: var(--ink); margin: 0 0 0.5rem; }
.ml-empty p  { font-size: 0.9rem; color: var(--muted); line-height: 1.6; margin: 0; }

/* grid */
.ml-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

/* card */
.ml-card {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s;
  display: flex; flex-direction: column;
}
.ml-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.09);
  border-color: #d1d5db;
}

.ml-card-bar { height: 5px; flex-shrink: 0; }

.ml-card-body { padding: 1.4rem 1.5rem 1.25rem; display: flex; flex-direction: column; flex: 1; }

.ml-card-top {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 0.85rem;
}

.ml-module-num {
  font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--muted);
}

.ml-lesson-pill {
  display: flex; align-items: center; gap: 4px;
  font-size: 0.75rem; font-weight: 600; color: var(--muted);
  background: var(--bg); border: 1px solid var(--border);
  padding: 3px 9px; border-radius: 99px;
}
.ml-lesson-pill .material-symbols-outlined { font-size: 13px; }

.ml-card-title {
  font-size: 1.05rem; font-weight: 700;
  color: var(--ink); margin: 0; line-height: 1.45;
  flex: 1;
}

.ml-card-footer { margin-top: 1.25rem; }

.ml-start-link {
  display: flex; align-items: center; gap: 4px;
  font-size: 0.82rem; font-weight: 700;
  color: var(--pink); transition: gap 0.15s;
}
.ml-start-link .material-symbols-outlined { font-size: 16px; }
.ml-card:hover .ml-start-link { gap: 8px; }

/* responsive */
@media (max-width: 600px) {
  .ml-grid { grid-template-columns: 1fr; }
  .ml-body { padding: 1.5rem 1rem 4rem; }
  .ml-page-title { font-size: 1.5rem; }
}
</style>