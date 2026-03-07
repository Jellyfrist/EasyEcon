<template>
  <div class="dashboard-page">
    
    <header class="top-navbar">
      <button @click="router.push({ name: 'Courses', params: { courseId: courseId } })" class="back-btn">
        <span class="material-symbols-outlined">arrow_back</span>
        Back To Course Dashboard
      </button>
    </header>

    <main class="main-container">
      
      <div class="page-header">
        <div class="title-area">
          <span class="course-label">Course #{{ courseId }}</span>
          <h1 class="page-title">Learning Modules</h1>
          <p class="page-subtitle">เลือกบทเรียนที่ต้องการศึกษาเพื่อเริ่มต้นการเรียนรู้</p>
        </div>
      </div>

      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p>กำลังโหลดข้อมูลบทเรียน...</p>
      </div>

      <div v-else-if="error" class="error-box">
        <span class="material-symbols-outlined">error</span>
        {{ error }}
      </div>

      <div v-else-if="modules.length === 0" class="empty-state">
        <div class="empty-icon">📚</div>
        <p class="empty-title">ไม่พบเนื้อหา</p>
        <p class="empty-desc">ขณะนี้ยังไม่มีการเพิ่มเนื้อหาบทเรียนในคอร์สนี้<br>โปรดรอคุณครูอัปเดตเนื้อหาในภายหลัง</p>
      </div>

      <div v-else class="modules-list">
        
        <div v-for="(mod, index) in modules" :key="mod.id" class="module-card">
          
          <div class="module-header" @click="toggleModule(mod)">
            <div class="module-header-left">
              <span class="material-symbols-outlined chevron-icon" :class="{ 'rotated': mod.isExpanded }">
                chevron_right
              </span>
              <h2 class="module-title" @click="goToLesson(mod.id)">
                <span class="module-badge">Module {{ index + 1 }}</span>
                {{ mod.title }}
              </h2>
            </div>
            
            <div class="module-header-right">
              <span class="lesson-count-badge">
                {{ mod.learning_pages?.length || 0 }} Lessons
              </span>
            </div>
          </div>

          <!-- <div v-show="mod.isExpanded" class="module-content">
            <div v-if="mod.learning_pages && mod.learning_pages.length > 0" class="lessons-list">
              
              <div v-for="(page, pIndex) in mod.learning_pages" :key="page.id" 
                   class="lesson-item" 
                   @click="goToLesson(page.id, mod.id)">
                
                <div class="lesson-info">
                  <div class="lesson-number">{{ pIndex + 1 }}</div>
                  <div class="lesson-details">
                    <h3 class="lesson-title">{{ page.title || 'Untitled Lesson' }}</h3>
                    <p class="lesson-subtitle">คลิกเพื่อเริ่มเรียนหัวข้อนี้</p>
                  </div>
                </div>

                <div class="lesson-action">
                   <span class="enter-btn-text">เข้าเรียน</span>
                   <span class="material-symbols-outlined action-arrow">arrow_forward</span>
                </div>

              </div>

            </div>
            
            <div v-else class="empty-lessons">
              <span class="material-symbols-outlined">info</span>
              ยังไม่มีเนื้อหาบทเรียนในโมดูลนี้
            </div>
          </div> -->

        </div>

      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import learningService from '@/services/learningService' 

const route = useRoute()
const router = useRouter()
const courseId = computed(() => route.params.courseId)

const modules = ref([])
const loading = ref(false)
const error = ref(null)

const loadModules = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await learningService.listModules(courseId.value)
    const fetchedModules = res.data || []

    for (let mod of fetchedModules) {
      try {
        const pagesRes = await learningService.listPages(mod.id);
        mod.learning_pages = (pagesRes.data || []).filter(p => p.is_published);
        
        mod.isExpanded = false;
      } catch (err) {
        console.warn(`ดึงข้อมูลหน้าย่อยของโมดูล ${mod.id} ไม่สำเร็จ`, err);
        mod.learning_pages = []; 
        mod.isExpanded = false;
      }
    }

    modules.value = fetchedModules;

  } catch (err) {
    console.error("Failed to fetch modules:", err)
    error.value = "เกิดข้อผิดพลาดในการโหลดข้อมูลบทเรียน"
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadModules()
})

const toggleModule = (mod) => {
  mod.isExpanded = !mod.isExpanded;
}

const goToLesson = (moduleId) => {
  router.push({
    name: 'LearningDashboard',
    params: {
      courseId: courseId.value,
      moduleId: moduleId
    }
  });
}
</script>

<style scoped>
/* ================= Base Styles ================= */
.dashboard-page {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Sarabun', sans-serif;
  padding-bottom: 5rem;
}

/* ================= Navbar ================= */
.top-navbar {
  background-color: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn { display: flex; align-items: center; gap: 8px; background: none; border: none; color: #64748b; font-weight: 700; font-size: 0.95rem; cursor: pointer; transition: color 0.2s; padding: 0; }
.back-btn:hover { color: #0f172a; }

/* ================= Main Content ================= */
.main-container { max-width: 900px; margin: 0 auto; padding: 2.5rem 1.5rem; }

/* ================= Header Section ================= */
.page-header { margin-bottom: 2.5rem; }
.course-label { font-size: 0.85rem; font-weight: 700; color: #e91e63; text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 0.5rem; }
.page-title { font-size: 2.2rem; font-weight: 800; color: #0f172a; margin: 0 0 0.5rem 0; letter-spacing: -0.5px; }
.page-subtitle { color: #64748b; margin: 0; font-size: 1rem; }

/* ================= States ================= */
.state-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 5rem 0; color: #64748b; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: #e91e63; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

.empty-state { text-align: center; padding: 5rem 2rem; background-color: white; border-radius: 24px; border: 1px solid #e2e8f0; }
.empty-icon { font-size: 4rem; margin-bottom: 1.5rem; }
.empty-title { font-size: 1.75rem; font-weight: 800; color: #e91e63; margin-bottom: 0.5rem; }
.empty-desc { color: #64748b; line-height: 1.6; }

/* ================= Module Cards (Accordion) ================= */
.modules-list { display: flex; flex-direction: column; gap: 1rem; }

.module-card {
  background-color: white;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  overflow: hidden; 
  transition: all 0.2s ease;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  cursor: pointer;
}

.module-header:hover { background-color: #f8fafc; }

.module-header-left { display: flex; align-items: center; gap: 12px; }

.chevron-icon { color: #94a3b8; font-size: 1.5rem; transition: transform 0.3s ease; }
.chevron-icon.rotated { transform: rotate(90deg); color: #e91e63; }

.module-title { font-size: 1.25rem; font-weight: 800; color: #0f172a; margin: 0; display: flex; align-items: center; gap: 12px; }
.module-badge { background-color: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; border: 1px solid #e2e8f0; }

.lesson-count-badge { font-size: 0.85rem; color: #64748b; background: #f8fafc; padding: 4px 12px; border-radius: 99px; border: 1px solid #e2e8f0; }

.module-content {
  padding: 0 1.5rem 1.5rem 4rem;
  border-top: 1px solid #f1f5f9;
  background-color: #fafbfc;
}

/* ================= Lessons List ================= */
.lessons-list { display: flex; flex-direction: column; gap: 8px; padding-top: 1.5rem; border-left: 2px solid #fce7f3; padding-left: 12px; }

.lesson-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-radius: 12px; background-color: white; border: 1px solid #e2e8f0; cursor: pointer; transition: all 0.2s ease; }
.lesson-item:hover { border-color: #f9a8d4; box-shadow: 0 4px 12px rgba(233, 30, 99, 0.08); transform: translateX(4px); }

.lesson-info { display: flex; align-items: center; gap: 12px; }
.lesson-number { width: 32px; height: 32px; background-color: #fce7f3; color: #e91e63; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; }
.lesson-title { font-size: 1.05rem; font-weight: 700; color: #1e293b; margin: 0; }
.lesson-subtitle { font-size: 0.8rem; color: #94a3b8; margin: 0; }

.lesson-action { display: flex; align-items: center; gap: 8px; opacity: 0.5; transition: all 0.2s; }
.lesson-item:hover .lesson-action { opacity: 1; color: #e91e63; }
.enter-btn-text { font-size: 0.85rem; font-weight: 700; }
.action-arrow { font-size: 18px; }

.empty-lessons { display: flex; align-items: center; gap: 8px; padding-top: 1.5rem; color: #94a3b8; font-style: italic; }
</style>