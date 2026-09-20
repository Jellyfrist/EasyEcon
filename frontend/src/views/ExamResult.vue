<template>
  <div class="page">

    <div v-if="isLoading" class="loading-state">Loading result...</div>

    <template v-else-if="attempt">

      <div class="header">
        <div class="header-left">
          <div class="header-text">
            <p class="breadcrumb">Attempt #{{ attempt.id }}</p>
            <h1 class="page-title">Exam Result</h1>
          </div>
        </div>
      </div>

      <div :class="['score-hero', attempt.passed ? 'pass' : 'fail']">
        <div class="score-circle">
          <svg class="circle-svg" viewBox="0 0 120 120">
            <circle class="circle-bg"  cx="60" cy="60" r="52" fill="none" stroke-width="10"/>
            <circle class="circle-fill" cx="60" cy="60" r="52" fill="none" stroke-width="10"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="dashOffset"
              stroke-linecap="round"
              transform="rotate(-90 60 60)"
            />
          </svg>
          <div class="circle-inner">
            <span class="score-pct">{{ Number(attempt.score_pct || 0).toFixed(1) }}%</span>
            <span class="score-raw">{{ attempt.score || 0 }} / {{ attempt.max_score || 0 }}</span>
          </div>
        </div>
        <div class="hero-info">
          <div :class="['result-chip', attempt.passed ? 'pass' : 'fail']">
            <template v-if="attempt.passed">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
              Passed
            </template>
            <template v-else>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              Failed
            </template>
          </div>
          <div class="hero-stats">
            <div class="hero-stat">
              <span class="hero-stat-label">Percentile</span>
              <span class="hero-stat-val">{{ attempt.percentile != null ? attempt.percentile.toFixed(0) + 'th' : '—' }}</span>
            </div>
            <div class="hero-stat">
              <span class="hero-stat-label">Submitted</span>
              <span class="hero-stat-val">{{ formatTime(attempt.submitted_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="topicEntries && topicEntries.length" class="card">
        <h2 class="card-title">Topic Breakdown</h2>
        <div class="topic-list">
          <div v-for="[topic, stat] in topicEntries" :key="topic" class="topic-row">
            <span class="topic-name">{{ topic }}</span>
            <div class="topic-bar-track">
              <div
                class="topic-bar-fill"
                :style="{ width: topicPct(stat) + '%' }"
                :class="topicPct(stat) >= 60 ? 'good' : 'bad'"
              ></div>
            </div>
            <span :class="['topic-pct', topicPct(stat) >= 60 ? 'good' : 'bad']">
              {{ topicPct(stat).toFixed(0) }}%
            </span>
          </div>
        </div>
      </div>

      <div v-if="wrongTopics.length" class="card">
        <h2 class="card-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/></svg>
          Areas to Improve
        </h2>
        <div class="weakness-list">
          <div
            v-for="t in wrongTopics"
            :key="t.topic_tag"
            :class="['weakness-item', t.is_weak ? 'weak' : 'minor']"
          >
            <div class="weakness-head">
              <span class="weakness-topic">{{ t.topic_tag }}</span>
              <span class="weakness-count">
                {{ t.wrong_count }}/{{ t.total_questions }} wrong · {{ Number(t.score_pct || 0).toFixed(0) }}%
              </span>
            </div>

            <p v-if="t.message" class="weakness-q">{{ t.message }}</p>

            <div v-if="t.lessons?.length" class="lesson-links">
              <router-link
                v-for="lesson in t.lessons"
                :key="lesson.page_id"
                :to="lesson.study_url"
                class="review-link"
              >
                Review: {{ lesson.title }}
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </router-link>
            </div>
            <p v-else class="no-lesson">No lesson is linked to this topic yet.</p>
          </div>
        </div>
      </div>

      <div class="actions-row">
        <button class="btn-ghost" @click="$router.push({ name: 'ExamHistory', params: { sessionId: attempt.session_id } })">
          My Exam History
        </button>
        <button class="btn-primary" @click="$router.push({ name: 'ExamAnalysis', params: { attemptId: attempt.id } })">
          View Full Analysis
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
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
const attemptId = route.params.attemptId

// --- State ---
const attempt     = ref(null)
const wrongTopics = ref([])   // GET /exam/attempts/:id/wrong-topics
const isLoading   = ref(false)
const error       = ref(null)

// --- Load ---
async function loadAttempt() {
  isLoading.value = true
  error.value = null
  try {
    const res = await examService.getAttempt(attemptId)
    attempt.value = res.data ?? res
  } catch (err) {
    console.error('Failed to load attempt', err)
    error.value = err?.response?.data?.detail ?? 'Failed to load result.'
  } finally {
    isLoading.value = false
  }
}

// wrong topics + the lessons covering them. a failure here must not hide the
// score, so it only warns and leaves the "Areas to Improve" card out.
async function loadWrongTopics() {
  try {
    const res = await examService.getWrongTopics(attemptId)
    wrongTopics.value = res.data ?? res ?? []
  } catch (err) {
    console.warn('Failed to load wrong topics', err)
    wrongTopics.value = []
  }
}

onMounted(() => {
  loadAttempt()
  loadWrongTopics()
})

// --- Circle progress ---
const circumference = 2 * Math.PI * 52  // r=52
const dashOffset = computed(() => {
  if (!attempt.value) return circumference
  return circumference - ((attempt.value.score_pct || 0) / 100) * circumference
})

// --- Topic Stats ---
const topicEntries = computed(() => {
  if (!attempt.value || !attempt.value.topic_stats) return []
  return Object.entries(attempt.value.topic_stats)
})

function topicPct(stat) {
  if (typeof stat === 'number') return stat
  if (stat?.total) return (stat.correct / stat.total) * 100
  return 0
}

// --- Helpers ---
function formatTime(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })
}
</script>

<style scoped>
/* ── Page ── */
.page {
  min-height: 100vh;
  padding: 2rem 2.5rem;
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

/* ── Score Hero ── */
.score-hero {
  border-radius: var(--radius-lg);
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  border: 1.5px solid;
  box-shadow: var(--shadow-sm);
}

.score-hero.pass {
  background: #f0fdf4;
  border-color: #86efac;
}

.score-hero.fail {
  background: #fef2f2;
  border-color: #fca5a5;
}

.score-circle {
  position: relative;
  width: 130px;
  height: 130px;
  flex-shrink: 0;
}

.circle-svg { width: 100%; height: 100%; }
.circle-bg  { stroke: var(--card-border); }

.score-hero.pass .circle-fill { stroke: var(--forest-green); }
.score-hero.fail .circle-fill { stroke: #ef4444; }
.circle-fill { transition: stroke-dashoffset 1s ease; }

.circle-inner {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-pct {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-main);
  line-height: 1;
}

.score-raw {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 3px;
}

.hero-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.9375rem;
  font-weight: 700;
  padding: 0.375rem 1.125rem;
  border-radius: 999px;
  width: fit-content;
}

.result-chip.pass { background: var(--light-green); color: var(--forest-green); }
.result-chip.fail { background: #fecaca; color: #dc2626; }

.hero-stats {
  display: flex;
  gap: 1.5rem;
}

.hero-stat {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.hero-stat-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hero-stat-val {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-main);
}

/* ── Card ── */
.card {
  background: var(--white);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 1.375rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: var(--shadow-sm);
}

.card-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

/* ── Topic Breakdown ── */
.topic-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.topic-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.topic-name {
  font-size: 0.84rem;
  color: var(--text-main);
  width: 160px;
  flex-shrink: 0;
}

.topic-bar-track {
  flex: 1;
  height: 7px;
  background: var(--gray-light);
  border-radius: 999px;
  overflow: hidden;
}

.topic-bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.6s ease;
}

.topic-bar-fill.good { background: var(--forest-green); }
.topic-bar-fill.bad  { background: #ef4444; }

.topic-pct {
  font-size: 0.78rem;
  font-weight: 700;
  width: 38px;
  text-align: right;
  flex-shrink: 0;
}

.topic-pct.good { color: var(--forest-green); }
.topic-pct.bad  { color: #dc2626; }

/* ── Weakness ── */
.weakness-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.weakness-item {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: var(--radius-md);
  padding: 0.875rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.3125rem;
}

/* topics above the 60% threshold: wrong, but not flagged as weak */
.weakness-item.minor {
  background: var(--gray-light, #f8fafc);
  border-color: var(--card-border);
}

.weakness-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
}

.weakness-topic {
  font-size: 0.7rem;
  font-weight: 700;
  color: #c2410c;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.weakness-item.minor .weakness-topic { color: var(--text-muted); }

.weakness-count {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}

.lesson-links {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
  margin-top: 0.125rem;
}

.no-lesson {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
}

.weakness-q {
  font-size: 0.84rem;
  color: var(--text-main);
  line-height: 1.55;
}

.review-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--primary-pink);
  text-decoration: none;
  width: fit-content;
  transition: opacity 0.15s;
}

.review-link:hover { opacity: 0.75; }

/* ── Actions ── */
.actions-row {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding-top: 0.25rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--primary-pink);
  color: var(--white);
  border: none;
  border-radius: 999px;
  padding: 0.6875rem 1.5rem;
  font-size: 0.875rem;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.15s ease;
  box-shadow: 0 4px 14px rgba(237,64,129,0.3);
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-ghost {
  background: var(--white);
  color: var(--text-main);
  border: 1.5px solid var(--card-border);
  border-radius: 999px;
  padding: 0.6875rem 1.5rem;
  font-size: 0.875rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: var(--shadow-sm);
}

.btn-ghost:hover {
  border-color: var(--primary-pink);
  color: var(--primary-pink);
  box-shadow: 0 0 0 3px var(--light-pink);
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
@media (max-width: 600px) {
  .page { padding: 1.25rem 1rem; }
  .score-hero { flex-direction: column; align-items: center; text-align: center; }
  .hero-stats { justify-content: center; }
  .actions-row { flex-direction: column; }
  .topic-name { width: 110px; font-size: 0.78rem; }
}
</style>