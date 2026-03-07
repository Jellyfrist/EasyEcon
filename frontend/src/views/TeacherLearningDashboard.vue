<template>
  <div class="dashboard-page">
    
    <header class="top-navbar">
      <button @click="router.push(`/teacher/courses/${courseId}/edit`)" class="back-btn">
        <span class="material-symbols-outlined">arrow_back</span>
        Back To Courses
      </button>
    </header>

    <main class="main-container">
      
      <div class="page-header">
        <div class="title-area">
          <h1 class="page-title">Learning Lessons</h1>
          <p class="page-subtitle">จัดการโครงสร้างโมดูลและเนื้อหาบทเรียนทั้งหมดในคอร์สนี้</p>
        </div>
        
        <button @click="goToModuleEditor" class="btn-primary">
          <span class="material-symbols-outlined">add</span> 
          Manage Modules
        </button>
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
        <p class="empty-title">Not Found</p>
        <p class="empty-desc">ยังไม่มีการสร้างโมดูลหรือบทเรียนในคอร์สนี้<br>กดปุ่ม "Manage Modules" ด้านบนเพื่อเริ่มต้น</p>
      </div>

      <div v-else class="modules-list">
        
        <div v-for="(mod, index) in modules" :key="mod.id" class="module-card">
          
          <div class="module-header" @click="toggleModule(mod)">
            <div class="module-header-left">
              <span class="material-symbols-outlined chevron-icon" :class="{ 'rotated': mod.isExpanded }">
                chevron_right
              </span>
              <h2 class="module-title">
                <span class="module-badge">Module {{ index + 1 }}</span>
                {{ mod.title }}
              </h2>
            </div>
            
            <button @click.stop="createNewLesson(mod.id)" class="btn-outline-primary">
              <span class="material-symbols-outlined icon-small">add</span> เพิ่มบทเรียน
            </button>
          </div>

          <div v-show="mod.isExpanded" class="module-content">
            <div v-if="mod.learning_pages && mod.learning_pages.length > 0" class="lessons-list">
              
              <div v-for="(page, pIndex) in mod.learning_pages" :key="page.id" 
                   class="lesson-item" 
                   @click="editLesson(page.id, mod.id)">
                
                <div class="lesson-info">
                  <div class="lesson-number">{{ pIndex + 1 }}</div>
                  <div class="lesson-details">
                    <h3 class="lesson-title">{{ page.title || 'Untitled Lesson' }}</h3>
                    <div class="lesson-status">
                      <span v-if="page.is_published" class="status-badge published">
                        <span class="material-symbols-outlined icon-micro">done_all</span> เผยแพร่แล้ว
                      </span>
                      <span v-else class="status-badge draft">
                        <span class="material-symbols-outlined icon-micro">draft</span> ฉบับร่าง
                      </span>
                    </div>
                  </div>
                </div>

                <div class="lesson-action">
                  <button class="btn-edit-icon">
                    <span class="material-symbols-outlined">edit</span>
                  </button>
                </div>

              </div>

            </div>
            
            <div v-else class="empty-lessons">
              <span class="material-symbols-outlined">info</span>
              ยังไม่ได้สร้างเนื้อหาบทเรียนในโมดูลนี้
            </div>
          </div>

        </div>

      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import learningService from '@/services/learningService' 

const route = useRoute()
const router = useRouter()
const courseId = route.params.courseId

const modules = ref([])
const loading = ref(false)
const error = ref(null)

const loadModules = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await learningService.listModules(courseId)
    const fetchedModules = res.data || []

    for (let mod of fetchedModules) {
      try {
        const pagesRes = await learningService.listPages(mod.id);
        mod.learning_pages = pagesRes.data || [];
        
        mod.isExpanded = false; 
      } catch (err) {
        console.warn(`ดึงข้อมูลหน้าย่อยของโมดูล ${mod.id} ไม่สำเร็จ`, err);
        mod.learning_pages = []; 
        mod.isExpanded = false;
      }
    }

    modules.value = fetchedModules;

  } catch (err) {
    console.error("Failed to fetch dashboard data:", err)
    error.value = "Network Error - เกิดข้อผิดพลาดในการโหลดข้อมูล"
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

const goToModuleEditor = () => {
  router.push(`/teacher/modules/${courseId}`)
}

const createNewLesson = (moduleId) => {
  router.push(`/learning/${courseId}/${moduleId}/edit`);
}

const editLesson = (pageId, moduleId) => {
  router.push(`/learning/${courseId}/${moduleId}/edit/${pageId}`);
}
</script>

<style scoped>
/* ================= Base Styles ================= */
.dashboard-page {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Sarabun', 'Inter', sans-serif;
  padding-bottom: 5rem;
}

.material-symbols-outlined { vertical-align: middle; }

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
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2.5rem; flex-wrap: wrap; gap: 1.5rem; }
.page-title { font-size: 2.2rem; font-weight: 800; color: #0f172a; margin: 0 0 0.5rem 0; letter-spacing: -0.5px; }
.page-subtitle { color: #64748b; margin: 0; font-size: 1rem; font-weight: 500; }

.btn-primary { display: flex; align-items: center; gap: 8px; background-color: #f43f5e; color: white; border: none; padding: 12px 24px; border-radius: 99px; font-weight: 700; font-size: 0.95rem; cursor: pointer; box-shadow: 0 4px 12px rgba(244, 63, 94, 0.2); transition: all 0.2s; }
.btn-primary:hover { background-color: #e11d48; transform: translateY(-2px); }

/* ================= States ================= */
.state-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 5rem 0; color: #64748b; font-weight: 600; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: #f43f5e; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }
.error-box { background-color: #fef2f2; color: #ef4444; padding: 1.5rem; border-radius: 16px; border: 1px solid #fee2e2; display: flex; align-items: center; gap: 12px; font-weight: 600; }

.empty-state { text-align: center; padding: 5rem 2rem; background-color: white; border-radius: 24px; border: 1px solid #e2e8f0; box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
.empty-title { font-size: 1.75rem; font-weight: 800; color: #f43f5e; margin: 0 0 1rem 0; }
.empty-desc { color: #64748b; font-size: 1rem; margin: 0; line-height: 1.6; }

/* ================= Module Cards (Accordion Style) ================= */
.modules-list { display: flex; flex-direction: column; gap: 1rem; animation: slideUp 0.4s ease-out; }
@keyframes slideUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

.module-card {
  background-color: white;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
  overflow: hidden; 
  transition: all 0.2s ease;
}

.module-card:hover { border-color: #cbd5e1; }

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem;
  cursor: pointer;
  background-color: white;
  transition: background-color 0.2s;
}

.module-header:hover { background-color: #f8fafc; }

.module-header-left { display: flex; align-items: center; gap: 12px; }

.chevron-icon { color: #94a3b8; font-size: 1.5rem; transition: transform 0.3s ease; }
.chevron-icon.rotated { transform: rotate(90deg); color: #f43f5e; }

.module-title { font-size: 1.25rem; font-weight: 800; color: #0f172a; margin: 0; display: flex; align-items: center; gap: 12px; }
.module-badge { background-color: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 8px; font-size: 0.8rem; font-family: monospace; font-weight: 700; border: 1px solid #e2e8f0; }

.btn-outline-primary { display: flex; align-items: center; gap: 6px; background-color: #fff1f2; color: #e11d48; border: 1px solid #ffe4e6; padding: 8px 16px; border-radius: 12px; font-weight: 700; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; }
.btn-outline-primary:hover { background-color: #e11d48; color: white; border-color: #e11d48; }

.module-content {
  padding: 0 1.5rem 1.5rem 4rem;
  border-top: 1px solid #f1f5f9;
  background-color: #fafbfc;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* ================= Lessons List (Inside Module) ================= */
.lessons-list { display: flex; flex-direction: column; gap: 8px; padding-top: 1.5rem; border-left: 2px solid #ffe4e6; padding-left: 12px; }

.lesson-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-radius: 12px; background-color: white; border: 1px solid #e2e8f0; cursor: pointer; transition: all 0.2s ease; }
.lesson-item:hover { border-color: #fecaca; box-shadow: 0 4px 12px rgba(244, 63, 94, 0.08); transform: translateX(4px); }

.lesson-info { display: flex; align-items: center; gap: 12px; }
.lesson-number { width: 32px; height: 32px; background-color: #fff1f2; color: #f43f5e; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem; }
.lesson-title { font-size: 1.05rem; font-weight: 700; color: #1e293b; margin: 0 0 4px 0; transition: color 0.2s; }
.lesson-item:hover .lesson-title { color: #e11d48; }

.status-badge { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; }
.status-badge.published { background-color: #ecfdf5; color: #059669; }
.status-badge.draft { background-color: #fff7ed; color: #ea580c; }
.icon-micro { font-size: 12px; }

.lesson-action { opacity: 0; transition: opacity 0.2s; }
.lesson-item:hover .lesson-action { opacity: 1; }
.btn-edit-icon { width: 36px; height: 36px; border-radius: 10px; background-color: #f8fafc; border: 1px solid #e2e8f0; color: #94a3b8; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; }
.btn-edit-icon:hover { color: #f43f5e; border-color: #fecaca; background-color: #fff1f2; }

/* Empty Lessons */
.empty-lessons { display: flex; align-items: center; gap: 8px; padding-top: 1.5rem; color: #94a3b8; font-size: 0.95rem; font-weight: 500; font-style: italic; }
</style>