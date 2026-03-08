<template>
  <div class="dashboard">

    <div class="page-card">

      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="$router.back()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
          </button>
          <div class="header-text">
            <p class="breadcrumb">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
              Course #{{ courseId }}
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 18l6-6-6-6"/></svg>
              Exams
            </p>
            <h1 class="page-title">My Exam Template</h1>
            <p class="page-subtitle">Manage all exam templates for this course</p>
          </div>
        </div>
        <button class="btn-create" @click.stop="openCreateExam">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
          Create New Exam
        </button>
      </div>

      <!-- Filter bar -->
      <div class="filter-bar">
        <div class="filter-bar-top">
          <span class="filter-bar-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
            Filter
          </span>
          <div class="search-box">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            <input v-model="searchQuery" type="text" placeholder="Search exams…" />
            <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
          </div>
        </div>
        <div class="filter-bar-bottom">
          <div class="filter-group">
            <span class="filter-label">Type</span>
            <div class="filter-pills">
              <button :class="['pill', { active: filterType === 'all' }]"                          @click="filterType = 'all'">All</button>
              <button :class="['pill pill-midterm', { active: filterType === 'midterm' }]"         @click="filterType = 'midterm'">Midterm</button>
              <button :class="['pill pill-final', { active: filterType === 'final' }]"           @click="filterType = 'final'">Final</button>
              <button :class="['pill pill-summer', { active: filterType === 'summer' }]"          @click="filterType = 'summer'">Summer</button>
              <button :class="['pill pill-quiz', { active: filterType === 'quiz' }]"            @click="filterType = 'quiz'">Quiz</button>
            </div>
          </div>
          <div class="filter-divider"></div>
          <div class="filter-group">
            <span class="filter-label">Status</span>
            <div class="filter-pills">
              <button :class="['pill', { active: filterStatus === 'all' }]"                        @click="filterStatus = 'all'">All</button>
              <button :class="['pill pill-open',   { active: filterStatus === 'public' }]"         @click="filterStatus = 'public'">
                <span class="status-dot"></span>Published
              </button>
              <button :class="['pill pill-closed', { active: filterStatus === 'draft' }]"          @click="filterStatus = 'draft'">Draft</button>
            </div>
          </div>
        </div>
      </div>

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
            <button class="btn-primary" @click="launchExam(exam)">
              Launch Exam
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

// --- Load ---
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

onMounted(() => { loadExams() })

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
/* ── Dashboard wrapper ── */
.dashboard {
  min-height: 100vh;
  padding: 2rem;
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ── Page Card (header + filter combined) ── */
.page-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(237, 64, 129, 0.22);
}

/* ── Header ── */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: linear-gradient(135deg, var(--primary-pink) 0%, #f06292 100%);
  padding: 1.5rem 1.75rem;
  position: relative;
  overflow: hidden;
}

.header::before {
  content: '';
  position: absolute;
  right: -40px; top: -40px;
  width: 160px; height: 160px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  pointer-events: none;
}

.header::after {
  content: '';
  position: absolute;
  right: 60px; bottom: -50px;
  width: 110px; height: 110px;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
  pointer-events: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  z-index: 1;
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.4);
  background: rgba(255,255,255,0.15);
  color: white;
  cursor: pointer;
  transition: all 0.18s ease;
  flex-shrink: 0;
  backdrop-filter: blur(4px);
}

.back-btn:hover {
  background: rgba(255,255,255,0.28);
  border-color: rgba(255,255,255,0.7);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  color: rgba(255,255,255,0.75);
  font-weight: 500;
}

.breadcrumb svg {
  flex-shrink: 0;
  opacity: 0.7;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--white);
  line-height: 1.15;
  letter-spacing: -0.01em;
}

.page-subtitle {
  font-size: 0.8rem;
  font-weight: 400;
  color: rgba(255,255,255,0.78);
  margin: 0;
}

/* Create button (lives in header, white ghost style) */
.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1.1rem;
  background: rgba(255,255,255,0.18);
  border: 1.5px solid rgba(255,255,255,0.45);
  border-radius: var(--radius-md);
  color: var(--white);
  font-size: 0.84rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.18s ease;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(4px);
  flex-shrink: 0;
}

.btn-create:hover {
  background: rgba(255,255,255,0.30);
  border-color: rgba(255,255,255,0.75);
}

/* ── Filter Bar ── */
.filter-bar {
  border-top: 1px solid rgba(237, 64, 129, 0.15);
}

.filter-bar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: var(--primary-pink);
  padding: 0.6rem 1rem;
}

.filter-bar-title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  white-space: nowrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(255, 255, 255, 0.18);
  border: 1.5px solid rgba(255, 255, 255, 0.35);
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  min-width: 200px;
  transition: all 0.2s;
}

.search-box:focus-within {
  background: rgba(255, 255, 255, 0.28);
  border-color: rgba(255, 255, 255, 0.7);
}

.search-box svg { color: rgba(255,255,255,0.8); flex-shrink: 0; }

.search-box input {
  border: none;
  outline: none;
  font-size: 0.82rem;
  font-family: inherit;
  background: transparent;
  color: var(--white);
  width: 100%;
}

.search-box input::placeholder { color: rgba(255,255,255,0.65); }

.search-clear {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.25);
  border: none;
  cursor: pointer;
  color: white;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  flex-shrink: 0;
  transition: background 0.15s;
}

.search-clear:hover { background: rgba(255,255,255,0.4); }

.filter-bar-bottom {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  background: var(--white);
  padding: 0.625rem 1rem;
}

.filter-divider {
  width: 1.5px;
  height: 24px;
  background: var(--card-border);
  flex-shrink: 0;
  border-radius: 2px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.07em;
  white-space: nowrap;
  flex-shrink: 0;
}

.filter-pills {
  display: flex;
  gap: 0.3rem;
  align-items: center;
  flex-wrap: wrap;
}

.pill {
  padding: 0.28rem 0.7rem;
  border-radius: 999px;
  border: 1.5px solid var(--card-border);
  background: transparent;
  font-size: 0.76rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 0.15s ease;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  line-height: 1;
}

.pill:hover:not(.active) {
  background: var(--light-pink);
  color: var(--primary-pink);
  border-color: var(--primary-pink);
}

.pill.active { background: var(--primary-pink);    color: var(--white); border-color: var(--primary-pink); }
.pill-midterm.active { background: #2563eb;                 color: #fff;         border-color: #2563eb; }
.pill-final.active { background: #d97706;                 color: #fff;         border-color: #d97706; }
.pill-summer.active { background: var(--forest-green);     color: #fff;         border-color: var(--forest-green); }
.pill-quiz.active { background: #7c3aed;                 color: #fff;         border-color: #7c3aed; }
.pill-open.active { background: var(--forest-green);     color: #fff;         border-color: var(--forest-green); }
.pill-closed.active { background: var(--text-muted);       color: #fff;         border-color: var(--text-muted); }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--forest-green);
  flex-shrink: 0;
  box-shadow: 0 0 0 2px rgba(10, 112, 60, 0.2);
}

.pill-open.active .status-dot {
  background: #fff;
  box-shadow: 0 0 0 2px rgba(255,255,255,0.35);
}

/* ── Stats Bar ── */
.stats-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.875rem;
}

.stat-card {
  background: var(--white);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 1.125rem 1.375rem;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-num {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1;
}

.stat-label {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* ── Exam List ── */
.exam-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.exam-card {
  background: var(--white);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.exam-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.exam-card.published {
  border-left: 3px solid var(--forest-green);
}

.exam-card-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.exam-type-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  white-space: nowrap;
  flex-shrink: 0;
}

.exam-type-badge.midterm { background: #eff6ff;              color: #2563eb; }
.exam-type-badge.final { background: var(--light-yellow);  color: #92400e; }
.exam-type-badge.summer { background: var(--light-green);   color: var(--forest-green); }
.exam-type-badge.quiz { background: #faf5ff;              color: #7c3aed; }

.exam-info { min-width: 0; }

.exam-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 0.375rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.exam-meta {
  display: flex;
  gap: 0.625rem;
  flex-wrap: wrap;
}

.exam-meta span {
  font-size: 0.775rem;
  color: var(--text-muted);
}

.exam-card-right {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  flex-shrink: 0;
}

.status-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
}

.status-badge.published { background: var(--light-green); color: var(--forest-green); }
.status-badge.draft { background: var(--gray-light);  color: var(--text-muted); }

.action-buttons { display: flex; gap: 6px; }

.icon-btn {
  width: 34px;
  height: 34px;
  border: 1.5px solid var(--card-border);
  background: var(--white);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 0.15s ease;
}

.icon-btn:hover { background: var(--gray-light); }
.icon-btn.danger:hover { background: #fef2f2; border-color: #fca5a5; color: #dc2626; }

/* ── Buttons ── */
.btn-primary {
  background: var(--primary-pink);
  color: var(--white);
  border: none;
  border-radius: var(--radius-md);
  padding: 0.55rem 1.25rem;
  font-size: 0.84rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
  transition: background 0.15s ease, transform 0.15s ease;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-ghost {
  background: transparent;
  color: var(--text-muted);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  padding: 0.55rem 1.125rem;
  font-size: 0.84rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.btn-ghost:hover { background: var(--gray-light); color: var(--text-main); border-color: var(--text-muted); }

.btn-danger {
  background: #dc2626;
  color: var(--white);
  border: none;
  border-radius: var(--radius-md);
  padding: 0.55rem 1.125rem;
  font-size: 0.84rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.btn-danger:hover { background: #b91c1c; }

/* ── Empty state ── */
.empty-state {
  text-align: center;
  padding: 4rem 1.5rem;
  background: var(--white);
  border-radius: var(--radius-lg);
  border: 1.5px dashed var(--card-border);
}

.empty-state p {
  color: var(--text-muted);
  font-size: 0.9375rem;
  margin-bottom: 1.125rem;
}

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(30, 35, 60, 0.5);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 2rem;
}

.modal {
  background: var(--white);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
}

.modal.modal-sm { max-width: 420px; }

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.375rem 1.625rem;
  border-bottom: 2px solid var(--gray-light);
}

.modal-header h2 {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-main);
}

.modal-body {
  padding: 1.375rem 1.625rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-footer {
  padding: 1.125rem 1.625rem;
  border-top: 2px solid var(--gray-light);
  display: flex;
  justify-content: flex-end;
  gap: 0.625rem;
}

.delete-msg {
  font-size: 0.9rem;
  color: var(--text-main);
  line-height: 1.6;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .dashboard { padding: 1.25rem 1rem; }
  .stats-bar { grid-template-columns: repeat(2, 1fr); }
  .exam-card { flex-direction: column; align-items: flex-start; }
  .exam-card-right { width: 100%; justify-content: space-between; }
  .filter-bar-top { flex-direction: column; align-items: stretch; gap: 0.5rem; }
  .search-box { min-width: unset; }
  .filter-bar-bottom { flex-direction: column; align-items: stretch; gap: 0.5rem; }
  .filter-divider { width: 100%; height: 1.5px; }
  .filter-group { flex-wrap: wrap; }
}
</style>