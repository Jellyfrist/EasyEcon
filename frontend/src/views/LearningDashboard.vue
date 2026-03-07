<template>
  <div class="layout-wrapper">
    
    <aside class="sidebar">
      
      <div class="sidebar-nav">
        <button class="nav-btn" @click="router.push('/student/dashboard')">
          <span class="material-symbols-outlined icon-home">home</span> หน้าแรก
        </button>
        <button class="nav-btn bg-slate-50" @click="router.push(`/student/courses/${courseId}`)">
          <span class="material-symbols-outlined">arrow_back</span> กลับไปที่คลังบทเรียน
        </button>
      </div>

      <div class="module-list-header">
        <p>รายชื่อบทเรียน ({{ courseModules.length }} บท)</p>
      </div>

      <div class="sidebar-modules" v-if="courseModules.length > 0">
        <div 
          v-for="(mod, index) in courseModules" 
          :key="mod.id" 
          class="module-item" 
          :class="{ active: mod.id == moduleId }"
          @click="goToModule(mod.id)"
        >
          <div class="module-title-box">
            <span class="mod-num" :class="{ 'text-rose-500': mod.id == moduleId }">
              บทที่ {{ index + 1 }} <span v-if="mod.id == moduleId" class="status-text">(กำลังเรียน)</span>
            </span>
            <h4 class="mod-name" :class="{ 'text-slate-800': mod.id == moduleId }">{{ mod.title }}</h4>
          </div>
          <span v-if="mod.id == moduleId" class="material-symbols-outlined text-rose-500 text-sm icon-play">play_circle</span>
          <span v-else class="material-symbols-outlined text-slate-300 text-sm">chevron_right</span>
        </div>
      </div>
      <div v-else class="text-center py-10 text-slate-400 text-sm">กำลังโหลด...</div>

    </aside>

    <main class="main-content">
      
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>กำลังโหลดข้อมูลบทเรียน...</p>
      </div>

      <div v-else-if="dashboardData" class="dashboard-container">
        
        <nav class="breadcrumb">หลักสูตร <span class="material-symbols-outlined text-sm mx-1">chevron_right</span> <span>บทที่ {{ currentModuleIndex + 1 }}</span></nav>
        
        <section class="overview-section">
          <div class="text-content">
            <h1 class="course-title">บทที่ {{ currentModuleIndex + 1 }}: <br/>{{ dashboardData.module?.title }}</h1>
            <p class="course-desc">{{ dashboardData.module?.description || 'ทำความเข้าใจหลักการพื้นฐานของวิชาเศรษฐศาสตร์ ศึกษาเกี่ยวกับความขาดแคลน ค่าเสียโอกาส และปัญหาพื้นฐานทางเศรษฐกิจที่สังคมต้องเผชิญ พร้อมวิวัฒนาการของแนวคิดทางเศรษฐกิจ' }}</p>
          </div>

          <div class="progress-pill">
            <div class="circle-chart" :style="`background: conic-gradient(#e11d48 ${dashboardData.progress_percent}%, #f1f5f9 0);`">
              <div class="inner-circle"><span class="percent-text">{{ dashboardData.progress_percent }}%</span></div>
            </div>
            <div class="progress-info">
              <p>ความคืบหน้า</p>
              <h4>{{ dashboardData.completed_pages }} จาก {{ dashboardData.total_pages }} หัวข้อ</h4>
            </div>
          </div>
        </section>

        <div class="plan-header">
          <h2>แผนการเรียน</h2>
          <span class="total-time">ระยะเวลารวม: 1 ชม. 45 นาที</span>
        </div>

        <div class="lesson-list">
          <div 
            v-for="(page, index) in dashboardData.pages" 
            :key="page.id" 
            class="lesson-card" 
            :class="page.status"
          >
            <div class="status-icon-wrapper" :class="page.status">
              <span class="material-symbols-outlined icon">
                {{ page.status === 'completed' ? 'check' : (page.status === 'active' ? 'play_arrow' : 'lock') }}
              </span>
            </div>
            
            <div class="lesson-details">
              <div class="lesson-meta">
                <span class="lesson-index">หัวข้อ {{ currentModuleIndex + 1 }}.{{ index + 1 }}</span>
                <span class="badge-type" :class="page.status === 'active' ? 'bg-rose-100 text-rose-600' : 'bg-slate-100 text-slate-500'">วิดีโอ</span>
              </div>
              <h3 class="lesson-title">{{ page.title }}</h3>
              <p class="lesson-desc">รายละเอียดเนื้อหาของหัวข้อนี้เพื่อปูพื้นฐานความเข้าใจ</p>
            </div>

            <button 
              @click="goToLesson(page.id)" 
              class="action-btn" 
              :class="page.status"
              :disabled="page.status === 'locked'"
            >
              {{ page.status === 'completed' ? 'ทบทวนอีกครั้ง' : (page.status === 'active' ? 'เข้าสู่บทเรียน' : 'ล็อกอยู่') }}
            </button>
          </div>
        </div>

        <div class="post-test-banner mt-12">
          <div class="banner-content">
            <h2>พร้อมรับการประเมินผลท้ายบท?</h2>
            <p>เรียนให้ครบทุกหัวข้อเพื่อปลดล็อกแบบทดสอบ Post-test ของบทที่ {{ currentModuleIndex + 1 }}</p>
          </div>
          <button class="btn-unlock" disabled>
            ปลดล็อกการสอบ <span class="material-symbols-outlined ml-1 text-lg">arrow_forward</span>
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
  return courseModules.value.findIndex(m => m.id == moduleId.value) >= 0 
         ? courseModules.value.findIndex(m => m.id == moduleId.value) 
         : 0;
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
    router.replace(`/student/courses/${courseId.value}/modules/${courseModules.value[0].id}`);
  }
});

watch(moduleId, async (newId) => {
  if (newId) await loadDashboard(newId);
});

const goToModule = (mId) => {
  if (moduleId.value == mId) return; 
  router.push(`/student/courses/${courseId.value}/modules/${mId}`);
};

const goToLesson = (pageId) => {
  if (!pageId) {
    alert("ไม่พบรหัสเนื้อหา (Page ID)");
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
/* ================= Base Layout ================= */
.layout-wrapper { display: flex; min-height: 100vh; background-color: #f8fafc; font-family: 'Sarabun', 'Inter', sans-serif; }
.material-symbols-outlined { vertical-align: middle; }

/* ================= SIDEBAR ================= */
.sidebar { width: 280px; background-color: white; border-right: 1px solid #e2e8f0; display: flex; flex-direction: column; flex-shrink: 0; height: 100vh; position: sticky; top: 0; overflow-y: auto; }
.sidebar-nav { padding: 1.5rem; display: flex; flex-direction: column; gap: 8px; border-bottom: 1px solid #f1f5f9; }
.nav-btn { display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-radius: 12px; font-weight: 700; font-size: 0.95rem; color: #475569; background: transparent; border: none; cursor: pointer; transition: all 0.2s; justify-content: flex-start; }
.nav-btn:hover { background-color: #f1f5f9; color: #0f172a; }
.icon-home { color: #1e293b; }

.module-list-header { padding: 1.5rem 1.5rem 0.75rem; color: #94a3b8; font-size: 0.8rem; font-weight: 700; }
.sidebar-modules { padding: 0 1rem 2rem; display: flex; flex-direction: column; gap: 8px; }

/* Sidebar Items */
.module-item { display: flex; justify-content: space-between; align-items: center; padding: 16px; border-radius: 16px; cursor: pointer; transition: all 0.2s; border: 1px solid transparent; background-color: #f8fafc; }
.module-item:hover { border-color: #e2e8f0; }
.module-item.active { background-color: white; border-color: #f43f5e; box-shadow: 0 4px 15px rgba(244, 63, 94, 0.08); }

.module-title-box { display: flex; flex-direction: column; gap: 4px; padding-right: 10px; }
.mod-num { font-size: 0.75rem; font-weight: 800; color: #94a3b8; }
.status-text { font-size: 0.7rem; font-weight: 800; color: #f43f5e; margin-left: 4px; }
.text-rose-500 { color: #e11d48 !important; }
.mod-name { margin: 0; font-size: 0.9rem; font-weight: 700; color: #475569; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* ================= MAIN CONTENT ================= */
.main-content { flex: 1; padding: 3rem 4rem; overflow-y: auto; background-color: white; }
.dashboard-container { max-width: 950px; margin: 0 auto; }

.breadcrumb { font-size: 0.85rem; color: #94a3b8; font-weight: 700; display: flex; align-items: center; margin-bottom: 1.5rem; }
.breadcrumb span:last-child { color: #f43f5e; }

/* Overview Section */
.overview-section { display: flex; justify-content: space-between; align-items: flex-start; gap: 3rem; margin-bottom: 3.5rem; }
.text-content { flex: 1; }
.course-title { font-size: 3.2rem; font-weight: 900; color: #0f172a; line-height: 1.15; margin: 0 0 1.5rem 0; letter-spacing: -1.5px; }
.course-desc { font-size: 1.1rem; color: #64748b; line-height: 1.7; font-weight: 500; }

/* Progress Pill */
.progress-pill { background-color: white; border-radius: 20px; padding: 1.25rem 2rem 1.25rem 1.25rem; display: flex; align-items: center; gap: 1.5rem; border: 1px solid #f1f5f9; box-shadow: 0 10px 30px -5px rgba(0,0,0,0.06); flex-shrink: 0; min-width: 250px; }
.circle-chart { width: 68px; height: 68px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.inner-circle { width: 54px; height: 54px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.percent-text { color: #e11d48; font-weight: 800; font-size: 1.15rem; }
.progress-info p { margin: 0 0 4px 0; font-size: 0.8rem; color: #94a3b8; font-weight: 700; }
.progress-info h4 { margin: 0; font-size: 1.15rem; color: #0f172a; font-weight: 800; }

/* Plan Header */
.plan-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem; }
.plan-header h2 { font-size: 1.6rem; font-weight: 800; color: #0f172a; margin: 0; }
.total-time { font-size: 0.9rem; font-weight: 700; color: #64748b; }

/* Lesson List */
.lesson-list { display: flex; flex-direction: column; gap: 1.25rem; }
.lesson-card { display: flex; align-items: center; padding: 1.5rem; border-radius: 20px; background: white; border: 2px solid #f1f5f9; transition: all 0.2s ease; }

/* Card States */
.lesson-card.completed { border-color: #f1f5f9; }
.lesson-card.active { border-color: #fecdd3; box-shadow: 0 10px 25px -5px rgba(244, 63, 94, 0.15); }
.lesson-card.locked { opacity: 0.6; background-color: #f8fafc; }

/* Icon Wrapper */
.status-icon-wrapper { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1.5rem; flex-shrink: 0; }
.status-icon-wrapper.completed { background-color: #ecfdf5; color: #10b981; }
.status-icon-wrapper.active { background-color: #fff1f2; color: #e11d48; }
.status-icon-wrapper.locked { background-color: #f1f5f9; color: #94a3b8; }
.icon { font-size: 32px; }

/* Details */
.lesson-details { flex: 1; }
.lesson-meta { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.lesson-index { font-size: 0.85rem; font-weight: 800; color: #94a3b8; }
.badge-type { padding: 4px 10px; border-radius: 8px; font-size: 0.7rem; font-weight: 800; }

.lesson-title { margin: 0 0 6px 0; font-size: 1.25rem; font-weight: 800; color: #1e293b; }
.lesson-desc { margin: 0; font-size: 1rem; color: #64748b; font-weight: 500; }

/* Buttons */
.action-btn { padding: 12px 28px; border-radius: 99px; font-weight: 800; font-size: 0.95rem; cursor: pointer; border: 1px solid transparent; transition: all 0.2s; white-space: nowrap; }
.action-btn.completed { background-color: white; color: #64748b; border-color: #e2e8f0; }
.action-btn.completed:hover { border-color: #94a3b8; color: #0f172a; }
.action-btn.active { background-color: #e11d48; color: white; box-shadow: 0 4px 12px rgba(225, 29, 72, 0.25); }
.action-btn.active:hover { background-color: #be123c; transform: translateY(-2px); }
.action-btn.locked { background-color: transparent; color: #94a3b8; cursor: not-allowed; }

/* Post Test Banner */
.post-test-banner { background: linear-gradient(135deg, #e11d48, #be123c); border-radius: 24px; padding: 3rem; display: flex; justify-content: space-between; align-items: center; color: white; box-shadow: 0 15px 35px -10px rgba(225, 29, 72, 0.4); }
.banner-content h2 { font-size: 2rem; font-weight: 900; margin: 0 0 1rem 0; letter-spacing: -0.5px; }
.banner-content p { margin: 0; font-size: 1.1rem; opacity: 0.9; max-width: 550px; line-height: 1.6; font-weight: 500; }
.btn-unlock { background: white; color: #e11d48; border: none; padding: 16px 32px; border-radius: 99px; font-weight: 800; font-size: 1.05rem; display: flex; align-items: center; cursor: not-allowed; opacity: 0.9; }

/* Loading */
.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; color: #64748b; font-weight: 700; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: #e11d48; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 1024px) { .overview-section { flex-direction: column; gap: 2rem; } .progress-pill { width: 100%; justify-content: flex-start; } }
@media (max-width: 768px) {
  .layout-wrapper { flex-direction: column; }
  .sidebar { width: 100%; height: auto; position: static; border-right: none; border-bottom: 1px solid #e2e8f0; }
  .main-content { padding: 2rem 1.5rem; }
  .lesson-card { flex-direction: column; text-align: center; gap: 1.5rem; }
  .status-icon-wrapper { margin-right: 0; }
  .lesson-meta { justify-content: center; }
  .action-btn { width: 100%; }
  .post-test-banner { flex-direction: column; text-align: center; gap: 2rem; padding: 2rem; }
}
</style>