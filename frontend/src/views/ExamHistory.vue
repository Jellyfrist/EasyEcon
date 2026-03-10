<template>
  <div class="page">

    <div v-if="isLoading" class="loading-state">Loading history...</div>

    <template v-else>

      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="goBackToAnalysis">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
          </button>
          <div class="header-text">
            <p class="breadcrumb">Session #{{ sessionId }}</p>
            <h1 class="page-title">My Attempts</h1>
          </div>
        </div>
      </div>

      <div v-if="attempts.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <rect width="20" height="16" x="2" y="4" rx="2"/>
            <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            <line x1="12" y1="17" x2="12" y2="17"/>
          </svg>
        </div>
        <p>You haven't taken this exam yet.</p>
      </div>

      <template v-else>

        <div v-if="best" :class="['best-card', best.passed ? 'pass' : 'fail']">
          <div class="best-left">
            <p class="best-label">Best Attempt</p>
            <p class="best-score">{{ Number(best.score_pct || 0).toFixed(1) }}<span class="best-unit">%</span></p>
            <p class="best-raw">{{ best.score || 0 }} / {{ best.max_score || 0 }} pts</p>
          </div>
          <div class="best-right">
            <span :class="['result-chip', best.passed ? 'pass' : 'fail']">
              <template v-if="best.passed">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
                Passed
              </template>
              <template v-else>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
                Failed
              </template>
            </span>
            <p class="best-meta" v-if="best.percentile != null">Percentile: {{ best.percentile.toFixed(0) }}th</p>
            <p class="best-meta">{{ formatTime(best.submitted_at) }}</p>
          </div>
        </div>

        <div class="card">
          <h2 class="card-title">All Attempts</h2>
          <div class="attempt-list">
            <div
              v-for="(attempt, idx) in sortedAttempts"
              :key="attempt.id"
              class="attempt-row"
            >
              <div class="attempt-num">
                <span class="num-label">Attempt</span>
                <span class="num-val">{{ sortedAttempts.length - idx }}</span>
              </div>

              <div class="attempt-score-wrap">
                <div class="attempt-pct-row">
                  <span class="attempt-pct">{{ Number(attempt.score_pct || 0).toFixed(1) }}%</span>
                  <span :class="['result-chip-sm', attempt.passed ? 'pass' : 'fail']">
                    {{ attempt.passed ? 'Pass' : 'Fail' }}
                  </span>
                </div>
                <div class="pct-bar-track">
                  <div
                    class="pct-bar-fill"
                    :style="{ width: attempt.score_pct + '%' }"
                    :class="barClass(attempt.score_pct)"
                  ></div>
                </div>
                <span class="attempt-raw">{{ attempt.score || 0 }} / {{ attempt.max_score || 0 }} pts</span>
              </div>

              <div class="attempt-meta">
                <span v-if="attempt.percentile != null">{{ attempt.percentile.toFixed(0) }}th percentile</span>
                <span>{{ formatTime(attempt.submitted_at) }}</span>
              </div>

              <div class="attempt-actions">
                <button class="btn-ghost-sm" @click="viewResult(attempt)">Result</button>
                <button class="btn-ghost-sm" @click="viewAnalysis(attempt)">Analysis</button>
              </div>
            </div>
          </div>
        </div>

      </template>
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
const attempts  = ref([])   
const isLoading = ref(false)
const error     = ref(null)

// --- Load ---
async function loadAttempts() {
  isLoading.value = true
  error.value = null
  try {
    const res = await examService.getMyAttempts(sessionId)
    attempts.value = res.data ?? res
  } catch (err) {
    console.error('Failed to load attempts', err)
    error.value = err?.response?.data?.detail ?? 'Failed to load history.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => { loadAttempts() })

// --- Computed ---
// newest first
const sortedAttempts = computed(() =>
  [...attempts.value].sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at))
)

const best = computed(() => {
  if (!attempts.value.length) return null
  return [...attempts.value].sort((a, b) => (b.score_pct || 0) - (a.score_pct || 0))[0]
})

// --- Helpers ---
function formatTime(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })
}
function barClass(pct) {
  if (pct >= 80) return 'green'
  if (pct >= 60) return 'yellow'
  return 'red'
}

// --- Navigate ---
function viewResult(attempt) {
  router.push({ name: 'ExamResult', params: { attemptId: attempt.id } })
}
function viewAnalysis(attempt) {
  router.push({ name: 'ExamAnalysis', params: { attemptId: attempt.id } })
}
function goBackToAnalysis() {
  if (best.value) {
    router.push({ 
      name: 'ExamAnalysis', 
      params: { attemptId: best.value.id } 
    });
  } else {
    router.back();
  }
}
</script>

<style scoped>
/* Page wrapper */
.page {
  max-width: 680px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/*  Header */
.header {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, var(--primary-pink) 0%, #f06292 100%);
  border-radius: var(--radius-lg);
  padding: 1.5rem 1.75rem;
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

/* Best Attempt Card */
.best-card {
  border-radius: var(--radius-lg);
  padding: 1.625rem 1.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.25rem;
  border: 1.5px solid;
  box-shadow: var(--shadow-sm);
}
.best-card.pass {
  background: var(--light-green);
  border-color: #86efac;
}
.best-card.fail {
  background: #fef2f2;
  border-color: #fca5a5;
}

.best-left  { display: flex; flex-direction: column; gap: 4px; }

.best-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.best-score {
  font-size: 3rem;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1;
}
.best-unit { font-size: 1.5rem; }

.best-raw {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.best-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}
.best-meta {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* Result chips */
.result-chip {
  font-size: 0.8rem;
  font-weight: 700;
  padding: 5px 14px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.result-chip.pass { background: var(--light-green);  color: var(--forest-green); }
.result-chip.fail { background: #fecaca; color: #dc2626; }

.result-chip-sm {
  font-size: 0.69rem;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: 999px;
}
.result-chip-sm.pass { background: var(--light-green);  color: var(--forest-green); }
.result-chip-sm.fail { background: #fecaca; color: #dc2626; }

/* All-Attempts card */
.card {
  background: var(--white);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 1.375rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  box-shadow: var(--shadow-sm);
}

.card-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--text-main);
}

/* Attempt rows */
.attempt-list { display: flex; flex-direction: column; }

.attempt-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 0;
  border-bottom: 1px solid var(--gray-light);
}
.attempt-row:last-child { border-bottom: none; }

.attempt-num {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  width: 52px;
  flex-shrink: 0;
}
.num-label {
  font-size: 0.625rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.num-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-main);
}

.attempt-score-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}
.attempt-pct-row { display: flex; align-items: center; gap: 0.625rem; }

.attempt-pct {
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--text-main);
}

/* Progress bar */
.pct-bar-track {
  height: 6px;
  background: var(--gray-light);
  border-radius: 999px;
  overflow: hidden;
}
.pct-bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.4s ease;
}
.pct-bar-fill.green  { background: var(--forest-green); }
.pct-bar-fill.yellow { background: var(--primary-yellow); }
.pct-bar-fill.red    { background: var(--primary-pink); }

.attempt-raw {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.attempt-meta {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 0.75rem;
  color: var(--text-muted);
  flex-shrink: 0;
  text-align: right;
}

/* Action buttons */
.attempt-actions { display: flex; gap: 6px; flex-shrink: 0; }

.btn-ghost-sm {
  background: transparent;
  color: var(--text-muted);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  padding: 5px 12px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.btn-ghost-sm:hover {
  background: var(--gray-light);
  border-color: var(--forest-green);
  color: var(--forest-green);
}

/* Empty / loading / error states */
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
  color: var(--text-muted);
  opacity: 0.5;
}
.empty-state p { color: var(--text-muted); font-size: 0.9375rem; }

.loading-state {
  text-align: center;
  padding: 4rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.error-banner {
  background: #fef2f2;
  border: 1px solid #fca5a5;
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  font-size: 0.84rem;
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/*  Responsive  */
@media (max-width: 600px) {
  .page { padding: 1.25rem 1rem; }
  .best-card { flex-direction: column; align-items: flex-start; }
  .best-right { align-items: flex-start; }
  .attempt-row { flex-wrap: wrap; }
  .attempt-meta { text-align: left; }
}
</style>