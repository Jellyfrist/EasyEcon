<template>
  <div class="dashboard">

    <div class="page-card">

      <!-- Header: pink gradient top -->
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
            <h1 class="page-title">Exam Sessions</h1>
            <p class="page-subtitle">All exam sessions available for this course</p>
          </div>
        </div>
      </div>

      <!-- Filter bar: white bottom section -->
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
              <button :class="['pill pill-final',   { active: filterType === 'final' }]"           @click="filterType = 'final'">Final</button>
              <button :class="['pill pill-summer',  { active: filterType === 'summer' }]"          @click="filterType = 'summer'">Summer</button>
              <button :class="['pill pill-quiz',    { active: filterType === 'quiz' }]"            @click="filterType = 'quiz'">Quiz</button>
            </div>
          </div>
          <div class="filter-divider"></div>
          <div class="filter-group">
            <span class="filter-label">Status</span>
            <div class="filter-pills">
              <button :class="['pill', { active: filterStatus === 'all' }]"                        @click="filterStatus = 'all'">All</button>
              <button :class="['pill pill-open',   { active: filterStatus === 'open' }]"           @click="filterStatus = 'open'">
                <span class="status-dot"></span>Open
              </button>
              <button :class="['pill pill-closed', { active: filterStatus === 'closed' }]"         @click="filterStatus = 'closed'">Closed</button>
            </div>
          </div>
        </div>
      </div>

    </div>

    <div v-if="isLoading" class="loading-state">Loading exams...</div>

    <div v-else-if="filteredSessions.length === 0" class="empty-state">
      <p>No exams available in this course.</p>
    </div>

    <div v-else class="session-list">
      <div
        v-for="session in filteredSessions"
        :key="session.id"
        class="session-card"
        :class="{ 'is-open': session.is_open, 'is-closed': !session.is_open }"
      >
        <div class="session-left">
          <div class="type-badge" :class="session.exam_type ?? 'midterm'">
            {{ examTypeLabels[session.exam_type] ?? session.exam_type }}
          </div>
          <div class="session-info">
            <h3 class="session-title">{{ session.title }}</h3>
            <div class="session-meta">
              <span v-if="session.time_limit_minutes">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                {{ session.time_limit_minutes }} min
              </span>
              <span v-if="session.max_attempts">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
                {{ attemptsLeft(session) }}
              </span>
              <span v-if="session.available_from && session.available_until">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
                {{ formatDate(session.available_from) }} – {{ formatDate(session.available_until) }}
              </span>
            </div>
          </div>
        </div>

        <div class="session-right">
          
          <div v-if="getMyAttempt(session.id)" class="my-result">
            <span :class="['score-chip', getMyAttempt(session.id)?.passed ? 'pass' : 'fail']">
              {{ Number(getMyAttempt(session.id)?.score_pct || 0).toFixed(1) }}%
              · {{ getMyAttempt(session.id)?.passed ? 'Passed' : 'Failed' }}
            </span>
          </div>

          <span :class="['status-badge', session.is_open ? 'open' : 'closed']">
            {{ session.is_open ? 'Open' : 'Closed' }}
          </span>

          <button
            v-if="session.is_open && attemptsRemaining(session) > 0"
            class="btn-primary"
            @click="openExam(session)"
          >
            {{ getMyAttempt(session.id) ? 'Retake' : 'Start Exam' }}
          </button>

          <button
            v-else-if="getMyAttempt(session.id)"
            class="btn-ghost"
            @click="viewResult(session)"
          >
            View Result
          </button>

          <button v-else class="btn-ghost" disabled>
            {{ !session.is_open ? 'Not available' : 'No attempts left' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '@/services/examService'

const route = useRoute()
const router = useRouter()
const courseId = computed(() => route.params.courseId)

// --- State ---
const sessions = ref([])
const myAttempts = ref([])  
const isLoading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const filterType = ref('all')
const filterStatus = ref('all')

const examTypeLabels = {
  midterm: 'Midterm',
  final: 'Final',
  summer: 'Summer',
  quiz: 'Quiz',
}

async function loadSessions() {
  isLoading.value = true
  error.value = null
  try {
    const res  = await examService.listOpenSessions(courseId.value)
    sessions.value = res.data ?? res

    const attemptsPromises = sessions.value.map(s => examService.getMyAttempts(s.id).catch(() => null))
    const results = await Promise.all(attemptsPromises)

    const collectedAttempts = []
    results.forEach((r, index) => {
      if (!r) return
      const attempts = r.data ?? r
      if (attempts && attempts.length > 0) {

        const latest = attempts.sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at))[0]
        collectedAttempts.push({ ...latest, session_id: sessions.value[index].id })
      }
    })
    myAttempts.value = collectedAttempts

  } catch (err) {
    console.error('Failed to load sessions', err)
    error.value = err?.response?.data?.detail ?? 'Failed to load exams.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadSessions()
})

// --- Computed ---
const filteredSessions = computed(() => {
  return sessions.value.filter(s => {
    const matchType = filterType.value === 'all' || s.exam_type === filterType.value
    const matchStatus = filterStatus.value === 'all' ||
      (filterStatus.value === 'open' && s.is_open) ||
      (filterStatus.value === 'closed' && !s.is_open)
    const matchSearch = !searchQuery.value ||
      s.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchType && matchStatus && matchSearch
  })
})

// --- Helpers ---

function getMyAttempt(sessionId) {
  return myAttempts.value.find(a => a.session_id === sessionId)
}

function attemptsUsed(session) {
  return myAttempts.value.filter(a => a.session_id === session.id).length
}
function attemptsRemaining(session) {
  return (session.max_attempts ?? 1) - attemptsUsed(session)
}
function attemptsLeft(session) {
  const remaining = attemptsRemaining(session)
  const total = session.max_attempts ?? 1
  return `${remaining}/${total} attempts left`
}
function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

// --- Navigation ---
function openExam(session) {
  router.push({ name: 'ExamSession', params: { sessionId: session.id } })
}
function viewResult(session) {
  const attempt = getMyAttempt(session.id)
  if (attempt) router.push({ name: 'ExamResult', params: { attemptId: attempt.id } })
}
</script>

<style scoped>
/* ── Dashboard wrapper ── */
.dashboard {
  min-height: 100vh;
  padding: 2rem;
  max-width: 900px;
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
  right: -40px;
  top: -40px;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  pointer-events: none;
}

.header::after {
  content: '';
  position: absolute;
  right: 60px;
  bottom: -50px;
  width: 110px;
  height: 110px;
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

/* ── Filter Bar (inside .page-card, no own border/radius) ── */
.filter-bar {
  border-top: 1px solid rgba(237, 64, 129, 0.15);
}

/* Top row — pink */
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

/* Search (lives inside pink top bar) */
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

/* Bottom row — white, both groups side by side */
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

/* Filter groups */
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

/* Pill base */
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

/* Active "All" → pink */
.pill.active {
  background: var(--primary-pink);
  color: var(--white);
  border-color: var(--primary-pink);
}

/* Type-specific active colors */
.pill-midterm.active { background: #2563eb; border-color: #2563eb; color: #fff; }
.pill-final.active   { background: #d97706; border-color: #d97706; color: #fff; }
.pill-summer.active  { background: var(--forest-green); border-color: var(--forest-green); color: #fff; }
.pill-quiz.active    { background: #7c3aed; border-color: #7c3aed; color: #fff; }

/* Status-specific active colors */
.pill-open.active    { background: var(--forest-green); border-color: var(--forest-green); color: #fff; }
.pill-closed.active  { background: var(--text-muted);   border-color: var(--text-muted);   color: #fff; }

/* Status dot */
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



/* ── Session List ── */
.session-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.session-card {
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

.session-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.session-card.is-open {
  border-left: 3px solid var(--accent-green);
}

.session-card.is-closed {
  opacity: 0.72;
}

/* ── Session Left ── */
.session-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.type-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  white-space: nowrap;
  flex-shrink: 0;
}

.type-badge.midterm { background: #eff6ff; color: #2563eb; }
.type-badge.final   { background: var(--light-yellow); color: #92400e; }
.type-badge.summer  { background: var(--light-green); color: var(--forest-green); }
.type-badge.quiz    { background: #faf5ff; color: #7c3aed; }

.session-info {
  min-width: 0;
}

.session-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 0.375rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-meta {
  display: flex;
  gap: 0.875rem;
  flex-wrap: wrap;
}

.session-meta span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.775rem;
  color: var(--text-muted);
}

/* ── My Result ── */
.my-result {
  display: flex;
  align-items: center;
}

/* ── Session Right ── */
.session-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

/* ── Status badge (reuse badge system) ── */
.status-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
}

.status-badge.open   { background: var(--light-green); color: var(--forest-green); }
.status-badge.closed { background: var(--gray-light);  color: var(--text-muted); }

/* ── Score chip ── */
.score-chip {
  font-size: 0.775rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
}

.score-chip.pass { background: var(--light-green); color: var(--forest-green); }
.score-chip.fail { background: #fee2e2; color: #b91c1c; }

/* ── Buttons (override global .btn for local needs) ── */
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
  white-space: nowrap;
  transition: background 0.15s ease, transform 0.15s ease;
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: scale(0.98);
}

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

.btn-ghost:hover:not(:disabled) {
  background: var(--gray-light);
  color: var(--text-main);
  border-color: var(--text-muted);
}

.btn-ghost:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ── Empty / Loading / Error States ── */
.empty-state {
  text-align: center;
  padding: 4rem 1.5rem;
  background: var(--white);
  border-radius: var(--radius-lg);
  border: 1.5px dashed var(--card-border);
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 0.875rem;
}

.empty-state p {
  color: var(--text-muted);
  font-size: 0.9375rem;
}

.loading-state {
  text-align: center;
  padding: 4rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.error-banner {
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  font-size: 0.84rem;
  color: #b91c1c;
  font-weight: 500;
}

/* ── Responsive ── */
@media (max-width: 700px) {
  .dashboard { padding: 1.25rem 1rem; }
  .session-card { flex-direction: column; align-items: flex-start; }
  .session-right { width: 100%; justify-content: space-between; }
  .filter-bar-top { flex-direction: column; align-items: stretch; gap: 0.5rem; }
  .search-box { min-width: unset; }
  .filter-bar-bottom { flex-direction: column; align-items: stretch; gap: 0.5rem; }
  .filter-divider { width: 100%; height: 1.5px; }
  .filter-group { flex-wrap: wrap; }
}
</style>