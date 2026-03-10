<template>
    <div class="page">
    
        <div v-if="isLoading" class="loading-state">Loading analysis...</div>
    
        <template v-else-if="attempt">
    
          <div class="header">
            <div class="header-left">
              <button class="back-btn" @click="goExamSet">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
              </button>
              <div class="header-text">
                <p class="breadcrumb">Attempt #{{ attempt.id }}</p>
                <h1 class="page-title">Performance Analysis</h1>
              </div>
            </div>
          </div>
    
          <div class="summary-bar">
            <div class="summary-item">
              <span class="summary-val" :class="attempt.passed ? 'green' : 'red'">{{ Number(attempt.score_pct || 0).toFixed(1) }}%</span>
              <span class="summary-label">Score</span>
            </div>
            <div class="divider"></div>
            <div class="summary-item">
              <span class="summary-val">{{ attempt.score || 0 }} / {{ attempt.max_score || 0 }}</span>
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
    
          <div v-if="topicEntries && topicEntries.length" class="card">
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
    
          <div v-if="groupedWeakness && groupedWeakness.length" class="card">
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
                      <p class="weakness-q-text">{{ w.question_text || 'No question text available.' }}</p>
                    </div>
    
                    <div v-if="w.correct_answer" class="answer-row">
                      <span class="answer-label">Correct Answer:</span>
                      <span class="answer-val">{{ w.correct_answer }}</span>
                    </div>
    
                    <div v-if="w.explanation" class="explanation-box">
                      <span class="explanation-label">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
                      Explanation
                    </span>
                      <p class="explanation-text">{{ w.explanation }}</p>
                    </div>
    
                    <div v-if="w.linked_learning_page_id" class="action-row">
                      <router-link
                        :to="`/learn/${w.linked_learning_page_id}`"
                        class="review-link"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
                        Review Lesson 
                        <span v-if="w.page_number" class="page-ref-text">
                          (page {{ w.page_number }})
                        </span>
                      </router-link>
                    </div>
    
                  </div>
                </div>
              </div>
            </div>
          </div>
    
          <div v-else-if="!attempt.weakness_report?.length" class="perfect-card">
            <div class="perfect-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/></svg>
            </div>
            <p class="perfect-text">No weak areas found. Great performance!</p>
          </div>
    
          <div class="actions-row">
            <button class="btn-ghost" @click="goExamSet">
                Back to Exam session
            </button>
            <button class="btn-primary" @click="goExamHistory">
                My Exam History
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

const sessionId = computed(() => {
    return attempt.value ?.session_id || route.params.sessionId
})
// --- State ---
const attempt = ref(null)
const isLoading = ref(false)
const error = ref(null)

// --- Load ---
async function loadAttempt() {
    isLoading.value = true
    error.value = null
    try {
        const res = await examService.getAttempt(attemptId)
        attempt.value = res.data ?? res
    } catch (err) {
        console.error('Failed to load attempt', err)
        error.value = err ?.response ?.data ?.detail ?? 'Failed to load analysis.'
    } finally {
        isLoading.value = false
    }
}

onMounted(() => { loadAttempt() })

// --- Computed ---
const topicEntries = computed(() => {
    if (!attempt.value || !attempt.value.topic_stats) return []
    return Object.entries(attempt.value.topic_stats)
})

// Group weakness_report by topic
const groupedWeakness = computed(() => {
    if (!attempt.value || !attempt.value.weakness_report || !attempt.value.weakness_report.length) return []
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
    if (stat ?.total) return (stat.correct / stat.total) * 100
    return 0
}

const TYPE_LABELS = {
    multiple_choice: 'MCQ',
    true_false: 'T/F',
    short_answer: 'Short',
}

function typeLabel(type) { return TYPE_LABELS[type] ?? 'Q' }

function goExamSet() {
    if (sessionId.value) {
        router.push({
            name: 'ExamSession',
            params: { sessionId: sessionId.value }
        });
    } else {
        router.back();
    }
}

function goExamHistory() {
    if (sessionId.value) {
        router.push({
            name: 'ExamHistory',
            params: { sessionId: sessionId.value }
        });
    } else {
        router.back();
    }
}
</script>

<style scoped>
/* ── Page ── */

.page {
    min-height: 100vh;
    padding: 2rem;
    max-width: 760px;
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
    right: -40px;
    top: -40px;
    width: 160px;
    height: 160px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
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
    background: rgba(255, 255, 255, 0.06);
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
    border: 1.5px solid rgba(255, 255, 255, 0.4);
    background: rgba(255, 255, 255, 0.15);
    color: white;
    cursor: pointer;
    transition: all 0.18s ease;
    flex-shrink: 0;
    backdrop-filter: blur(4px);
}

.back-btn:hover {
    background: rgba(255, 255, 255, 0.28);
    border-color: rgba(255, 255, 255, 0.7);
}

.breadcrumb {
    font-size: 0.72rem;
    color: rgba(255, 255, 255, 0.75);
    font-weight: 500;
}

.page-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: var(--white);
    line-height: 1.2;
    letter-spacing: -0.01em;
}

/* ── Summary Bar ── */

.summary-bar {
    background: var(--white);
    border: 1.5px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.75rem;
    display: flex;
    align-items: center;
    box-shadow: var(--shadow-sm);
}

.summary-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.summary-val {
    font-size: 1.375rem;
    font-weight: 800;
    color: var(--text-main);
}

.summary-val.green {
    color: var(--forest-green);
}

.summary-val.red {
    color: #dc2626;
}

.summary-label {
    font-size: 0.7rem;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.divider {
    width: 1px;
    background: var(--card-border);
    height: 40px;
    flex-shrink: 0;
}

.result-chip {
    font-size: 0.8125rem;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 999px;
}

.result-chip.pass {
    background: var(--light-green);
    color: var(--forest-green);
}

.result-chip.fail {
    background: #fecaca;
    color: #dc2626;
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

/* ── Topic Grid ── */

.topic-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
}

.topic-card {
    border-radius: var(--radius-md);
    padding: 0.875rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.625rem;
    border: 1.5px solid;
}

.topic-card.good {
    background: #f0fdf4;
    border-color: #bbf7d0;
}

.topic-card.bad {
    background: #fef2f2;
    border-color: #fecaca;
}

.topic-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
}

.topic-card-name {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--text-main);
}

.topic-card-pct {
    font-size: 0.875rem;
    font-weight: 800;
    flex-shrink: 0;
}

.topic-card-pct.good {
    color: var(--forest-green);
}

.topic-card-pct.bad {
    color: #dc2626;
}

.topic-bar-track {
    height: 6px;
    background: var(--card-border);
    border-radius: 999px;
    overflow: hidden;
}

.topic-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s ease;
}

.topic-bar-fill.good {
    background: var(--forest-green);
}

.topic-bar-fill.bad {
    background: #ef4444;
}

.topic-card-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
}

/* ── Weakness Groups ── */

.weakness-groups {
    display: flex;
    flex-direction: column;
    gap: 1.125rem;
}

.weakness-group {
    display: flex;
    flex-direction: column;
    gap: 0.625rem;
}

.group-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 0.5rem;
    border-bottom: 1.5px solid var(--gray-light);
}

.group-topic {
    font-size: 0.84rem;
    font-weight: 700;
    color: var(--text-main);
}

.group-count {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.weakness-items {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.weakness-item {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: var(--radius-md);
    padding: 0.875rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.weakness-item-top {
    display: flex;
    align-items: flex-start;
    gap: 0.625rem;
}

.q-type-badge {
    font-size: 0.625rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 999px;
    white-space: nowrap;
    flex-shrink: 0;
    margin-top: 2px;
}

.q-type-badge.multiple_choice {
    background: #eff6ff;
    color: #2563eb;
}

.q-type-badge.true_false {
    background: var(--light-green);
    color: var(--forest-green);
}

.q-type-badge.short_answer {
    background: var(--light-yellow);
    color: #b45309;
}

.weakness-q-text {
    font-size: 0.84rem;
    color: var(--text-main);
    line-height: 1.55;
}

.answer-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.answer-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    flex-shrink: 0;
}

.answer-val {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--forest-green);
}

/* ── Explanation ── */

.explanation-box {
    background: var(--light-yellow);
    border-left: 3px solid var(--primary-pink);
    padding: 0.75rem 0.875rem;
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

.explanation-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--primary-pink);
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 0.3rem;
}

.explanation-text {
    font-size: 0.8125rem;
    color: var(--text-main);
    line-height: 1.6;
}

/* ── Review Link ── */

.action-row {
    padding-top: 0.75rem;
    border-top: 1px dashed var(--card-border);
}

.review-link {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--primary-pink);
    text-decoration: none;
    background: var(--light-pink);
    padding: 0.375rem 0.75rem;
    border-radius: var(--radius-md);
    transition: background 0.15s ease, opacity 0.15s ease;
    width: fit-content;
}

.review-link:hover {
    background: #ffb3cc;
}

.page-ref-text {
    color: var(--primary-hover);
    font-weight: 700;
}

/* ── Perfect Card ── */

.perfect-card {
    background: #f0fdf4;
    border: 1.5px solid #bbf7d0;
    border-radius: var(--radius-lg);
    padding: 2.25rem;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    box-shadow: var(--shadow-sm);
}

.perfect-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--light-green);
    color: var(--forest-green);
    display: flex;
    align-items: center;
    justify-content: center;
}

.perfect-text {
    font-size: 0.9375rem;
    font-weight: 600;
    color: var(--forest-green);
}

/* ── Actions ── */

.actions-row {
    display: flex;
    justify-content: space-between;
    gap: 0.75rem;
    padding-top: 0.25rem;
}

.btn-primary {
    display: inline-flex;
    text-align: center;
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
    box-shadow: 0 4px 14px rgba(237, 64, 129, 0.3);
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
    .page {
        padding: 1.25rem 1rem;
    }
    .summary-bar {
        padding: 1rem;
    }
    .summary-val {
        font-size: 1.125rem;
    }
    .topic-grid {
        grid-template-columns: 1fr 1fr;
    }
    .actions-row {
        flex-direction: column;
    }
}
</style>