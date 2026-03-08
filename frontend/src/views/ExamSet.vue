<template>
  <div class="page">

    <div v-if="isLoading" class="loading-state">Loading exam info...</div>

    <template v-else-if="session">

      <div class="header">
        <button class="back-btn" @click="$router.back()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
        </button>
        <div class="header-text">
          <p class="breadcrumb">Exam</p>
          <h1 class="page-title">{{ session.title }}</h1>
        </div>
      </div>

      <div class="info-grid">
        <div class="info-card">
          <div class="info-icon">⏱</div>
          <div>
            <p class="info-label">Time Limit</p>
            <p class="info-value">{{ session.time_limit_minutes ? `${session.time_limit_minutes} minutes` : 'No limit' }}</p>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon">📝</div>
          <div>
            <p class="info-label">Questions</p>
            <p class="info-value">{{ session.questions?.length || 0 }} questions</p>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon">🏆</div>
          <div>
            <p class="info-label">Total Points</p>
            <p class="info-value">{{ totalPoints }} points</p>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon">📊</div>
          <div>
            <p class="info-label">Question Types</p>
            <p class="info-value">{{ questionTypeSummary }}</p>
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

    <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

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

// ───────────────────────────────────────────────────────────────────────────

// --- Computed ---

const totalPoints = computed(() =>
  session.value?.questions?.reduce((s, q) => s + (q.points ?? 1), 0) ?? 0
)

const questionTypeSummary = computed(() => {
  if (!session.value?.questions?.length) return '—'
  const counts = {}
  for (const q of session.value.questions) {
    const label = questionTypeLabel(q.type)
    counts[label] = (counts[label] ?? 0) + 1
  }
  return Object.entries(counts).map(([k, v]) => `${v} ${k}`).join(', ')
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

// --- Navigate ---
function startExam() {
  router.push({ name: 'TakeExam', params: { sessionId } })
}
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.page {
  font-family: 'Sarabun', sans-serif;
  min-height: 100vh;
  padding: 32px;
  max-width: 760px;
  margin: 0 auto;
  display: flex; flex-direction: column; gap: 20px;
}

/* Header */
.header { display: flex; align-items: center; gap: 14px; }
.back-btn {
  width: 38px; height: 38px; flex-shrink: 0;
  border: 1.5px solid #dde1ea; background: #fff;
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #555; transition: all 0.15s;
}
.back-btn:hover { background: #f0f1f5; }
.breadcrumb  { font-size: 12px; color: #9399aa; margin-bottom: 2px; }
.page-title  { font-family: 'IBM Plex Sans Thai', sans-serif; font-size: 22px; font-weight: 700; color: #1a1d2e; }

/* Info Grid */
.info-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
}
.info-card {
  background: #fff; border: 1px solid #e8eaf2; border-radius: 14px;
  padding: 16px 18px; display: flex; align-items: center; gap: 12px;
}
.info-icon  { font-size: 22px; flex-shrink: 0; }
.info-label { font-size: 11.5px; color: #7c82a0; margin-bottom: 3px; }
.info-value { font-size: 14px; font-weight: 700; color: #1a1d2e; }

/* Instructions */
.instructions-card {
  background: #fffbeb; border: 1.5px solid #fde68a;
  border-radius: 14px; padding: 20px 24px;
  display: flex; flex-direction: column; gap: 10px;
}
.instructions-text { font-size: 14px; color: #3a3d52; line-height: 1.7; white-space: pre-line; }

/* Section Card */
.section-card {
  background: #fff; border: 1px solid #e8eaf2;
  border-radius: 14px; padding: 22px 24px;
  display: flex; flex-direction: column; gap: 14px;
}
.section-title {
  font-size: 14px; font-weight: 700; color: #1a1d2e;
  display: flex; align-items: center; gap: 7px;
}

/* Question List */
.question-list { display: flex; flex-direction: column; gap: 0; }
.question-row {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 0; border-bottom: 1px solid #f0f1f5;
}
.question-row:last-child { border-bottom: none; }

.q-num {
  width: 24px; height: 24px; border-radius: 50%;
  background: #f0f1f5; font-size: 11px; font-weight: 700; color: #555;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.q-type-badge {
  font-size: 10.5px; font-weight: 700; padding: 3px 9px;
  border-radius: 999px; flex-shrink: 0;
}
.q-type-badge.multiple_choice   { background: #eff6ff; color: #2563eb; }
.q-type-badge.true_false        { background: #f0fdf4; color: #16a34a; }
.q-type-badge.fill_in_the_blank { background: #faf5ff; color: #7c3aed; }
.q-type-badge.short_answer      { background: #fef3c7; color: #b45309; }

.q-text   { flex: 1; font-size: 13.5px; color: #3a3d52; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.q-points { font-size: 12px; font-weight: 600; color: #9399aa; white-space: nowrap; flex-shrink: 0; }

/* CTA Bar */
.cta-bar {
  background: #fff; border: 1px solid #e8eaf2;
  border-radius: 14px; padding: 18px 24px;
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  position: sticky; bottom: 24px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}
.cta-left { display: flex; align-items: center; }
.cta-hint {
  display: flex; align-items: center; gap: 6px;
  font-size: 13px; color: #b45309;
}
.btn-start {
  background: #1a1d2e; color: #fff;
  border: none; border-radius: 10px;
  padding: 11px 28px; font-size: 15px;
  font-family: 'Sarabun', sans-serif; font-weight: 600;
  cursor: pointer; display: flex; align-items: center; gap: 8px;
  transition: background 0.15s; white-space: nowrap;
}
.btn-start:hover { background: #2d3251; }

/* States */
.loading-state { text-align: center; padding: 64px; color: #7c82a0; font-size: 14px; }
.error-banner {
  background: #fef2f2; border: 1px solid #fca5a5;
  border-radius: 9px; padding: 12px 16px; font-size: 13.5px; color: #dc2626;
}

@media (max-width: 700px) {
  .page       { padding: 20px 16px; }
  .info-grid  { grid-template-columns: repeat(2, 1fr); }
  .cta-bar    { flex-direction: column; align-items: stretch; position: static; }
  .btn-start  { justify-content: center; }
}
</style>