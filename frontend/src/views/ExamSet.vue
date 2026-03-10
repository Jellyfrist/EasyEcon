<template>
  <div class="page">

    <div v-if="isLoading" class="loading-state">Loading exam info...</div>

    <template v-else-if="session">

      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="goToDashboard">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
          </button>
          <div class="header-text">
            <p class="breadcrumb">Exam Session</p>
            <h1 class="page-title">{{ session.title }}</h1>
          </div>
        </div>
      </div>

      <!-- stat cards -->
      <div class="info-grid">
        <div class="info-card">
          <svg class="info-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
          <div>
            <p class="info-label">Time Limit</p>
            <p class="info-value">{{ session.time_limit_minutes ? `${session.time_limit_minutes} minutes` : 'No limit' }}</p>
          </div>
        </div>
        <div class="info-card">
          <svg class="info-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          <div>
            <p class="info-label">Questions</p>
            <p class="info-value">{{ session.questions?.length || 0 }} questions</p>
          </div>
        </div>
        <div class="info-card">
          <svg class="info-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/></svg>
          <div>
            <p class="info-label">Total Points</p>
            <p class="info-value">{{ totalPoints }} points</p>
          </div>
        </div>
      </div>

      <!-- Question types breakdown -->
      <div class="qtype-card">
        <div class="qtype-header">
          <svg class="info-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18"/></svg>
          <span class="qtype-title">Question Types</span>
        </div>
        <div class="qtype-list">
          <div v-for="(item, i) in questionTypeSummary" :key="i" class="qtype-item">
            <span class="qtype-count">{{ item.count }}</span>
            <span class="qtype-name">{{ item.label }}</span>
          </div>
        </div>
      </div>

      <div v-if="session.instructions" class="instructions-card">
        <h2 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
          Instructions
        </h2>
        <p class="instructions-text">{{ session.instructions }}</p>
      </div>

      <div class="cta-bar">
        <div class="cta-left">
          <p class="cta-hint">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/></svg>
            Once started, the timer cannot be paused.
          </p>
        </div>
        <button class="btn-primary" @click="startExam">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
          Start Exam
        </button>
      </div>

    </template>

    <div v-if="error" class="error-banner">ERROR: {{ error }}</div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '@/services/examService'

const route = useRoute()
const router = useRouter()
const sessionId = route.params.sessionId

// --- State ---
const session   = ref(null)
const isLoading = ref(false)
const error     = ref(null)

// --- Load ---
async function loadSession() {
  isLoading.value = true
  error.value = null
  try {
    const res = await examService.openSession(sessionId)
    session.value = res.data ?? res
  } catch (err) {
    console.error('Failed to load session', err)
    error.value = err?.response?.data?.detail ?? 'Failed to load exam.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
    loadSession()
})

// --- Computed ---
const totalPoints = computed(() =>
  session.value?.questions?.reduce((s, q) => s + (q.points ?? 1), 0) ?? 0
)

const questionTypeSummary = computed(() => {
  if (!session.value?.questions?.length) return []
  const counts = {}
  for (const q of session.value.questions) {
    const label = questionTypeLabel(q.type)
    counts[label] = (counts[label] ?? 0) + 1
  }
  return Object.entries(counts).map(([label, count]) => ({ label, count }))
})

// --- Helpers ---
const TYPE_LABELS = {
  multiple_choice: 'MCQ',
  true_false: 'T/F',
  short_answer: 'Short',
}

function questionTypeLabel(type) {
  return TYPE_LABELS[type] ?? type
}

function startExam() {
  router.push({ 
    name: 'TakeExam', 
    params: { sessionId: sessionId } 
  })
}

function goToDashboard() {
  let courseId = route.query.courseId || localStorage.getItem('currentCourseId');
  
  if (!courseId && session.value) {
    courseId = session.value.course_id || session.value.courseId || session.value.course?.id;
  }
  console.log("Course ID:", courseId);

  if (courseId && courseId !== 'undefined' && courseId !== 'null') {
    router.push({ 
      name: 'ExamDashboard', 
      params: { courseId: courseId } 
    });
  } else {
    console.warn("not found courseId");
    router.push('/student/courses'); 
  }
}

</script>

<style scoped>
/* ── Page wrapper ── */
.page {
  min-height: 100vh;
  padding: 2rem;
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ── Header ── */
.header {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, var(--primary-pink) 0%, #f06292 100%);
  border-radius: var(--radius-lg);
  padding: 2rem 2.5rem;
  box-shadow: 0 8px 24px rgba(237, 64, 129, 0.28);
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
  font-size: 0.72rem;
  color: rgba(255,255,255,0.75);
  font-weight: 500;
}

.page-title {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--white);
  line-height: 1.2;
  letter-spacing: -0.01em;
}

/* ── Info Grid (top 3 cards) ── */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.info-card {
  background: var(--white);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.875rem;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.info-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.info-icon {
  color: var(--primary-pink);
  flex-shrink: 0;
}

.info-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 600;
  margin-bottom: 2px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.9375rem;
  font-weight: 700;
  color: var(--text-main);
}

/* ── Question Types Card ── */
.qtype-card {
  background: var(--white);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 0.875rem 1.25rem;
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.qtype-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  padding-right: 1.25rem;
  border-right: 1.5px solid var(--card-border);
}

.qtype-title {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.qtype-list {
  display: flex;
  flex: 1;
  align-items: center;
}

.qtype-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 0.375rem 0.75rem;
  border-right: 1.5px solid var(--card-border);
}

.qtype-item:last-child {
  border-right: none;
}

.qtype-count {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--primary-pink);
  line-height: 1;
}

.qtype-name {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

/* ── Instructions Card ── */
.instructions-card {
  background: var(--light-yellow);
  border: 1.5px solid #fde68a;
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.instructions-text {
  font-size: 0.875rem;
  color: var(--text-main);
  line-height: 1.7;
  white-space: pre-line;
}

/* ── CTA Bar ── */
.cta-bar {
  background: var(--white);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 1.125rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  position: sticky;
  bottom: 1.5rem;
  box-shadow: var(--shadow-md);
}

.cta-left {
  display: flex;
  align-items: center;
}

.cta-hint {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: #92400e;
  font-weight: 500;
}

.btn-primary {
  background: var(--primary-pink);
  color: var(--white);
  border: none;
  border-radius: var(--radius-md);
  padding: 0.6rem 1.5rem;
  font-size: 0.9rem;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
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

/* ── States ── */
.loading-state {
  text-align: center;
  padding: 4rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  .page        { padding: 1.25rem 1rem; }
  .info-grid   { grid-template-columns: 1fr; }
  .qtype-card  { flex-direction: column; align-items: stretch; gap: 0.75rem; }
  .qtype-header {
    padding-right: 0;
    border-right: none;
    border-bottom: 1.5px solid var(--card-border);
    padding-bottom: 0.75rem;
  }
  .cta-bar     { flex-direction: column; align-items: stretch; position: static; }
  .btn-primary { justify-content: center; }
}
</style>