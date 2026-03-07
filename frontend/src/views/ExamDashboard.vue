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
          <h1 class="page-title">Take Exam Practice Feature</h1>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input v-model="searchQuery" type="text" placeholder="Search exam..." />
      </div>
      <div class="filter-tabs">
        <button :class="['tab', { active: filterType === 'all' }]"     @click="filterType = 'all'">All</button>
        <button :class="['tab', { active: filterType === 'midterm' }]" @click="filterType = 'midterm'">Midterm</button>
        <button :class="['tab', { active: filterType === 'final' }]"   @click="filterType = 'final'">Final</button>
        <button :class="['tab', { active: filterType === 'summer' }]"  @click="filterType = 'summer'">Summer</button>
        <button :class="['tab', { active: filterType === 'quiz' }]"    @click="filterType = 'quiz'">Quiz</button>
      </div>
      <div class="filter-tabs">
        <button :class="['tab', { active: filterStatus === 'all' }]"    @click="filterStatus = 'all'">All</button>
        <button :class="['tab', { active: filterStatus === 'open' }]"   @click="filterStatus = 'open'">
          <span class="dot green"></span>Open
        </button>
        <button :class="['tab', { active: filterStatus === 'closed' }]" @click="filterStatus = 'closed'">Closed</button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="loading-state">Loading exams...</div>

    <!-- Empty -->
    <div v-else-if="filteredSessions.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <p>No exams available in this course.</p>
    </div>

    <!-- Session List -->
    <div v-else class="session-list">
      <div
        v-for="session in filteredSessions"
        :key="session.id"
        class="session-card"
        :class="{ 'is-open': session.is_open, 'is-closed': !session.is_open }"
      >
        <!-- Left -->
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

        <!-- Right -->
        <div class="session-right">
          <!-- My attempt badge -->
          <div v-if="myAttemptMap[session.id]" class="my-result">
            <span :class="['score-chip', myAttemptMap[session.id].passed ? 'pass' : 'fail']">
              {{ myAttemptMap[session.id].score_pct.toFixed(1) }}%
              · {{ myAttemptMap[session.id].passed ? 'Passed' : 'Failed' }}
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
            {{ myAttemptMap[session.id] ? 'Retake' : 'Start Exam' }}
          </button>

          <button
            v-else-if="myAttemptMap[session.id]"
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

    <!-- Error -->
    <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

    <button class="btn-primary" @click="$router.push({ name: 'ExamHistory', params: { sessionId: 'current' } })">
        View all my exam history
    </button>

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
const sessions = ref([])   // ExamSessionResponse[]
const myAttempts = ref([])   // ExamAttemptResponse[] — latest per session
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

// --- Load ---
async function loadSessions() {
  isLoading.value = true
  error.value = null
  try {
    const res  = await examService.listOpenSessions(courseId.value)
    sessions.value = res.data ?? res

    // For each session, fetch student's own attempts (fire-and-forget per session)
    await Promise.allSettled(
      sessions.value.map(async s => {
        try {
          const r = await examService.getMyAttempts(s.id)
          const attempts = r.data ?? r
          if (attempts?.length) {
            // Keep the latest attempt per session
            const latest = attempts.sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at))[0]
            myAttempts.value.push({ ...latest, session_id: s.id })
          }
        } catch { /* session has no attempts yet */ }
      })
    )
  } catch (err) {
    console.error('Failed to load sessions', err)
    error.value = err?.response?.data?.detail ?? 'Failed to load exams.'
  } finally {
    isLoading.value = false
  }
}

// ─── MOCK (remove when API is ready) ───────────────────────────────────────
function loadMock() {
  sessions.value = [
    {
      id: 1, title: 'Midterm 2025 — Microeconomics', exam_type: 'midterm',
      time_limit_minutes: 90, max_attempts: 1, is_open: true, is_active: true,
      available_from: '2025-03-01T09:00:00', available_until: '2025-03-01T12:00:00',
    },
    {
      id: 2, title: 'Final Exam 2025', exam_type: 'final',
      time_limit_minutes: 120, max_attempts: 1, is_open: false, is_active: false,
      available_from: '2025-05-10T09:00:00', available_until: '2025-05-10T12:00:00',
    },
    {
      id: 3, title: 'Quiz 1 — Demand & Supply', exam_type: 'quiz',
      time_limit_minutes: 30, max_attempts: 2, is_open: true, is_active: true,
      available_from: null, available_until: null,
    },
    {
      id: 4, title: 'Quiz 2 — Elasticity', exam_type: 'quiz',
      time_limit_minutes: 30, max_attempts: 2, is_open: true, is_active: true,
      available_from: null, available_until: null,
    },
  ]
  myAttempts.value = [
    {
      id: 101, session_id: 3, student_id: 1,
      score: 18, max_score: 20, score_pct: 90, passed: true,
      percentile: 88, topic_stats: {}, weakness_report: [],
      started_at: '2025-02-10T10:00:00', submitted_at: '2025-02-10T10:28:00',
    },
  ]
}

onMounted(() => loadMock())   // <- swap to loadSessions() before deploy
//onMounted(() => loadSessions())
// ───────────────────────────────────────────────────────────────────────────

// --- Computed ---

// map session_id -> latest attempt for quick lookup
const myAttemptMap = computed(() => {
  return Object.fromEntries(myAttempts.value.map(a => [a.session_id, a]))
})

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
  const attempt = myAttemptMap.value[session.id]
  if (attempt) router.push({ name: 'ExamResult', params: { attemptId: attempt.id } })
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.dashboard {
  font-family: 'Sarabun', sans-serif;
  min-height: 100vh;
  padding: 32px;
  max-width: 900px;
  margin: 0 auto;
  display: flex; flex-direction: column; gap: 18px;
}

/* Filters */
.filters {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.search-box {
  display: flex; align-items: center; gap: 9px;
  background: #fff; border: 1.5px solid #e2e5ef;
  border-radius: 10px; padding: 9px 14px; min-width: 220px;
}
.search-box svg { color: #9399aa; flex-shrink: 0; }
.search-box input {
  border: none; outline: none; font-size: 14px;
  font-family: 'Sarabun', sans-serif; background: transparent; color: #1a1d2e; width: 100%;
}
.filter-tabs { display: flex; gap: 6px; align-items: center; }
.tab {
  padding: 7px 14px; border-radius: 9px; border: 1.5px solid #e2e5ef;
  background: #fff; font-size: 13px; font-family: 'Sarabun', sans-serif;
  cursor: pointer; color: #555; transition: all 0.15s;
  display: flex; align-items: center; gap: 6px;
}
.tab.active { background: #1a1d2e; color: #fff; border-color: #1a1d2e; }
.tab:hover:not(.active) { background: #f0f1f5; }
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot.green { background: #22c55e; }

/* Session List */
.session-list { display: flex; flex-direction: column; gap: 10px; }

.session-card {
  background: #fff; border: 1.5px solid #e8eaf2;
  border-radius: 14px; padding: 20px 24px;
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; transition: box-shadow 0.15s, border-color 0.15s;
}
.session-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.07); }
.session-card.is-open   { border-left: 3px solid #22c55e; }
.session-card.is-closed { opacity: 0.7; }

/* Left */
.session-left { display: flex; align-items: center; gap: 16px; flex: 1; min-width: 0; }

.type-badge {
  font-size: 11px; font-weight: 600; padding: 4px 12px;
  border-radius: 999px; white-space: nowrap; flex-shrink: 0;
}
.type-badge.midterm { background: #eff6ff; color: #2563eb; }
.type-badge.final   { background: #fef3c7; color: #d97706; }
.type-badge.summer  { background: #f0fdf4; color: #16a34a; }
.type-badge.quiz    { background: #faf5ff; color: #7c3aed; }

.session-info { min-width: 0; }
.session-title {
  font-size: 15px; font-weight: 600; color: #1a1d2e;
  margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.session-meta {
  display: flex; gap: 14px; flex-wrap: wrap;
}
.session-meta span {
  display: flex; align-items: center; gap: 4px;
  font-size: 12.5px; color: #7c82a0;
}

/* Right */
.session-right { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

.status-badge {
  font-size: 12px; font-weight: 500; padding: 4px 12px; border-radius: 999px;
}
.status-badge.open   { background: #dcfce7; color: #16a34a; }
.status-badge.closed { background: #f3f4f6; color: #6b7280; }

.score-chip {
  font-size: 12.5px; font-weight: 600; padding: 4px 12px; border-radius: 999px;
}
.score-chip.pass { background: #dcfce7; color: #16a34a; }
.score-chip.fail { background: #fef2f2; color: #dc2626; }

/* Buttons */
.btn-primary {
  background: #1a1d2e; color: #fff;
  border: none; border-radius: 10px;
  padding: 9px 20px; font-size: 13.5px;
  font-family: 'Sarabun', sans-serif; font-weight: 500;
  cursor: pointer; white-space: nowrap;
  transition: background 0.15s;
}
.btn-primary:hover { background: #2d3251; }

.btn-ghost {
  background: transparent; color: #555;
  border: 1.5px solid #e2e5ef; border-radius: 10px;
  padding: 9px 18px; font-size: 13.5px;
  font-family: 'Sarabun', sans-serif;
  cursor: pointer; white-space: nowrap;
  transition: background 0.15s;
}
.btn-ghost:hover:not(:disabled) { background: #f7f8fc; }
.btn-ghost:disabled { opacity: 0.45; cursor: not-allowed; }

/* States */
.empty-state {
  text-align: center; padding: 64px 24px;
  background: #fff; border-radius: 14px; border: 1.5px dashed #d0d4e5;
}
.empty-icon { font-size: 40px; margin-bottom: 14px; }
.empty-state p { color: #7c82a0; font-size: 15px; }
.loading-state { text-align: center; padding: 64px; color: #7c82a0; font-size: 14px; }
.error-banner {
  background: #fef2f2; border: 1px solid #fca5a5;
  border-radius: 9px; padding: 12px 16px; font-size: 13.5px; color: #dc2626;
}

@media (max-width: 700px) {
  .dashboard { padding: 20px 16px; }
  .session-card { flex-direction: column; align-items: flex-start; }
  .session-right { width: 100%; justify-content: space-between; }
  .filters { flex-direction: column; align-items: stretch; }
}
</style>