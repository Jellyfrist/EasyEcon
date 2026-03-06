<template>
  <div class="page">

    <div v-if="isLoading" class="loading-state">Loading analysis...</div>

    <template v-else-if="attempt">

      <!-- Header -->
      <div class="header">
        <button class="back-btn" @click="$router.back()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
        </button>
        <div>
          <p class="breadcrumb">Attempt #{{ attempt.id }}</p>
          <h1 class="page-title">Performance Analysis</h1>
        </div>
      </div>

      <!-- Score Summary Bar -->
      <div class="summary-bar">
        <div class="summary-item">
          <span class="summary-val" :class="attempt.passed ? 'green' : 'red'">{{ attempt.score_pct.toFixed(1) }}%</span>
          <span class="summary-label">Score</span>
        </div>
        <div class="divider"></div>
        <div class="summary-item">
          <span class="summary-val">{{ attempt.score }} / {{ attempt.max_score }}</span>
          <span class="summary-label">Points</span>
        </div>
        <div class="divider"></div>
        <div class="summary-item">
          <span class="summary-val">{{ attempt.percentile != null ? attempt.percentile.toFixed(0) + 'th' : '—' }}</span>
          <span class="summary-label">Percentile</span>
        </div>
        <div class="divider"></div>
        <div class="summary-item">
          <span :class="['result-chip', attempt.passed ? 'pass' : 'fail']">
            {{ attempt.passed ? 'Passed' : 'Failed' }}
          </span>
          <span class="summary-label">Result</span>
        </div>
      </div>

      <!-- Topic Breakdown -->
      <div v-if="topicEntries.length" class="card">
        <h2 class="card-title">Topic Breakdown</h2>
        <div class="topic-grid">
          <div
            v-for="[topic, stat] in topicEntries"
            :key="topic"
            :class="['topic-card', topicPct(stat) >= 60 ? 'good' : 'bad']"
          >
            <div class="topic-card-top">
              <span class="topic-card-name">{{ topic }}</span>
              <span :class="['topic-card-pct', topicPct(stat) >= 60 ? 'good' : 'bad']">
                {{ topicPct(stat).toFixed(0) }}%
              </span>
            </div>
            <div class="topic-bar-track">
              <div
                class="topic-bar-fill"
                :style="{ width: topicPct(stat) + '%' }"
                :class="topicPct(stat) >= 60 ? 'good' : 'bad'"
              ></div>
            </div>
            <span class="topic-card-sub" v-if="stat?.total">
              {{ stat.correct }} / {{ stat.total }} correct
            </span>
          </div>
        </div>
      </div>

      <!-- Weakness Report -->
      <div v-if="groupedWeakness.length" class="card">
        <h2 class="card-title">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/></svg>
          Questions to Review
        </h2>

        <div class="weakness-groups">
          <div v-for="group in groupedWeakness" :key="group.topic" class="weakness-group">
            <div class="group-header">
              <span class="group-topic">{{ group.topic }}</span>
              <span class="group-count">{{ group.items.length }} question{{ group.items.length > 1 ? 's' : '' }}</span>
            </div>

            <div class="weakness-items">
              <div v-for="(w, i) in group.items" :key="i" class="weakness-item">
                <div class="weakness-item-top">
                  <span :class="['q-type-badge', w.type ?? 'multiple_choice']">
                    {{ typeLabel(w.type) }}
                  </span>
                  <p class="weakness-q-text">{{ w.question_text }}</p>
                </div>

                <div v-if="w.correct_answer" class="answer-row">
                  <span class="answer-label">Correct answer:</span>
                  <span class="answer-val">{{ w.correct_answer }}</span>
                </div>

                <router-link
                  v-if="w.linked_learning_page_id"
                  :to="`/learn/${w.linked_learning_page_id}`"
                  class="review-link"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
                  Review lesson
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No weakness -->
      <div v-else-if="!attempt.weakness_report?.length" class="perfect-card">
        <span class="perfect-icon">🏆</span>
        <p class="perfect-text">No weak areas found. Great performance!</p>
      </div>

    </template>

    <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

    <!-- Actions -->
    <div class="actions-row">
        <button class="btn-ghost" @click="$router.push({ name: 'ExamDashboard', params: { courseId: 'current' } })">
            Back to Exam session
        </button>
        <button class="btn-primary" @click="$router.push({ name: 'ExamHistory', params: { sessionId: 'current' } })">
            View all my exam history
        </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import examService from '@/services/examService'

const route = useRoute()
const attemptId = route.params.attemptId

// --- State ---
const attempt   = ref(null)   // ExamAttemptResponse
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
    error.value = err?.response?.data?.detail ?? 'Failed to load analysis.'
  } finally {
    isLoading.value = false
  }
}

// ─── MOCK (remove when API is ready) ───────────────────────────────────────
function loadMock() {
  attempt.value = {
    id: 101,
    student_id: 1,
    session_id: 1,
    score: 38,
    max_score: 50,
    score_pct: 76.0,
    passed: true,
    percentile: 82,
    topic_stats: {
      'Demand & Supply':  { correct: 4, total: 5 },
      'Elasticity':       { correct: 3, total: 5 },
      'Market Structure': { correct: 2, total: 4 },
      'Cost Theory':      { correct: 5, total: 5 },
      'Game Theory':      { correct: 2, total: 3 },
    },
    weakness_report: [
      {
        topic: 'Market Structure',
        question_text: 'Which market structure features many sellers with differentiated products?',
        type: 'multiple_choice',
        correct_answer: 'Monopolistic competition',
        linked_learning_page_id: 12,
      },
      {
        topic: 'Elasticity',
        question_text: 'If price elasticity of demand is -2, demand is considered?',
        type: 'multiple_choice',
        correct_answer: 'Elastic',
        linked_learning_page_id: 7,
      },
      {
        topic: 'Elasticity',
        question_text: 'A monopolist always produces at the socially optimal output level.',
        type: 'true_false',
        correct_answer: 'False',
        linked_learning_page_id: 8,
      },
      {
        topic: 'Game Theory',
        question_text: 'Explain the concept of Nash Equilibrium in your own words.',
        type: 'short_answer',
        correct_answer: null,
        linked_learning_page_id: 20,
      },
    ],
    started_at:   '2025-03-01T09:00:00',
    submitted_at: '2025-03-01T10:22:00',
  }
}

onMounted(() => loadMock())   // <- swap to loadAttempt() before deploy
//onMounted(() => loadAttempt())
// ───────────────────────────────────────────────────────────────────────────

// --- Computed ---
const topicEntries = computed(() => {
  if (!attempt.value?.topic_stats) return []
  return Object.entries(attempt.value.topic_stats)
})

// Group weakness_report by topic
const groupedWeakness = computed(() => {
  if (!attempt.value?.weakness_report?.length) return []
  const map = {}
  for (const w of attempt.value.weakness_report) {
    const topic = w.topic ?? w.topic_tag ?? 'Unknown'
    if (!map[topic]) map[topic] = []
    map[topic].push(w)
  }
  return Object.entries(map).map(([topic, items]) => ({ topic, items }))
})

// --- Helpers ---
function topicPct(stat) {
  if (typeof stat === 'number') return stat
  if (stat?.total) return (stat.correct / stat.total) * 100
  return 0
}

const TYPE_LABELS = {
  multiple_choice: 'MCQ',
  true_false:      'T/F',
  short_answer:    'Short',
}
function typeLabel(type) { return TYPE_LABELS[type] ?? 'Q' }
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
.breadcrumb { font-size: 12px; color: #9399aa; margin-bottom: 2px; }
.page-title { font-family: 'IBM Plex Sans Thai', sans-serif; font-size: 22px; font-weight: 700; color: #1a1d2e; }

/* Summary Bar */
.summary-bar {
  background: #fff; border: 1px solid #e8eaf2; border-radius: 14px;
  padding: 20px 28px;
  display: flex; align-items: center; gap: 0;
}
.summary-item {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 5px;
}
.summary-val   { font-size: 22px; font-weight: 800; color: #1a1d2e; }
.summary-val.green { color: #16a34a; }
.summary-val.red   { color: #dc2626; }
.summary-label { font-size: 11.5px; color: #9399aa; }
.divider { width: 1px; background: #e8eaf2; height: 40px; flex-shrink: 0; }
.result-chip {
  font-size: 13px; font-weight: 700; padding: 4px 14px; border-radius: 999px;
}
.result-chip.pass { background: #dcfce7; color: #16a34a; }
.result-chip.fail { background: #fef2f2; color: #dc2626; }

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

/* Topic Grid */
.topic-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px;
}
.topic-card {
  border-radius: 12px; padding: 14px 16px;
  display: flex; flex-direction: column; gap: 10px;
  border: 1.5px solid;
}
.topic-card.good { background: #f0fdf4; border-color: #bbf7d0; }
.topic-card.bad  { background: #fef2f2; border-color: #fecaca; }

.topic-card-top  { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.topic-card-name { font-size: 13px; font-weight: 600; color: #1a1d2e; }
.topic-card-pct  { font-size: 14px; font-weight: 800; flex-shrink: 0; }
.topic-card-pct.good { color: #16a34a; }
.topic-card-pct.bad  { color: #dc2626; }

.topic-bar-track { height: 6px; background: #e8eaf2; border-radius: 999px; overflow: hidden; }
.topic-bar-fill  { height: 100%; border-radius: 999px; transition: width 0.6s ease; }
.topic-bar-fill.good { background: #22c55e; }
.topic-bar-fill.bad  { background: #ef4444; }

.topic-card-sub { font-size: 11.5px; color: #7c82a0; }

/* Weakness Groups */
.weakness-groups { display: flex; flex-direction: column; gap: 18px; }

.weakness-group { display: flex; flex-direction: column; gap: 10px; }
.group-header {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 8px; border-bottom: 1.5px solid #f0f1f5;
}
.group-topic { font-size: 13.5px; font-weight: 700; color: #1a1d2e; }
.group-count { font-size: 12px; color: #9399aa; }

.weakness-items { display: flex; flex-direction: column; gap: 8px; }
.weakness-item {
  background: #fff7ed; border: 1px solid #fed7aa;
  border-radius: 10px; padding: 14px 16px;
  display: flex; flex-direction: column; gap: 8px;
}
.weakness-item-top { display: flex; align-items: flex-start; gap: 10px; }

.q-type-badge {
  font-size: 10px; font-weight: 700; padding: 3px 8px;
  border-radius: 999px; white-space: nowrap; flex-shrink: 0; margin-top: 2px;
}
.q-type-badge.multiple_choice { background: #eff6ff; color: #2563eb; }
.q-type-badge.true_false      { background: #f0fdf4; color: #16a34a; }
.q-type-badge.short_answer    { background: #fef3c7; color: #b45309; }

.weakness-q-text { font-size: 13.5px; color: #3a3d52; line-height: 1.55; }

.answer-row { display: flex; align-items: center; gap: 8px; }
.answer-label { font-size: 12px; color: #9399aa; flex-shrink: 0; }
.answer-val   { font-size: 13px; font-weight: 600; color: #16a34a; }

.review-link {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 12.5px; font-weight: 600; color: #2563eb;
  text-decoration: none; width: fit-content;
}
.review-link:hover { text-decoration: underline; }

/* Perfect */
.perfect-card {
  background: #f0fdf4; border: 1.5px solid #bbf7d0;
  border-radius: 14px; padding: 36px;
  text-align: center; display: flex; flex-direction: column; align-items: center; gap: 12px;
}
.perfect-icon { font-size: 40px; }
.perfect-text { font-size: 15px; font-weight: 600; color: #16a34a; }

/* States */
.loading-state { text-align: center; padding: 64px; color: #7c82a0; font-size: 14px; }
.error-banner {
  background: #fef2f2; border: 1px solid #fca5a5;
  border-radius: 9px; padding: 12px 16px; font-size: 13.5px; color: #dc2626;
}

@media (max-width: 600px) {
  .page        { padding: 20px 16px; }
  .summary-bar { padding: 16px; gap: 0; }
  .summary-val { font-size: 18px; }
  .topic-grid  { grid-template-columns: 1fr 1fr; }
}
</style>