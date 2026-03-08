<template>
  <div class="page">

    <div v-if="isLoading" class="loading-state">Loading history...</div>

    <template v-else>

      <div class="header">
        <button class="back-btn" @click="$router.back()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
        </button>
        <div>
          <p class="breadcrumb">Session #{{ sessionId }}</p>
          <h1 class="page-title">My Attempts</h1>
        </div>
      </div>

      <div v-if="attempts.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
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
              {{ best.passed ? '🎉 Passed' : '❌ Failed' }}
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

onMounted(() => {
  loadAttempts()
})

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
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.page {
  font-family: 'Sarabun', sans-serif;
  min-height: 100vh;
  padding: 32px;
  max-width: 680px;
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
.breadcrumb { font-size: 12px; color: #9399aa; margin-bottom: 2px; }
.page-title { font-family: 'IBM Plex Sans Thai', sans-serif; font-size: 22px; font-weight: 700; color: #1a1d2e; }

/* Best Card */
.best-card {
  border-radius: 16px; padding: 26px 28px;
  display: flex; align-items: center; justify-content: space-between; gap: 20px;
  border: 1.5px solid;
}
.best-card.pass { background: #f0fdf4; border-color: #86efac; }
.best-card.fail { background: #fef2f2; border-color: #fca5a5; }

.best-left  { display: flex; flex-direction: column; gap: 4px; }
.best-label { font-size: 11.5px; font-weight: 700; color: #9399aa; text-transform: uppercase; letter-spacing: 0.05em; }
.best-score { font-size: 48px; font-weight: 800; color: #1a1d2e; line-height: 1; }
.best-unit  { font-size: 24px; }
.best-raw   { font-size: 13px; color: #7c82a0; }

.best-right { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.best-meta  { font-size: 12.5px; color: #7c82a0; }

.result-chip {
  font-size: 13px; font-weight: 700; padding: 5px 16px; border-radius: 999px;
}
.result-chip.pass { background: #dcfce7; color: #16a34a; }
.result-chip.fail { background: #fecaca; color: #dc2626; }

/* Card */
.card {
  background: #fff; border: 1px solid #e8eaf2;
  border-radius: 14px; padding: 22px 24px;
  display: flex; flex-direction: column; gap: 14px;
}
.card-title { font-size: 14px; font-weight: 700; color: #1a1d2e; }

/* Attempt List */
.attempt-list { display: flex; flex-direction: column; gap: 0; }
.attempt-row {
  display: flex; align-items: center; gap: 16px;
  padding: 14px 0; border-bottom: 1px solid #f0f1f5;
}
.attempt-row:last-child { border-bottom: none; }

.attempt-num {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  width: 52px; flex-shrink: 0;
}
.num-label { font-size: 10px; color: #9399aa; text-transform: uppercase; letter-spacing: 0.05em; }
.num-val   { font-size: 20px; font-weight: 800; color: #1a1d2e; }

.attempt-score-wrap { flex: 1; display: flex; flex-direction: column; gap: 5px; min-width: 0; }
.attempt-pct-row    { display: flex; align-items: center; gap: 10px; }
.attempt-pct        { font-size: 17px; font-weight: 700; color: #1a1d2e; }
.result-chip-sm {
  font-size: 11px; font-weight: 700; padding: 2px 9px; border-radius: 999px;
}
.result-chip-sm.pass { background: #dcfce7; color: #16a34a; }
.result-chip-sm.fail { background: #fef2f2; color: #dc2626; }

.pct-bar-track { height: 6px; background: #f0f1f5; border-radius: 999px; overflow: hidden; }
.pct-bar-fill  { height: 100%; border-radius: 999px; transition: width 0.4s; }
.pct-bar-fill.green  { background: #22c55e; }
.pct-bar-fill.yellow { background: #f59e0b; }
.pct-bar-fill.red    { background: #ef4444; }
.attempt-raw { font-size: 12px; color: #9399aa; }

.attempt-meta {
  display: flex; flex-direction: column; gap: 3px;
  font-size: 12px; color: #9399aa; flex-shrink: 0; text-align: right;
}

.attempt-actions { display: flex; gap: 6px; flex-shrink: 0; }
.btn-ghost-sm {
  background: transparent; color: #555;
  border: 1.5px solid #e2e5ef; border-radius: 8px;
  padding: 5px 12px; font-size: 12.5px;
  font-family: 'Sarabun', sans-serif;
  cursor: pointer; transition: background 0.15s; white-space: nowrap;
}
.btn-ghost-sm:hover { background: #f7f8fc; }

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

@media (max-width: 600px) {
  .page      { padding: 20px 16px; }
  .best-card { flex-direction: column; align-items: flex-start; }
  .best-right { align-items: flex-start; }
  .attempt-row { flex-wrap: wrap; }
  .attempt-meta { text-align: left; }
}
</style>