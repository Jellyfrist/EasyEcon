<template>
  <div class="page-wrapper">
    
    <header class="top-navbar">
      <button @click="router.push(`/teacher`)" class="back-btn">
        <span class="material-symbols-outlined">arrow_back</span>
        Back To Dashboard
      </button>
    </header>

    <div class="content-layout">
      
      <div class="left-col">
        <div class="card form-card">
          <h2 class="form-title">
            {{ isEditMode ? 'Edit Course' : 'Create New Course' }}
          </h2>
  
          <div class="form-group">
            <label>Course Title</label>
            <input v-model="title" class="input-field" type="text" placeholder="e.g. Microeconomics 101" maxlength="50" :disabled="store.loading" />
          </div>
  
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="description" class="input-field" placeholder="Short description of the course..." rows="4" :disabled="store.loading" />
          </div>
  
          <div v-if="store.error" class="error-msg">{{ store.error }}</div>
  
          <div class="btn-row">
            <button class="btn btn-primary" :disabled="store.loading || !title.trim()" @click="handleSubmit">
              {{ store.loading ? 'Saving...' : (isEditMode ? 'Update Course' : 'Create Course') }}
            </button>
  
            <button v-if="isEditMode" class="btn btn-danger" :disabled="store.loading" @click="handleDelete">
              Delete
            </button>
  
            <button class="btn btn-outline" :disabled="store.loading" @click="router.back()">
              Cancel
            </button>
          </div>
        </div>
      </div>

      <div v-if="isEditMode" class="right-col">
        
        <h3 class="section-subtitle">Manage Content</h3>

        <div class="action-list">
          
          <div class="mini-action-card" @click="router.push({ name: 'TeacherLearningDashboard', params: { courseId: courseId } })">
            <div class="card-left">
              <div class="icon-box bg-emerald-50 text-emerald-600">
                <span class="material-symbols-outlined">view_module</span>
              </div>
              <div class="text-box">
                <h4>Modules (Learn)</h4>
                <p>Ordered lessons with mini quizzes.</p>
              </div>
            </div>
            <div class="card-right">
              <span class="badge badge-module">{{ store.currentCourse?.module_count ?? 0 }}</span>
              <button class="btn-icon add-btn" @click.stop="router.push({ name: 'LearningModule', params: { courseId: courseId } })" title="New Module">
                <span class="material-symbols-outlined">add</span>
              </button>
            </div>
          </div>

          <div class="mini-action-card" @click="router.push({ name: 'TeacherFlashcardDashboard', params: { courseId: courseId } })">
            <div class="card-left">
              <div class="icon-box bg-rose-50 text-rose-600">
                <span class="material-symbols-outlined">style</span>
              </div>
              <div class="text-box">
                <h4>Flashcards</h4>
                <p>Stand-alone topics for review.</p>
              </div>
            </div>
            <div class="card-right">
              <span class="badge badge-flashcard">{{ store.currentCourse?.flashcard_set_count ?? 0 }}</span>
              <button class="btn-icon add-btn" @click.stop="router.push({ name: 'FlashcardEditor', params: { courseId: courseId } })" title="New Set">
                <span class="material-symbols-outlined">add</span>
              </button>
            </div>
          </div>

          <div class="mini-action-card disabled-card">
            <div class="card-left">
              <div class="icon-box bg-blue-50 text-blue-600">
                <span class="material-symbols-outlined">quiz</span>
              </div>
              <div class="text-box">
                <h4>Exams</h4>
                <p>Midterm and final banks.</p>
              </div>
            </div>
            <div class="card-right">
              <span class="badge badge-exam">{{ store.currentCourse?.exam_template_count ?? 0 }}</span>
              <button class="btn-icon add-btn" disabled>
                <span class="material-symbols-outlined">add</span>
              </button>
            </div>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { onMounted, onUnmounted, watch, ref, computed } from 'vue'
import { useCourseStore } from '@/store/courseStore'

const route = useRoute()
const router = useRouter()
const store = useCourseStore()

const courseId = computed(() => route.params.courseId)
const isEditMode = computed(() => !!courseId.value)

const title = ref('')
const description = ref('')

async function loadCourse() {
    await store.fetchCourse(courseId.value)
    if (store.currentCourse) {
        title.value = store.currentCourse.title
        description.value = store.currentCourse.description ?? ''
    }
}

onMounted(async () => {
    if (isEditMode.value) await loadCourse()
})

watch(courseId, async (newId) => {
    if (newId) await loadCourse()
})

onUnmounted(() => {
    store.clearCurrent()
})

const handleSubmit = async () => {
    if (!title.value.trim()) return

    const payload = {
        title: title.value.trim(),
        description: description.value.trim() || null
    }

    if (!isEditMode.value) {
        const created = await store.createCourse(payload)
        if (created) router.replace(`/teacher/courses/${created.id}/edit`)
    } else {
        await store.updateCourse(Number(courseId.value), payload)
    }
}

const handleDelete = async () => {
    if (!confirm('Are you sure? All content in this course will be deleted.')) return

    const ok = await store.deleteCourse(Number(courseId.value))
    if (ok) router.push('/teacher')
}
</script>

<style scoped>
.page-wrapper {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: 'Sarabun', 'Inter', sans-serif;
  padding-bottom: 5rem;
}

.top-navbar {
  background-color: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn {
  display: flex; align-items: center; gap: 8px;
  background: none; border: none; color: #64748b;
  font-weight: 700; font-size: 0.95rem; cursor: pointer;
}
.back-btn:hover { color: #0f172a; }

.content-layout {
  max-width: 1100px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: start;
}

@media (min-width: 900px) {
  .content-layout {
    grid-template-columns: 6fr 4fr;
  }
}

.form-card {
  background-color: white;
  padding: 2.5rem;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
}

.form-title { font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0 0 2rem 0; letter-spacing: -0.5px; }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; font-weight: 600; color: #64748b; margin-bottom: 0.5rem; font-size: 0.95rem; }

.input-field {
  width: 100%;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  font-size: 1rem;
  color: #334155;
  background-color: #f8fafc;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}
.input-field:focus { background-color: white; border-color: #f43f5e; }
textarea.input-field { resize: vertical; }

.btn-row { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 2rem; }
.btn { display: flex; align-items: center; justify-content: center; padding: 12px 24px; border-radius: 99px; font-weight: 700; font-size: 0.95rem; cursor: pointer; transition: all 0.2s; border: none; }
.btn-primary { background-color: #f43f5e; color: white; box-shadow: 0 4px 12px rgba(244, 63, 94, 0.2); }
.btn-primary:hover:not(:disabled) { background-color: #e11d48; transform: translateY(-2px); }
.btn-danger { background-color: #ef4444; color: white; }
.btn-danger:hover:not(:disabled) { background-color: #dc2626; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #64748b; font-weight: 700; }
.btn-outline:hover:not(:disabled) { background: #f8fafc; color: #0f172a; border-color: #cbd5e1; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }

.error-msg { color: #ef4444; font-size: 0.875rem; background: #fef2f2; border-radius: 12px; border: 1px solid #fee2e2; padding: 0.75rem 1rem; margin-bottom: 1rem; font-weight: 600; }

.section-subtitle { font-size: 1.25rem; font-weight: 800; color: #0f172a; margin: 0 0 1rem 0; }
.action-list { display: flex; flex-direction: column; gap: 1rem; }

.mini-action-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  padding: 1rem 1.25rem;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.mini-action-card:hover:not(.disabled-card) { border-color: #cbd5e1; transform: translateY(-2px); box-shadow: 0 8px 15px -5px rgba(0,0,0,0.05); }

.card-left { display: flex; align-items: center; gap: 1rem; }
.icon-box { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.bg-emerald-50 { background-color: #ecfdf5; } .text-emerald-600 { color: #059669; }
.bg-rose-50 { background-color: #fff1f2; } .text-rose-600 { color: #e11d48; }
.bg-blue-50 { background-color: #eff6ff; } .text-blue-600 { color: #2563eb; }

.text-box h4 { margin: 0 0 2px 0; font-size: 1rem; font-weight: 800; color: #1e293b; }
.text-box p { margin: 0; font-size: 0.8rem; color: #64748b; line-height: 1.3; }

.card-right { display: flex; align-items: center; gap: 12px; }

.badge { display: flex; align-items: center; justify-content: center; min-width: 24px; height: 24px; padding: 0 8px; border-radius: 99px; font-size: 0.75rem; font-weight: 800; }
.badge-module { background-color: #f0fdf4; color: #15803d; border: 1px solid #dcfce7; }
.badge-flashcard { background-color: #fff1f2; color: #be123c; border: 1px solid #ffe4e6; }
.badge-exam { background-color: #eff6ff; color: #1d4ed8; border: 1px solid #dbeafe; }

.btn-icon { width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background-color: #f8fafc; border: 1px solid #e2e8f0; color: #475569; cursor: pointer; transition: all 0.2s; }
.btn-icon:hover:not(:disabled) { background-color: white; color: #0f172a; border-color: #cbd5e1; }
.btn-icon:disabled { opacity: 0.5; cursor: not-allowed; }

.disabled-card { opacity: 0.7; cursor: not-allowed; }

@media (max-width: 600px) {
  .btn-row { flex-direction: column; gap: 0.5rem; }
  .btn-row .btn { width: 100%; }
}
</style>