<template>
  <div class="dashboard-page">
    
    <main class="main-container">
      
      <div class="hero-section">
        
        <div class="welcome-box">
          <h1 class="greeting">
            {{ greeting }}, <span class="highlight-name">{{ authStore.fullName || 'Teacher' }}</span> 👋
          </h1>
          <p class="subtitle">Welcome back to your teaching dashboard.</p>
          
          <button class="btn-primary mt-action" @click="router.push('/teacher/courses/create')">
            <span class="material-symbols-outlined">add</span> Create New Course
          </button>
        </div>

        <div class="stats-card">
          <h2 class="stats-title">You currently manage</h2>
          
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value text-rose">{{ courseStore.courses.length }}</div>
              <div class="stat-label">Courses</div>
            </div>
            
            <div class="divider"></div>
            
            <div class="stat-item">
              <div class="stat-value text-emerald">{{ totalFlashcardSets }}</div>
              <div class="stat-label">Flashcard Sets</div>
            </div>
            
            <div class="divider"></div>
            
            <div class="stat-item">
              <div class="stat-value text-blue">{{ totalExams }}</div>
              <div class="stat-label">Exam Templates</div>
            </div>
          </div>
        </div>
        
      </div>

      <div class="courses-section">
        <h2 class="section-title">My Courses</h2>

        <div v-if="courseStore.loading" class="state-container">
          <div class="spinner"></div>
          <p>กำลังโหลดข้อมูลคอร์สเรียน...</p>
        </div>

        <div v-else-if="courseStore.error" class="error-box">
          <span class="material-symbols-outlined">error</span>
          <div class="error-text">
            <p>{{ courseStore.error }}</p>
            <button class="btn-outline-red mt-2" @click="courseStore.fetchMyCourses()">Try Again</button>
          </div>
        </div>

        <div v-else-if="courseStore.courses.length === 0" class="empty-state">
          <span class="material-symbols-outlined empty-icon">school</span>
          <h3 class="empty-title">No courses yet</h3>
          <p class="empty-desc">Create your first course to get started.</p>
          <button class="btn-primary mt-4" @click="router.push('/teacher/courses/create')">
            <span class="material-symbols-outlined">add</span> Create Course
          </button>
        </div>

        <div v-else class="course-grid">
          
          <div v-for="course in courseStore.courses" :key="course.id" class="course-card">
            <div class="course-card-content">
              
              <div class="course-header">
                <span class="course-label">Course Overview</span>
              </div>
              
              <h3 class="course-title">{{ course.title }}</h3>
              <p class="course-desc">{{ course.description || 'No description provided for this course.' }}</p>

              <div class="badges-row">
                <span class="badge badge-module">
                  <span class="material-symbols-outlined icon-xs">view_module</span> 
                  {{ course.module_count ?? 0 }} modules
                </span>
                <span class="badge badge-flashcard">
                  <span class="material-symbols-outlined icon-xs">style</span> 
                  {{ course.flashcard_set_count ?? 0 }} sets
                </span>
                <span class="badge badge-exam">
                  <span class="material-symbols-outlined icon-xs">quiz</span> 
                  {{ course.exam_template_count ?? 0 }} exams
                </span>
              </div>
              
            </div>

            <div class="course-card-action">
              <button class="btn-edit-course" @click="router.push(`/teacher/courses/${course.id}/edit`)">
                <span class="material-symbols-outlined icon-sm">edit</span> Manage Course
              </button>
            </div>
            
          </div>
          
        </div>

      </div>

    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'
import { useCourseStore } from '@/store/courseStore'

const router = useRouter()
const authStore = useAuthStore()
const courseStore = useCourseStore()

// Greeting based on time of day
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good Morning'
  if (hour < 18) return 'Good Afternoon'
  return 'Good Evening'
})

// Sum all flashcard_set_count from each course in the list
const totalFlashcardSets = computed(() =>
  courseStore.courses.reduce((sum, c) => sum + (c.flashcard_set_count ?? 0), 0)
)

// Sum all exam_template_count from each course in the list
const totalExams = computed(() =>
  courseStore.courses.reduce((sum, c) => sum + (c.exam_template_count ?? 0), 0)
)

// Load teacher's own courses on mount
onMounted(async () => {
  await courseStore.fetchMyCourses()
})
</script>

<style scoped>
/* ================= Base Styles ================= */
.dashboard-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Prompt', sans-serif;
}

.material-symbols-outlined { vertical-align: middle; }
.main-container { max-width: 1100px; margin: 0 auto; padding: 3rem 1.5rem; }

/* ================= 1. Hero Section (Welcome & Stats) ================= */
.hero-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 4rem;
}

@media (min-width: 900px) {
  .hero-section {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.welcome-box {
  flex: 1;
}

.greeting {
  font-size: 2.5rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
  letter-spacing: -1px;
}

.highlight-name { color: #f43f5e; }
.subtitle { color: #64748b; font-size: 1.1rem; margin: 0; font-weight: 500; }
.mt-action { margin-top: 1.5rem; }

/* Stats Card */
.stats-card {
  background: white;
  border-radius: 24px;
  padding: 2rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
  min-width: 400px;
}

.stats-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #334155;
  margin: 0 0 1.5rem 0;
}

.stats-grid {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label { color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }

.text-rose { color: #f43f5e; }
.text-emerald { color: #10b981; }
.text-blue { color: #3b82f6; }

.divider { width: 1px; height: 50px; background-color: #e2e8f0; }

@media (max-width: 600px) {
  .stats-card { min-width: 100%; }
  .stats-grid { flex-direction: column; gap: 1rem; }
  .divider { width: 100%; height: 1px; }
  .stat-item { flex-direction: row; justify-content: space-between; width: 100%; }
  .stat-value { font-size: 1.75rem; }
}

/* ================= 2. Courses Section ================= */
.section-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 1.5rem 0;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 1rem;
}

/* Grid Layout */
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* Course Card */
.course-card {
  background-color: white;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  overflow: hidden;
}

.course-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
}

.course-card-content { padding: 1.75rem; flex: 1; }

.course-label {
  display: inline-block;
  background-color: #f1f5f9;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.course-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
  line-height: 1.3;
}

.course-desc {
  color: #64748b;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 1.5rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Badges */
.badges-row { display: flex; flex-wrap: wrap; gap: 8px; }

.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
}

.badge-module { background-color: #f0fdf4; color: #15803d; border: 1px solid #dcfce7; }
.badge-flashcard { background-color: #fff1f2; color: #be123c; border: 1px solid #ffe4e6; }
.badge-exam { background-color: #eff6ff; color: #1d4ed8; border: 1px solid #dbeafe; }
.icon-xs { font-size: 14px; }

/* Card Action Area */
.course-card-action {
  padding: 1.25rem 1.75rem;
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

/* ================= Buttons ================= */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: #f43f5e;
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 99px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(244, 63, 94, 0.25);
  transition: all 0.2s;
}

.btn-primary:hover { background-color: #e11d48; transform: translateY(-2px); box-shadow: 0 6px 15px rgba(225, 29, 72, 0.3); }

.btn-edit-course {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background-color: #10b981;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit-course:hover { background-color: #059669; }
.icon-sm { font-size: 18px; }

.btn-outline-red { background: white; border: 1px solid #fecaca; color: #ef4444; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.2s; }
.btn-outline-red:hover { background: #fef2f2; border-color: #ef4444; }

/* ================= States ================= */
.state-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 5rem 0; color: #64748b; font-weight: 600; }
.spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: #f43f5e; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 100% { transform: rotate(360deg); } }

.error-box { background-color: #fef2f2; color: #ef4444; padding: 1.5rem; border-radius: 16px; border: 1px solid #fee2e2; display: flex; align-items: flex-start; gap: 12px; font-weight: 600; }
.error-text p { margin: 0 0 8px 0; }

.empty-state { text-align: center; padding: 5rem 2rem; background-color: white; border-radius: 24px; border: 2px dashed #cbd5e1; }
.empty-icon { font-size: 4rem; color: #cbd5e1; margin-bottom: 1rem; }
.empty-title { font-size: 1.5rem; font-weight: 800; color: #334155; margin: 0 0 0.5rem 0; }
.empty-desc { color: #64748b; font-size: 1rem; margin: 0; }
</style>