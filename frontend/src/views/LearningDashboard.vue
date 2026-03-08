<template>
  <div class="layout-wrapper">

    <!-- sidebar -->
    <aside class="sidebar">

      <div class="sidebar-nav">
        <button class="nav-btn" @click="router.push('/dashboard')">
          <span class="material-symbols-outlined">home</span> Home
        </button>
        <button class="nav-btn" @click="router.push(`/courses/${courseId}/modules`)">
          <span class="material-symbols-outlined">arrow_back</span> Back to Modules
        </button>
      </div>

      <div class="sidebar-section-label">
        Lessons ({{ courseModules.length }})
      </div>

      <div class="sidebar-modules" v-if="courseModules.length > 0">
        <div
          v-for="(mod, index) in courseModules"
          :key="mod.id"
          class="sidebar-item"
          :class="{ active: mod.id == moduleId }"
          @click="goToModule(mod.id)"
        >
          <div class="sidebar-item-text">
            <span class="sidebar-item-num">
              Module {{ index + 1 }}
              <span v-if="mod.id == moduleId" class="in-progress-tag">In Progress</span>
            </span>
            <h4 class="sidebar-item-title">{{ mod.title }}</h4>
          </div>
          <span class="material-symbols-outlined sidebar-arrow">
            {{ mod.id == moduleId ? 'play_circle' : 'chevron_right' }}
          </span>
        </div>
      </div>

      <div v-else class="sidebar-loading">Loading...</div>

    </aside>

    <!-- main content -->
    <main class="main-content">

      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading lesson data...</p>
      </div>

      <div v-else-if="dashboardData" class="dashboard-container">

        <!-- breadcrumb -->
        <nav class="breadcrumb">
          <span>Course</span>
          <span class="material-symbols-outlined bc-arrow">chevron_right</span>
          <span class="bc-current">Module {{ currentModuleIndex + 1 }}</span>
        </nav>

        <!-- hero section -->
        <section class="hero-section">
          <div class="hero-text">
            <h1 class="hero-title">
              Module {{ currentModuleIndex + 1 }}: {{ dashboardData.module?.title }}
            </h1>
            <p class="hero-desc">
              {{ dashboardData.module?.description || 'Explore the core concepts of this module and build your understanding step by step.' }}
            </p>
          </div>

          <div class="progress-card">
            <div class="circle-wrap">
              <svg class="circle-svg" viewBox="0 0 44 44">
                <circle cx="22" cy="22" r="18" fill="none" stroke="#e8edf3" stroke-width="4"/>
                <circle
                  cx="22" cy="22" r="18"
                  fill="none"
                  stroke="#ed4081"
                  stroke-width="4"
                  stroke-linecap="round"
                  stroke-dasharray="113"
                  :stroke-dashoffset="113 - (113 * dashboardData.progress_percent / 100)"
                  transform="rotate(-90 22 22)"
                  style="transition: stroke-dashoffset 0.6s ease;"
                />
              </svg>
              <span class="circle-pct">{{ dashboardData.progress_percent }}%</span>
            </div>
            <div class="progress-info">
              <p class="progress-label">Progress</p>
              <p class="progress-value">{{ dashboardData.completed_pages }} / {{ dashboardData.total_pages }} topics</p>
            </div>
          </div>
        </section>

        <!-- lesson plan header -->
        <div class="section-header">
          <h2 class="section-title">Lesson Plan</h2>
        </div>

        <!-- lesson list -->
        <div class="lesson-list">
          <div
            v-for="(page, index) in dashboardData.pages"
            :key="page.id"
            class="lesson-card"
            :class="page.status"
          >
            <div class="status-icon" :class="page.status">
              <span class="material-symbols-outlined">
                {{ page.status === 'completed' ? 'check' : page.status === 'active' ? 'play_arrow' : 'lock' }}
              </span>
            </div>

            <div class="lesson-details">
              <div class="lesson-meta">
                <span class="lesson-index">{{ currentModuleIndex + 1 }}.{{ index + 1 }}</span>
                <span class="lesson-type-badge" :class="page.status === 'active' ? 'pink-badge' : 'gray-badge'">
                  Lesson
                </span>
              </div>
              <h3 class="lesson-title">{{ page.title }}</h3>
              <p class="lesson-desc">Click to study this topic and complete the lesson.</p>
            </div>

            <button
              @click="goToLesson(page.id)"
              class="lesson-btn"
              :class="page.status"
              :disabled="page.status === 'locked'"
            >
              {{ page.status === 'completed' ? 'Review Again' : page.status === 'active' ? 'Start Lesson' : 'Locked' }}
            </button>
          </div>
        </div>

        <!-- post test banner -->
        <div class="posttest-banner">
          <div class="banner-text">
            <h2>Ready for the end-of-module assessment?</h2>
            <p>Complete all lessons to unlock the Post-test for Module {{ currentModuleIndex + 1 }}.</p>
          </div>
          <button class="banner-btn" disabled>
            Unlock Assessment
            <span class="material-symbols-outlined">arrow_forward</span>
          </button>
        </div>

      </div>
    </main>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useLearningStore } from '@/store/learningStore'; 

const route = useRoute();
const router = useRouter();
const learningStore = useLearningStore();

const courseId = computed(() => route.params.courseId);
const moduleId = computed(() => route.params.moduleId);

const dashboardData = ref(null);
const isLoading = ref(true);
const courseModules = ref([]); 

const currentModuleIndex = computed(() => {
  const idx = courseModules.value.findIndex(m => m.id == moduleId.value);
  return idx >= 0 ? idx : 0;
});

const loadDashboard = async (mId) => {
  isLoading.value = true;
  try {
    const res = await learningStore.fetchModuleDashboard(mId);
    if (res && res.chapterInfo) {
      dashboardData.value = {
        module: { title: res.chapterInfo.title, description: res.chapterInfo.description },
        progress_percent: res.chapterInfo.progressPercent,
        completed_pages: res.chapterInfo.completedCount,
        total_pages: res.chapterInfo.totalCount,
        pages: res.lessons 
      };
    }
  } catch (error) {
    console.error("Dashboard Load Error:", error);
  } finally {
    isLoading.value = false;
  }
};

const loadSidebar = async () => {
  await learningStore.fetchModules(courseId.value);
  courseModules.value = learningStore.modules;
};

onMounted(async () => {
  await loadSidebar();
  if (moduleId.value) {
    await loadDashboard(moduleId.value);
  } else if (courseModules.value.length > 0) {
    router.replace(`/courses/${courseId.value}/modules/${courseModules.value[0].id}`);
  }
});

watch(moduleId, async (newId) => {
  if (newId) await loadDashboard(newId);
});

const goToModule = (mId) => {
  if (moduleId.value == mId) return; 
  router.push(`/courses/${courseId.value}/modules/${mId}`);
};

const goToLesson = (pageId) => {
  if (!pageId) {
    alert("Page ID not found.");
    return;
  }
  router.push({
    name: 'LearningChapter',
    params: {
      courseId: courseId.value,
      moduleId: moduleId.value,
      pageId: pageId
    }
  });
};
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  min-height: 100vh;
  background-color: #faf9f7;
  font-family: 'DM Sans', 'Helvetica Neue', sans-serif;
}

.material-symbols-outlined { vertical-align: middle; }

/* sidebar */
.sidebar {
  width: 272px;
  background: white;
  border-right: 1px solid #e8edf3;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100vh;
  position: sticky;
  top: 0;
  overflow-y: auto;
}

.sidebar-nav {
  padding: 1.25rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-bottom: 1px solid #f1f5f9;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.88rem;
  color: #64748b;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.18s;
  text-align: left;
  font-family: inherit;
}

.nav-btn:hover {
  background: #f1f5f9;
  color: #1a1a1a;
}

.sidebar-section-label {
  padding: 1.25rem 1.25rem 0.5rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
}

.sidebar-modules {
  padding: 0.5rem 0.75rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 10px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.18s;
  border: 1px solid transparent;
}

.sidebar-item:hover { background: #f8f9fb; }

.sidebar-item.active {
  background: white;
  border-color: #ffc7db;
  box-shadow: 0 2px 8px rgba(237,64,129,0.08);
}

.sidebar-item-text {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding-right: 8px;
}

.sidebar-item-num {
  font-size: 0.72rem;
  font-weight: 700;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 6px;
}

.in-progress-tag {
  background: #fce7ef;
  color: #ed4081;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 99px;
}

.sidebar-item-title {
  margin: 0;
  font-size: 0.88rem;
  font-weight: 600;
  color: #334155;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.sidebar-item.active .sidebar-item-title { color: #1a1a1a; }

.sidebar-arrow {
  font-size: 18px;
  color: #cbd5e1;
  flex-shrink: 0;
}

.sidebar-item.active .sidebar-arrow { color: #ed4081; }

.sidebar-loading {
  text-align: center;
  padding: 3rem 1rem;
  color: #94a3b8;
  font-size: 0.875rem;
}

/* main */
.main-content {
  flex: 1;
  overflow-y: auto;
  background: #faf9f7;
  padding: 3rem 3.5rem;
}

.dashboard-container {
  max-width: 860px;
  margin: 0 auto;
}

/* breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 1.75rem;
}

.bc-arrow { font-size: 16px; }
.bc-current { color: #475569; font-weight: 700; }

/* hero */
.hero-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2.5rem;
  margin-bottom: 3rem;
  background: white;
  border: 1px solid #e8edf3;
  border-radius: 20px;
  padding: 2rem 2.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.hero-text { flex: 1; }

.hero-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1a1a1a;
  margin: 0 0 0.75rem;
  line-height: 1.3;
  letter-spacing: -0.4px;
}

.hero-desc {
  font-size: 1rem;
  color: #64748b;
  line-height: 1.7;
  margin: 0;
  font-weight: 500;
}

.progress-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-shrink: 0;
  background: #faf9f7;
  border: 1px solid #e8edf3;
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  min-width: 190px;
}

.circle-wrap {
  position: relative;
  width: 56px;
  height: 56px;
  flex-shrink: 0;
}

.circle-svg { width: 56px; height: 56px; }

.circle-pct {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.82rem;
  font-weight: 800;
  color: #ed4081;
}

.progress-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 4px;
}

.progress-value {
  font-size: 1rem;
  font-weight: 800;
  color: #1a1a1a;
  margin: 0;
}

/* section */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: #1a1a1a;
  margin: 0;
}

/* lesson list */
.lesson-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 3rem;
}

.lesson-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  background: white;
  border: 1.5px solid #e8edf3;
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.lesson-card.active {
  border-color: #ffc7db;
  box-shadow: 0 4px 16px rgba(237,64,129,0.10);
}

.lesson-card.locked {
  opacity: 0.55;
  background: #f8f9fb;
}

.lesson-card:not(.locked):hover {
  border-color: #ffc7db;
  box-shadow: 0 4px 12px rgba(237,64,129,0.08);
}

.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.status-icon.completed { background: #c7ffc7; color: #0A703C; }
.status-icon.active { background: #fce7ef; color: #ed4081; }
.status-icon.locked { background: #f1f5f9; color: #94a3b8; }
.status-icon .material-symbols-outlined { font-size: 26px; }

.lesson-details { flex: 1; }

.lesson-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.lesson-index {
  font-size: 0.78rem;
  font-weight: 700;
  color: #94a3b8;
}

.lesson-type-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
}

.pink-badge { background: #fce7ef; color: #ed4081; }
.gray-badge { background: #f1f5f9; color: #64748b; }

.lesson-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 4px;
}

.lesson-desc {
  font-size: 0.88rem;
  color: #94a3b8;
  margin: 0;
  font-weight: 500;
}

.lesson-btn {
  padding: 10px 22px;
  border-radius: 99px;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  border: 1.5px solid transparent;
  transition: all 0.18s;
  white-space: nowrap;
  font-family: inherit;
}

.lesson-btn.completed {
  background: white;
  color: #64748b;
  border-color: #e2e8f0;
}

.lesson-btn.completed:hover {
  border-color: #94a3b8;
  color: #1a1a1a;
}

.lesson-btn.active {
  background: #ed4081;
  color: white;
  box-shadow: 0 4px 12px rgba(237, 64, 129, 0.22);
}

.lesson-btn.active:hover {
  background: #d13570;
  transform: translateY(-1px);
}

.lesson-btn.locked {
  background: transparent;
  color: #94a3b8;
  cursor: not-allowed;
}

/* post test banner */
.posttest-banner {
  background: linear-gradient(135deg, #ed4081 0%, #d13570 100%);
  border-radius: 20px;
  padding: 2.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  gap: 2rem;
  box-shadow: 0 8px 24px rgba(237,64,129,0.25);
}

.banner-text h2 {
  font-size: 1.35rem;
  font-weight: 800;
  margin: 0 0 0.6rem;
  line-height: 1.3;
}

.banner-text p {
  margin: 0;
  font-size: 0.95rem;
  opacity: 0.88;
  font-weight: 500;
  max-width: 480px;
  line-height: 1.55;
}

.banner-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  color: #ed4081;
  border: none;
  padding: 14px 28px;
  border-radius: 99px;
  font-weight: 800;
  font-size: 0.95rem;
  cursor: not-allowed;
  opacity: 0.85;
  flex-shrink: 0;
  font-family: inherit;
}

/* loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
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
@media (max-width: 1024px) {
  .hero-section { flex-direction: column; }
  .progress-card { width: 100%; }
  .main-content { padding: 2rem; }
}

@media (max-width: 768px) {
  .layout-wrapper { flex-direction: column; }
  .sidebar { width: 100%; height: auto; position: static; border-right: none; border-bottom: 1px solid #e8edf3; }
  .main-content { padding: 1.5rem 1rem; }
  .lesson-card { flex-direction: column; text-align: center; gap: 1rem; }
  .status-icon { margin: 0 auto; }
  .lesson-meta { justify-content: center; }
  .lesson-btn { width: 100%; }
  .posttest-banner { flex-direction: column; text-align: center; padding: 2rem; }
  .banner-btn { width: 100%; justify-content: center; }
}
</style>