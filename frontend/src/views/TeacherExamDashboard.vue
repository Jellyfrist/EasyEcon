<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <button class="back-btn" @click="$router.back()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
        </button>
        <div>
          <p class="breadcrumb">Course #{{ courseId }}</p>
          <h1 class="page-title">My Exam Template</h1>
        </div>
      </div>
      <button class="btn-primary" @click.stop="openCreateExam">
       + Create New Exam
      </button>
    </div>

    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-card">
        <span class="stat-num">{{ stats.total }}</span>
        <span class="stat-label">Total Exams</span>
      </div>
      <div class="stat-card">
        <span class="stat-num">{{ stats.published }}</span>
        <span class="stat-label">Published</span>
      </div>
      <div class="stat-card">
        <span class="stat-num">{{ stats.draft }}</span>
        <span class="stat-label">Drafts</span>
      </div>
      <div class="stat-card">
        <span class="stat-num">{{ stats.questions }}</span>
        <span class="stat-label">Total Questions</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input v-model="searchQuery" type="text" placeholder="search..." />
      </div>
      <div class="filter-tabs">
        <span>TYPE</span>
        <button :class="['tab',{ active: filterType === 'all' }]" @click="filterType='all'">All</button>
        <button :class="['tab',{ active: filterType === 'midterm' }]" @click="filterType='midterm'">Midterm</button>
        <button :class="['tab',{ active: filterType === 'final' }]" @click="filterType='final'">Final</button>
        <button :class="['tab',{ active: filterType === 'summer' }]" @click="filterType='summer'">Summer</button>
        <button :class="['tab',{ active: filterType === 'quiz' }]" @click="filterType='quiz'">Quiz</button>

      </div>
      <div class="filter-tabs">
        <span>STATUS</span>
        <button :class="['tab',{ active: filterStatus === 'all' }]" @click="filterStatus='all'">All</button>
        <button :class="['tab',{ active: filterStatus === 'public' }]" @click="filterStatus='public'">Public</button>
        <button :class="['tab',{ active: filterStatus === 'draft' }]" @click="filterStatus='draft'">Draft</button>
      </div>
    </div>

    <!-- Exam List -->
    <div class="exam-list">
      <div v-if="filteredExams.length === 0" class="empty-state">
        <p>No exams in this course yet</p>
        <button class="btn-primary" @click="openCreateModal">Create First Exam</button>
      </div>

      <div
        v-for="exam in filteredExams"
        :key="exam.id"
        class="exam-card"
        :class="{ published: exam.is_published }"
      >
        <div class="exam-card-left">
          <div class="exam-type-badge" :class="exam.exam_type">
            {{ examTypeLabels[exam.exam_type] }}
          </div>
          <div class="exam-info">
            <h3 class="exam-title">{{ exam.title }}</h3>
            <div class="exam-meta">
              <span v-if="exam.academic_year">Academic Year {{ exam.academic_year }}</span>
              <span v-if="exam.term">{{ exam.term }}</span>
              <span>{{ exam.question_count }} Questions</span>
              <span>{{ exam.total_points }} Points</span>
            </div>
          </div>
        </div>

        <button class="btn-primary" @click="launchExam(exam)">
            Launch Exam
        </button>

        <div class="exam-card-right">
          <span :class="['status-badge', exam.is_published ? 'published' : 'draft']">
            {{ exam.is_published ? 'Published' : 'Draft' }}
          </span>
          <div class="action-buttons">
            <button class="icon-btn" title="Edit" @click="editExam(exam)">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button
              class="icon-btn"
              :title="exam.is_published ? 'Unpublish' : 'Publish'"
              @click="togglePublish(exam)"
            >
              <svg v-if="!exam.is_published" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
            <button class="icon-btn danger" title="ลบ" @click="confirmDelete(exam)">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h2>Confirm Deletion</h2>
          </div>
          <div class="modal-body">
            <p class="delete-msg">Are you sure you want to delete the exam <strong>"{{ deletingExam?.title }}"</strong>?</p>
          </div>
          <div class="modal-footer">
            <button class="btn-ghost" @click="showDeleteModal = false">Cancel</button>
            <button class="btn-danger" @click="deleteExam">Delete Exam</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '@/services/examService'

const router = useRouter()
const route = useRoute()
const courseId = computed(() => route.params.courseId)

// --- State ---
const searchQuery = ref('')
const filterType = ref('all')
const filterStatus = ref('all')
const showDeleteModal = ref(false)
const deletingExam = ref(null)
const isLoading = ref(false)
const isDeleting = ref(false)
const error = ref(null)

const examTypeLabels = {
  midterm: "Midterm",
  final: "Final",
  summer: "Summer",
  quiz: "Quiz"
}

const stats = computed(() => ({
  total: exams.value.length,
  published: exams.value.filter(e => e.is_published).length,
  draft: exams.value.filter(e => !e.is_published).length,
  questions: exams.value.reduce((s,e)=>s+(e.question_count??0),0)
}))

// --- Data ---
const exams = ref([]) 

async function loadExams() {
  isLoading.value = true
  error.value = null
  try {
    const res = await examService.listTemplates(courseId.value)
    exams.value = res.data ?? res
  } catch (err) {
    console.error('Failed to load exams', err)
    error.value = 'Failed to load exams, please try again'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadExams()
})

// --- Computed ---
const filteredExams = computed(() => {
  return exams.value.filter(e => {
    const matchType = filterType.value === 'all' || e.exam_type === filterType.value
    const matchStatus = filterStatus.value === 'all' || e.is_published === (filterStatus.value === 'public')
    const matchSearch = !searchQuery.value || e.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchType && matchStatus && matchSearch
  })
})

// --- Navigation ---
function openCreateExam() {
  router.push({ name: 'ExamEditor', params: { courseId: courseId.value } })
}

function editExam(exam) {
  router.push({ name: 'ExamEditor', params: { courseId: courseId.value, templateId: exam.id } })
}

function launchExam(exam) {
  router.push({ name: 'TeacherExamLaunch', params: { templateId: exam.id } })
}

// --- Actions ---
async function togglePublish(exam) {
  const original = exam.is_published
  const idx = exams.value.findIndex(e => e.id === exam.id)
  if (idx !== -1) exams.value[idx].is_published = !original

  try {
    await examService.updateTemplate(exam.id, { is_published: !original })
  } catch (err) {
    console.error('Failed to toggle publish', err)
    if (idx !== -1) exams.value[idx].is_published = original
    error.value = 'Cannot save update, please try again.'
  }
}

function confirmDelete(exam) {
  deletingExam.value = exam
  showDeleteModal.value = true
}

async function deleteExam() {
  isDeleting.value = true
  error.value = null
  try {
    await examService.deleteTemplate(deletingExam.value.id)
    exams.value = exams.value.filter(e => e.id !== deletingExam.value.id)
    showDeleteModal.value = false
    deletingExam.value = null
  } catch (err) {
    console.error('Failed to delete exam', err)
    error.value = 'Cannot delete exam, please try again.'
  } finally {
    isDeleting.value = false
  }
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.dashboard {
  font-family: 'Sarabun', sans-serif;
  min-height: 100vh;
  padding: 32px;
  max-width: 1100px;
  margin: 0 auto;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}
.header-left { display: flex; align-items: center; gap: 14px; }
.back-btn {
  width: 38px; height: 38px;
  border: 1.5px solid #dde1ea;
  background: #fff;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #555;
  transition: all 0.15s;
}
.back-btn:hover { background: #f0f1f5; }
.breadcrumb { font-size: 12px; color: #9399aa; margin-bottom: 2px; }
.page-title { font-family: 'IBM Plex Sans Thai', sans-serif; font-size: 22px; font-weight: 700; color: #1a1d2e; }

/* Stats */
.stats-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}
.stat-card {
  background: #fff;
  border: 1px solid #e8eaf2;
  border-radius: 14px;
  padding: 18px 22px;
  display: flex; flex-direction: column; gap: 4px;
}
.stat-num { font-size: 28px; font-weight: 700; color: #1a1d2e; line-height: 1; }
.stat-label { font-size: 12.5px; color: #7c82a0; }

/* Filters */
.filters {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; margin-bottom: 18px; flex-wrap: wrap;
}
.search-box {
  display: flex; align-items: center; gap: 9px;
  background: #fff; border: 1.5px solid #e2e5ef;
  border-radius: 10px; padding: 9px 14px;
  min-width: 260px;
}
.search-box svg { color: #9399aa; flex-shrink: 0; }
.search-box input {
  border: none; outline: none; font-size: 14px;
  font-family: 'Sarabun', sans-serif; background: transparent; color: #1a1d2e; width: 100%;
}
.filter-tabs { display: flex; gap: 6px; }
.tab {
  padding: 8px 18px; border-radius: 9px; border: 1.5px solid #e2e5ef;
  background: #fff; font-size: 13.5px; font-family: 'Sarabun', sans-serif;
  cursor: pointer; color: #555; transition: all 0.15s;
}
.tab.active { background: #1a1d2e; color: #fff; border-color: #1a1d2e; }
.tab:hover:not(.active) { background: #f0f1f5; }

/* Exam List */
.exam-list { display: flex; flex-direction: column; gap: 10px; }
.exam-card {
  background: #fff;
  border: 1.5px solid #e8eaf2;
  border-radius: 14px;
  padding: 18px 22px;
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px;
  transition: box-shadow 0.15s, border-color 0.15s;
}
.exam-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.07); border-color: #d0d4e5; }
.exam-card.published { border-left: 3px solid #22c55e; }

.exam-card-left { display: flex; align-items: center; gap: 16px; flex: 1; min-width: 0; }
.exam-type-badge {
  font-size: 11px; font-weight: 600; padding: 4px 12px;
  border-radius: 999px; white-space: nowrap; flex-shrink: 0;
}
.exam-type-badge.midterm { background: #eff6ff; color: #2563eb; }
.exam-type-badge.final { background: #fef3c7; color: #d97706; }

.exam-info { min-width: 0; }
.exam-title { font-size: 15px; font-weight: 600; color: #1a1d2e; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.exam-meta { display: flex; gap: 10px; flex-wrap: wrap; }
.exam-meta span { font-size: 12.5px; color: #7c82a0; }

.exam-card-right { display: flex; align-items: center; gap: 14px; flex-shrink: 0; }
.status-badge {
  font-size: 12px; font-weight: 500; padding: 4px 12px; border-radius: 999px;
}
.status-badge.published { background: #dcfce7; color: #16a34a; }
.status-badge.draft { background: #f3f4f6; color: #6b7280; }

.action-buttons { display: flex; gap: 6px; }
.icon-btn {
  width: 34px; height: 34px;
  border: 1.5px solid #e2e5ef; background: #fff;
  border-radius: 9px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #555; transition: all 0.15s;
}
.icon-btn:hover { background: #f0f1f5; }
.icon-btn.danger:hover { background: #fef2f2; border-color: #fca5a5; color: #dc2626; }

/* Empty state */
.empty-state {
  text-align: center; padding: 64px 24px;
  background: #fff; border-radius: 14px; border: 1.5px dashed #d0d4e5;
}
.empty-icon { font-size: 40px; margin-bottom: 14px; }
.empty-state p { color: #7c82a0; font-size: 15px; margin-bottom: 18px; }

/* Buttons */
.btn-primary {
  background: #1a1d2e; color: #fff;
  border: none; border-radius: 10px;
  padding: 10px 20px; font-size: 14px;
  font-family: 'Sarabun', sans-serif; font-weight: 500;
  cursor: pointer; display: flex; align-items: center; gap: 7px;
  transition: background 0.15s;
}
.btn-primary:hover:not(:disabled) { background: #2d3251; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-secondary {
  background: #f0f1f5; color: #1a1d2e;
  border: none; border-radius: 10px;
  padding: 10px 20px; font-size: 14px;
  font-family: 'Sarabun', sans-serif; font-weight: 500;
  cursor: pointer; transition: background 0.15s;
}
.btn-secondary:hover:not(:disabled) { background: #e2e5ef; }
.btn-secondary:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-ghost {
  background: transparent; color: #555;
  border: 1.5px solid #e2e5ef; border-radius: 10px;
  padding: 10px 20px; font-size: 14px;
  font-family: 'Sarabun', sans-serif;
  cursor: pointer; transition: background 0.15s;
}
.btn-ghost:hover { background: #f7f8fc; }

.btn-danger {
  background: #dc2626; color: #fff;
  border: none; border-radius: 10px;
  padding: 10px 20px; font-size: 14px;
  font-family: 'Sarabun', sans-serif; font-weight: 500;
  cursor: pointer; transition: background 0.15s;
}
.btn-danger:hover { background: #b91c1c; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(10, 12, 22, 0.55);
  backdrop-filter: blur(3px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 24px;
}
.modal {
  background: #fff; border-radius: 18px;
  width: 100%; max-width: 600px;
  max-height: 90vh; overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.18);
}
.modal.modal-sm { max-width: 420px; }

.modal-header {
  padding: 22px 26px 0;
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #f0f1f5; padding-bottom: 18px;
}
.modal-header h2 { font-size: 17px; font-weight: 700; color: #1a1d2e; }
.close-btn {
  width: 32px; height: 32px; border: none; background: #f0f1f5;
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #555;
}
.close-btn:hover { background: #e2e5ef; }

.modal-body { padding: 22px 26px; display: flex; flex-direction: column; gap: 16px; }

.form-row { display: flex; gap: 14px; }
.two-col { flex-wrap: wrap; }
.two-col .form-group { flex: 1; min-width: 180px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group.full { flex: 1; }
label { font-size: 13px; font-weight: 600; color: #3a3d52; }
.required { color: #dc2626; }
input[type="text"],
input[type="number"],
select,
textarea {
  border: 1.5px solid #e2e5ef; border-radius: 9px;
  padding: 9px 13px; font-size: 14px;
  font-family: 'Sarabun', sans-serif; color: #1a1d2e;
  outline: none; transition: border-color 0.15s;
  background: #fdfdff;
}
input:focus, select:focus, textarea:focus { border-color: #1a1d2e; }
textarea { resize: vertical; }

.options-row { flex-wrap: wrap; gap: 10px; }
.toggle-label {
  display: flex; align-items: center; gap: 8px;
  cursor: pointer; font-size: 13.5px; color: #3a3d52;
}
.toggle-label input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; accent-color: #1a1d2e; }

.modal-footer {
  padding: 18px 26px;
  border-top: 1px solid #f0f1f5;
  display: flex; justify-content: flex-end; gap: 10px;
}

.delete-msg { font-size: 14.5px; color: #3a3d52; line-height: 1.6; }

/* Responsive */
@media (max-width: 768px) {
  .dashboard { padding: 20px 16px; }
  .stats-bar { grid-template-columns: repeat(2, 1fr); }
  .filters { flex-direction: column; align-items: stretch; }
  .search-box { min-width: unset; }
  .exam-card { flex-direction: column; align-items: flex-start; }
  .exam-card-right { width: 100%; justify-content: space-between; }
}
</style>