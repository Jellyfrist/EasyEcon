<template>
  <FeaturePage class="page student-course-page">
    <template #header>
        <EditorHeader title="Exam Result" :back-to="examListRoute" :breadcrumbs="[{ label: 'Courses', to: { name: 'Dashboard' } }, { label: 'Exams', to: examListRoute }, { label: 'Result', to: route.fullPath }]">
            <template #status><p v-if="attempt" class="header-status">Attempt #{{ attempt.id }}</p></template>
        </EditorHeader>
    </template>

    <div v-if="isLoading" class="loading-state">Loading result...</div>

    <template v-else-if="attempt">

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

      <ExamQuestionReview :wrong-topics="wrongTopics" :error="reviewError" />
      <div v-if="reviewError" class="error-banner" role="alert">{{ reviewError }}</div>

      <div class="actions-row">
        <button class="btn-ghost" @click="router.push(examListRoute)">
          Back to Exams
        </button>
      </div>

    </template>

    <ExamAttemptHistory v-if="!isLoading && !error && !historyError" :attempts="attempts" />
    <div v-if="historyError" class="error-banner" role="alert">{{ historyError }}</div>
    <div v-if="error" class="error-banner" role="alert">ERROR: {{ error }}</div>

  </FeaturePage>
</template>

<script setup>
import EditorHeader from '@/components/EditorHeader.vue'
import FeaturePage from '@/components/FeaturePage.vue'
import { ref, computed, watch } from 'vue'
import ExamQuestionReview from '@/components/ExamQuestionReview.vue'
import ExamAttemptHistory from '@/components/ExamAttemptHistory.vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '@/services/examService'

const route = useRoute()
const router = useRouter()
// All legacy result/analysis/history routes share this view.
const attempt = ref(null)
const examListRoute = computed(() => {
  const courseId = route.query.courseId || attempt.value?.course_id
  return courseId ? { name: 'ExamDashboard', params: { courseId } } : { name: 'Dashboard' }
})
const attempts = ref([])
const wrongTopics = ref([])
const isLoading = ref(false)
const error = ref(null)
const reviewError = ref('')
const historyError = ref('')
let loadVersion = 0

async function loadResult() {
  const version = ++loadVersion
  isLoading.value = true
  error.value = null
  reviewError.value = ''
  historyError.value = ''
  attempt.value = null
  attempts.value = []
  wrongTopics.value = []
  const routeAttemptId = route.params.attemptId
  const routeSessionId = route.params.sessionId

  try {
    let selectedId = routeAttemptId
    if (!selectedId && routeSessionId) {
      const res = await examService.getMyAttempts(routeSessionId)
      if (version !== loadVersion) return
      attempts.value = res.data ?? res ?? []
      selectedId = [...attempts.value]
        .sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at))[0]?.id
    }
    if (!selectedId) return

    const res = await examService.getAttempt(selectedId)
    if (version !== loadVersion) return
    attempt.value = res.data ?? res

    const [review, history] = await Promise.allSettled([
      examService.getWrongTopics(selectedId),
      routeSessionId ? Promise.resolve({ data: attempts.value }) : examService.getMyAttempts(attempt.value.session_id),
    ])
    if (version !== loadVersion) return
    if (review.status === 'fulfilled') {
      wrongTopics.value = review.value.data ?? review.value ?? []
    } else {
      reviewError.value = 'Could not load question analysis. Refresh this page to try again.'
    }
    if (history.status === 'fulfilled') {
      attempts.value = history.value.data ?? history.value ?? []
    } else {
      historyError.value = 'Could not load exam history. Refresh this page to try again.'
    }
  } catch (err) {
    if (version === loadVersion) {
      error.value = err?.response?.data?.detail ?? 'Failed to load result.'
    }
  } finally {
    if (version === loadVersion) isLoading.value = false
  }
}

watch(() => [route.params.attemptId, route.params.sessionId], loadResult, { immediate: true })

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

/* ── Header ── */

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
  background: var(--theme-bg-f0fdf4);
  border-color: var(--theme-border-86efac);
}

.score-hero.fail {
  background: var(--theme-bg-fef2f2);
  border-color: var(--theme-border-fca5a5);
}

.score-circle {
  position: relative;
  width: 130px;
  height: 130px;
  flex-shrink: 0;
}

.circle-svg { width: 100%; height: 100%; }
.circle-bg  { stroke: var(--card-border); }

.score-hero.pass .circle-fill { stroke: var(--text-green); }
.score-hero.fail .circle-fill { stroke: var(--theme-fg-ef4444); }
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

.result-chip.pass { background: var(--light-green); color: var(--text-green); }
.result-chip.fail { background: var(--theme-bg-fecaca); color: var(--theme-fg-dc2626); }

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
  background: var(--surface);
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

.topic-pct.good { color: var(--text-green); }
.topic-pct.bad  { color: var(--theme-fg-dc2626); }

/* ── Weakness ── */
.weakness-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.weakness-item {
  background: var(--theme-bg-fff7ed);
  border: 1px solid var(--theme-border-fed7aa);
  border-radius: var(--radius-md);
  padding: 0.875rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.3125rem;
}

/* topics above the 60% threshold: wrong, but not flagged as weak */
.weakness-item.minor {
  background: var(--gray-light, var(--theme-bg-f8fafc));
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
  color: var(--theme-fg-c2410c);
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
  background: var(--surface);
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
  background: var(--theme-bg-fee2e2);
  border: 1px solid var(--theme-border-fca5a5);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  font-size: 0.84rem;
  color: var(--theme-fg-b91c1c);
  font-weight: 500;
}

/* ── Responsive ── */
@media (max-width: 600px) {

  .score-hero { flex-direction: column; align-items: center; text-align: center; }
  .hero-stats { justify-content: center; }
  .actions-row { flex-direction: column; }
  .topic-name { width: 110px; font-size: 0.78rem; }
}
</style>
