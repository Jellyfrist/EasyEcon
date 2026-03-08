<template>
  <div class="page">

    <div v-if="isLoading" class="loading-state">Loading result...</div>

    <template v-else-if="attempt">

      <div class="header">
        <div>
          <p class="breadcrumb">Attempt #{{ attempt.id }}</p>
          <h1 class="page-title">Exam Result</h1>
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
            {{ attempt.passed ? '🎉 Passed' : '❌ Failed' }}
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

      <div v-if="attempt.weakness_report?.length" class="card">
        <h2 class="card-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/></svg>
          Areas to Improve
        </h2>
        <div class="weakness-list">
          <div v-for="(w, i) in attempt.weakness_report" :key="i" class="weakness-item">
            <span class="weakness-topic">{{ w.topic ?? w.topic_tag ?? 'Unknown topic' }}</span>
            <p v-if="w.question_text" class="weakness-q">{{ w.question_text }}</p>
            <router-link
              v-if="w.linked_learning_page_id"
              :to="`/learn/${w.linked_learning_page_id}`"
              class="review-link"
            >
              Review lesson →
            </router-link>
          </div>
        </div>
      </div>

      <div class="actions-row">
        <button class="btn-ghost" @click="$router.push({ name: 'ExamHistory', params: { sessionId: attempt.session_id } })">
          Back to History
        </button>
        <button class="btn-primary" @click="$router.push({ name: 'ExamAnalysis', params: { attemptId: attempt.id } })">
          View Full Analysis →
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
const attemptId = route.params.attemptId

// --- State ---
const attempt   = ref(null)   
const isLoading = ref(false)
const error     = ref(null)

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

onMounted(() => {
  loadAttempt()
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

/* Score Hero */
.score-hero {
  border-radius: 16px; padding: 32px;
  display: flex; align-items: center; gap: 32px;
  border: 1.5px solid;
}
.score-hero.pass { background: #f0fdf4; border-color: #86efac; }
.score-hero.fail { background: #fef2f2; border-color: #fca5a5; }

.score-circle { position: relative; width: 130px; height: 130px; flex-shrink: 0; }
.circle-svg   { width: 100%; height: 100%; }
.circle-bg    { stroke: #e8eaf2; }
.score-hero.pass .circle-fill { stroke: #22c55e; }
.score-hero.fail .circle-fill { stroke: #ef4444; }
.circle-fill  { transition: stroke-dashoffset 1s ease; }

.circle-inner {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.score-pct { font-size: 24px; font-weight: 800; color: #1a1d2e; line-height: 1; }
.score-raw  { font-size: 12px; color: #7c82a0; margin-top: 3px; }

.hero-info  { display: flex; flex-direction: column; gap: 16px; }
.result-chip {
  display: inline-block; font-size: 15px; font-weight: 700;
  padding: 6px 18px; border-radius: 999px; width: fit-content;
}
.result-chip.pass { background: #dcfce7; color: #16a34a; }
.result-chip.fail { background: #fecaca; color: #dc2626; }

.hero-stats { display: flex; gap: 24px; }
.hero-stat  { display: flex; flex-direction: column; gap: 3px; }
.hero-stat-label { font-size: 11.5px; color: #7c82a0; }
.hero-stat-val   { font-size: 16px; font-weight: 700; color: #1a1d2e; }

/* Card */
.card {
  background: #fff; border: 1px solid #e8eaf2;
  border-radius: 14px; padding: 22px 24px;
  display: flex; flex-direction: column; gap: 16px;
}
.card-title {
  font-size: 14px; font-weight: 700; color: #1a1d2e;
  display: flex; align-items: center; gap: 7px;
}

/* Topic Breakdown */
.topic-list { display: flex; flex-direction: column; gap: 12px; }
.topic-row  { display: flex; align-items: center; gap: 12px; }
.topic-name { font-size: 13.5px; color: #3a3d52; width: 150px; flex-shrink: 0; }
.topic-bar-track {
  flex: 1; height: 8px; background: #f0f1f5;
  border-radius: 999px; overflow: hidden;
}
.topic-bar-fill { height: 100%; border-radius: 999px; transition: width 0.6s ease; }
.topic-bar-fill.good { background: #22c55e; }
.topic-bar-fill.bad  { background: #ef4444; }
.topic-pct { font-size: 12.5px; font-weight: 700; width: 38px; text-align: right; flex-shrink: 0; }
.topic-pct.good { color: #16a34a; }
.topic-pct.bad  { color: #dc2626; }

/* Weakness */
.weakness-list { display: flex; flex-direction: column; gap: 10px; }
.weakness-item {
  background: #fff7ed; border: 1px solid #fed7aa;
  border-radius: 10px; padding: 14px 16px;
  display: flex; flex-direction: column; gap: 5px;
}
.weakness-topic { font-size: 11.5px; font-weight: 700; color: #c2410c; text-transform: uppercase; letter-spacing: 0.04em; }
.weakness-q     { font-size: 13.5px; color: #3a3d52; line-height: 1.5; }
.review-link    { font-size: 12.5px; font-weight: 600; color: #2563eb; text-decoration: none; width: fit-content; }
.review-link:hover { text-decoration: underline; }

/* Actions */
.actions-row {
  display: flex; justify-content: space-between; gap: 12px;
  padding-top: 4px;
}
.btn-primary {
  background: #1a1d2e; color: #fff;
  border: none; border-radius: 10px;
  padding: 11px 24px; font-size: 14px;
  font-family: 'Sarabun', sans-serif; font-weight: 500;
  cursor: pointer; transition: background 0.15s;
}
.btn-primary:hover { background: #2d3251; }
.btn-ghost {
  background: transparent; color: #555;
  border: 1.5px solid #e2e5ef; border-radius: 10px;
  padding: 11px 20px; font-size: 14px;
  font-family: 'Sarabun', sans-serif;
  cursor: pointer; transition: background 0.15s;
}
.btn-ghost:hover { background: #f7f8fc; }

/* States */
.loading-state { text-align: center; padding: 64px; color: #7c82a0; font-size: 14px; }
.error-banner {
  background: #fef2f2; border: 1px solid #fca5a5;
  border-radius: 9px; padding: 12px 16px; font-size: 13.5px; color: #dc2626;
}

@media (max-width: 600px) {
  .page        { padding: 20px 16px; }
  .score-hero  { flex-direction: column; align-items: center; text-align: center; }
  .hero-stats  { justify-content: center; }
  .actions-row { flex-direction: column; }
}
</style>