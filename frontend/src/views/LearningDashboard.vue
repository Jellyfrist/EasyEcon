<template>
  <div v-if="dashboardData" class="dashboard-container">
    <section class="header-card">
      <div class="header-text">
        <nav class="breadcrumb">หลักสูตร > <span>{{ dashboardData.module?.title }}</span></nav>
        <h1>{{ dashboardData.module?.title }}</h1>
        <p>{{ dashboardData.module?.description }}</p>
      </div>
      
      <div class="progress-box">
        <div class="circle-chart" :style="`background: conic-gradient(#e91e63 ${dashboardData.progress_percent}%, #f1f5f9 0);`">
          <div class="inner-circle"><h3>{{ dashboardData.progress_percent }}%</h3></div>
        </div>
        <div class="progress-info">
          <p>ความคืบหน้า</p>
          <small>{{ dashboardData.completed_pages }} จาก {{ dashboardData.total_pages }} หัวข้อ</small>
        </div>
      </div>
    </section>

    <div class="lesson-list">
      <div v-for="page in dashboardData.pages" :key="page.id" class="lesson-card" :class="{ completed: page.status === 'completed' }">
        <div class="status-icon" :class="{ done: page.status === 'completed' }">
          <span class="material-symbols-outlined">
            {{ page.status === 'completed' ? 'check_circle' : (page.status === 'active' ? 'play_circle' : 'lock') }}
          </span>
        </div>
        <div class="details">
          <small class="type-badge">{{ page.type }}</small>
          <h4>{{ page.title }}</h4>
          <p class="subtitle">{{ page.subtitle }}</p>
        </div>
        <button 
          @click="goToLesson(page)" 
          class="action-btn" 
          :class="{ outline: page.status === 'completed' }"
          :disabled="page.status === 'locked'"
        >
          {{ page.status === 'completed' ? 'ทบทวนอีกครั้ง' : (page.status === 'locked' ? 'ล็อกอยู่' : 'เข้าสู่บทเรียน') }}
        </button>
      </div>
    </div>
  </div>
  <div v-else class="loading">
    <div class="spinner"></div>
    <p>กำลังดึงข้อมูลบทเรียน...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useLearningStore } from '@/store/learningStore'; 

const route = useRoute();
const router = useRouter();
const learningStore = useLearningStore();

const dashboardData = ref(null);

onMounted(async () => {
  try {
    const moduleId = route.params.moduleId; 
    const res = await learningStore.fetchModuleDashboard(moduleId);
    
    if (res && res.chapterInfo) {
      dashboardData.value = {
        module: {
          title: res.chapterInfo.title,
          description: res.chapterInfo.description
        },
        progress_percent: res.chapterInfo.progressPercent,
        completed_pages: res.chapterInfo.completedCount,
        total_pages: res.chapterInfo.totalCount,
        pages: res.lessons 
      };
    }
  } catch (error) {
    console.error("ไม่สามารถดึงข้อมูลคอร์สเรียนได้:", error);
  }
});

const goToLesson = (page) => {
  if (page.status !== 'locked') {
    router.push(`/course/${route.params.moduleId}/lesson/${page.id}`);
  }
};
</script>

<style scoped>
.dashboard-container { max-width: 1000px; margin: 0 auto; padding: 2rem; }
.header-card { display: flex; justify-content: space-between; align-items: center; background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 2rem; border: 1px solid #f1f5f9;}
.breadcrumb { font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem; }
.breadcrumb span { color: #e91e63; font-weight: 600; }
.header-text h1 { font-size: 1.8rem; color: #0f172a; margin-bottom: 0.5rem; }
.header-text p { color: #64748b; }
.progress-box { display: flex; align-items: center; gap: 1rem; background: #f8fafc; padding: 1rem 1.5rem; border-radius: 12px; }
.circle-chart { width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: background 0.5s ease; }
.inner-circle { width: 56px; height: 56px; background: #f8fafc; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.inner-circle h3 { color: #0f172a; margin: 0; font-size: 1.1rem; }
.progress-info p { margin: 0; font-weight: 600; color: #1e293b; }
.progress-info small { color: #64748b; }

.lesson-list { display: flex; flex-direction: column; gap: 1rem; }
.lesson-card { display: flex; align-items: center; background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; transition: all 0.2s; }
.lesson-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.lesson-card.completed { border-left: 4px solid #10b981; }
.status-icon { margin-right: 1.5rem; color: #94a3b8; }
.status-icon.done { color: #10b981; }
.status-icon .material-symbols-outlined { font-size: 28px; }
.details { flex: 1; }
.type-badge { background: #f1f5f9; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; color: #64748b; margin-bottom: 4px; display: inline-block; }
.details h4 { margin: 0 0 4px 0; font-size: 1.1rem; color: #1e293b; }
.subtitle { margin: 0; font-size: 0.85rem; color: #64748b; }

.action-btn { background: #e91e63; color: white; padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; transition: all 0.2s; }
.action-btn:hover:not(:disabled) { background: #d81b60; }
.action-btn.outline { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
.action-btn.outline:hover { background: #e2e8f0; }
.action-btn:disabled { background: #f1f5f9; color: #94a3b8; cursor: not-allowed; }

.loading { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 50vh; color: #64748b; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: #e91e63; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>