<template>

  <!-- This has MOCK DATA for you to test -->

  <div class="page">

    <!-- Page Card: gradient header -->
    <div class="page-card">
      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="$router.back()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
          </button>
          <div class="header-text">
            <p class="breadcrumb">Session #{{ sessionId }}</p>
            <h1 class="page-title">{{ session?.title ?? 'Exam Results' }}</h1>
          </div>
        </div>
        <span :class="['session-badge', session?.is_open ? 'open' : 'closed']">
          {{ session?.is_open ? 'Open' : 'Closed' }}
        </span>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">Loading results...</div>

    <template v-else-if="!results.length">
      <div class="empty-state">
        <p>No students have submitted yet.</p>
      </div>
    </template>

    <template v-else>

      <!-- ── Summary Stats ── -->
      <div class="stats-bar">
        <div class="stat-card accent">
          <span class="stat-num">{{ results.length }}</span>
          <span class="stat-label">Students</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ avgScore }}%</span>
          <span class="stat-label">Average</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ medianScore }}%</span>
          <span class="stat-label">Median</span>
        </div>
        <div class="stat-card">
          <span class="stat-num green">{{ highScore }}%</span>
          <span class="stat-label">Highest</span>
        </div>
        <div class="stat-card">
          <span class="stat-num red">{{ lowScore }}%</span>
          <span class="stat-label">Lowest</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ passRate }}%</span>
          <span class="stat-label">Pass Rate</span>
        </div>
      </div>

      <!-- ── Score Distribution Chart ── -->
      <div class="card">
        <h2 class="card-title">Score Distribution</h2>
        <div class="chart-wrap">
          <div class="chart-bars">
            <div v-for="bucket in distributionBuckets" :key="bucket.label" class="chart-col">
              <span class="bar-count" v-if="bucket.count > 0">{{ bucket.count }}</span>
              <div
                class="bar"
                :style="{ height: barHeight(bucket.count) + 'px' }"
                :class="bucket.pct >= 80 ? 'bar-green' : bucket.pct >= 60 ? 'bar-yellow' : 'bar-red'"
              ></div>
              <span class="bar-label">{{ bucket.label }}</span>
            </div>
          </div>
          <div class="chart-legend">
            <span class="legend-dot green"></span><span>≥ 80%</span>
            <span class="legend-dot yellow"></span><span>60–79%</span>
            <span class="legend-dot red"></span><span>&lt; 60%</span>
          </div>
        </div>
      </div>

      <!-- ── Percentile Table ── -->
      <div class="card">
        <h2 class="card-title">Percentile Breakdown</h2>
        <table class="pct-table">
          <thead>
            <tr>
              <th>Percentile</th>
              <th>Score range</th>
              <th>Count</th>
              <th>% of class</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in percentileRows" :key="row.label">
              <td><span class="pct-label">{{ row.label }}</span></td>
              <td>{{ row.minScore }}% – {{ row.maxScore }}%</td>
              <td>{{ row.count }}</td>
              <td>
                <div class="mini-bar-wrap">
                  <div class="mini-bar" :style="{ width: row.classPct + '%' }"></div>
                  <span>{{ row.classPct }}%</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ── Student Results ── -->
      <div class="card">
        <div class="card-header-row">
          <h2 class="card-title">Student Results</h2>
          <div class="filters">
            <div class="search-box">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
              <input v-model="searchQuery" type="text" placeholder="Search student..." />
            </div>
            <div class="filter-tabs">
              <button :class="['tab', { active: filterStatus === 'all' }]" @click="filterStatus = 'all'">All</button>
              <button :class="['tab', { active: filterStatus === 'passed' }]" @click="filterStatus = 'passed'">Passed</button>
              <button :class="['tab', { active: filterStatus === 'failed' }]" @click="filterStatus = 'failed'">Failed</button>
            </div>
            <div class="filter-tabs">
              <button :class="['tab', { active: sortBy === 'rank' }]" @click="sortBy = 'rank'">Rank</button>
              <button :class="['tab', { active: sortBy === 'score_asc' }]" @click="sortBy = 'score_asc'">Score ↑</button>
              <button :class="['tab', { active: sortBy === 'submitted' }]" @click="sortBy = 'submitted'">Time</button>
            </div>
          </div>
        </div>

        <table class="results-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Student</th>
              <th>Score</th>
              <th>Percent</th>
              <th>Percentile</th>
              <th>Result</th>
              <th>Submitted</th>
              <th>Weak Topics</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(attempt, idx) in filteredResults"
              :key="attempt.id"
              class="result-row"
              @click="selectedAttempt = attempt"
              :class="{ selected: selectedAttempt?.id === attempt.id }"
            >
              <td class="td-rank">
                <span v-if="idx === 0" class="medal">🥇</span>
                <span v-else-if="idx === 1" class="medal">🥈</span>
                <span v-else-if="idx === 2" class="medal">🥉</span>
                <span v-else class="rank-num">{{ idx + 1 }}</span>
              </td>
              <td class="td-student">{{ attempt.student_id }}</td>
              <td class="td-score">
                <span class="score-val">{{ attempt.score }}</span>
                <span class="score-max">/ {{ attempt.max_score }}</span>
              </td>
              <td class="td-pct">
                <div class="pct-bar-wrap">
                  <div class="pct-bar" :style="{ width: attempt.score_pct + '%' }" :class="barClass(attempt.score_pct)"></div>
                  <span>{{ attempt.score_pct.toFixed(1) }}%</span>
                </div>
              </td>
              <td class="td-percentile">{{ attempt.percentile != null ? attempt.percentile.toFixed(0) + 'th' : '—' }}</td>
              <td>
                <span :class="['result-badge', attempt.passed ? 'pass' : 'fail']">
                  {{ attempt.passed ? 'Pass' : 'Fail' }}
                </span>
              </td>
              <td class="td-time">{{ formatTime(attempt.submitted_at) }}</td>
              <td class="td-topics">
                <span v-for="w in topWeakTopics(attempt.weakness_report)" :key="w" class="topic-tag">{{ w }}</span>
                <span v-if="!topWeakTopics(attempt.weakness_report).length" class="no-weakness">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </template>

    <div v-if="error" class="error-banner">
      ERROR: {{ error }}
    </div>

    <!-- ── Detail Panel ── -->
    <Teleport to="body">
      <div v-if="selectedAttempt" class="panel-overlay" @click.self="selectedAttempt = null">
        <div class="detail-panel">
          <div class="panel-header">
            <div>
              <p class="panel-sub">Student #{{ selectedAttempt.student_id }}</p>
              <h2 class="panel-title">Attempt Detail</h2>
            </div>
            <button class="close-btn" @click="selectedAttempt = null">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="panel-score-row">
            <div class="panel-score-big" :class="selectedAttempt.passed ? 'pass' : 'fail'">
              {{ selectedAttempt.score_pct.toFixed(1) }}%
            </div>
            <div class="panel-score-meta">
              <p>{{ selectedAttempt.score }} / {{ selectedAttempt.max_score }} pts</p>
              <p v-if="selectedAttempt.percentile != null">Percentile: {{ selectedAttempt.percentile.toFixed(0) }}th</p>
              <p>{{ formatTime(selectedAttempt.submitted_at) }}</p>
            </div>
          </div>
          <div v-if="topicStatsEntries(selectedAttempt).length" class="panel-section">
            <h3 class="panel-section-title">Topic Breakdown</h3>
            <div class="topic-stats-list">
              <div v-for="[topic, stat] in topicStatsEntries(selectedAttempt)" :key="topic" class="topic-stat-row">
                <span class="topic-name">{{ topic }}</span>
                <div class="topic-bar-wrap">
                  <div class="topic-bar" :style="{ width: topicPct(stat) + '%' }" :class="topicPct(stat) >= 60 ? 'good' : 'bad'"></div>
                </div>
                <span class="topic-pct">{{ topicPct(stat).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
          <div v-if="selectedAttempt.weakness_report?.length" class="panel-section">
            <h3 class="panel-section-title">Weakness Report</h3>
            <div class="weakness-list">
              <div v-for="w in selectedAttempt.weakness_report" :key="w.question_id ?? w.topic" class="weakness-item">
                <span class="weakness-topic">{{ w.topic ?? w.topic_tag ?? 'Unknown' }}</span>
                <span v-if="w.question_text" class="weakness-q">{{ w.question_text }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import examService from '@/services/examService'

const route = useRoute()
const sessionId = route.params.sessionId

// --- State ---
const session = ref(null)
const results = ref([])
const isLoading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const filterStatus = ref('all')
const sortBy = ref('rank')
const selectedAttempt = ref(null)

// --- Load ---
async function loadResults() {
  isLoading.value = true
  error.value = null
  try {
    const res  = await examService.getSessionResults(sessionId)
    const data = res.data ?? res
    if (Array.isArray(data)) {
      results.value = data
    } else {
      session.value = data.session ?? null
      results.value = data.results ?? data.attempts ?? []
    }
  } catch (err) {
    console.error('Failed to load results', err)
    error.value = err?.response?.data?.detail ?? 'Failed to load results.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => loadResults())

// --- Summary Stats ---
const sortedByScore = computed(() =>
  [...results.value].sort((a, b) => b.score_pct - a.score_pct)
)
const avgScore = computed(() => {
  if (!results.value.length) return 0
  return (results.value.reduce((s, r) => s + r.score_pct, 0) / results.value.length).toFixed(1)
})
const medianScore = computed(() => {
  if (!results.value.length) return 0
  const sorted = [...results.value].map(r => r.score_pct).sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 !== 0
    ? sorted[mid].toFixed(1)
    : ((sorted[mid - 1] + sorted[mid]) / 2).toFixed(1)
})
const highScore = computed(() =>
  results.value.length ? Math.max(...results.value.map(r => r.score_pct)).toFixed(1) : 0
)
const lowScore = computed(() =>
  results.value.length ? Math.min(...results.value.map(r => r.score_pct)).toFixed(1) : 0
)
const passRate = computed(() => {
  if (!results.value.length) return 0
  return ((results.value.filter(r => r.passed).length / results.value.length) * 100).toFixed(1)
})

// --- Score Distribution (10 buckets) ---
const BUCKETS = [
  { label: '0–9%',    min: 0,  max: 9,  pct: 5   },
  { label: '10–19%',  min: 10, max: 19, pct: 15  },
  { label: '20–29%',  min: 20, max: 29, pct: 25  },
  { label: '30–39%',  min: 30, max: 39, pct: 35  },
  { label: '40–49%',  min: 40, max: 49, pct: 45  },
  { label: '50–59%',  min: 50, max: 59, pct: 55  },
  { label: '60–69%',  min: 60, max: 69, pct: 65  },
  { label: '70–79%',  min: 70, max: 79, pct: 75  },
  { label: '80–89%',  min: 80, max: 89, pct: 85  },
  { label: '90–100%', min: 90, max: 100, pct: 95 },
]

const distributionBuckets = computed(() =>
  BUCKETS.map(b => ({
    ...b,
    count: results.value.filter(r => r.score_pct >= b.min && r.score_pct <= b.max).length,
  }))
)

const maxBucketCount = computed(() =>
  Math.max(...distributionBuckets.value.map(b => b.count), 1)
)

function barHeight(count) {
  return Math.max((count / maxBucketCount.value) * 140, count > 0 ? 8 : 0)
}

// --- Percentile Table ---
const PERCENTILE_RANGES = [
  { label: 'Top 10% (P90+)', min: 90, max: 100 },
  { label: 'P75 – P89', min: 75, max: 89 },
  { label: 'P50 – P74', min: 50, max: 74 },
  { label: 'P25 – P49', min: 25, max: 49 },
  { label: 'Bottom 25% (P24−)',min: 0, max: 24 },
]

const percentileRows = computed(() => {
  const total = results.value.length || 1
  return PERCENTILE_RANGES.map(range => {
    const inRange = results.value.filter(
      r => r.percentile != null && r.percentile >= range.min && r.percentile <= range.max
    )
    const scores = inRange.map(r => r.score_pct)
    return {
      label: range.label,
      count: inRange.length,
      minScore: scores.length ? Math.min(...scores).toFixed(1) : '—',
      maxScore: scores.length ? Math.max(...scores).toFixed(1) : '—',
      classPct: Number(((inRange.length / total) * 100).toFixed(1)),
    }
  })
})

// --- Filtered + Sorted Results ---
const filteredResults = computed(() => {
  let list = sortBy.value === 'rank' ? [...sortedByScore.value] : [...results.value]

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(r => String(r.student_id).toLowerCase().includes(q))
  }
  if (filterStatus.value === 'passed') list = list.filter(r => r.passed)
  if (filterStatus.value === 'failed') list = list.filter(r => !r.passed)
  if (sortBy.value === 'score_asc')  list.sort((a, b) => a.score_pct - b.score_pct)
  if (sortBy.value === 'submitted')  list.sort((a, b) => new Date(a.submitted_at) - new Date(b.submitted_at))

  return list
})

// --- Helpers ---
function formatTime(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })
}
function barClass(pct) {
  if (pct >= 80) return 'bar-green'
  if (pct >= 60) return 'bar-yellow'
  return 'bar-red'
}
function topWeakTopics(report) {
  if (!report?.length) return []
  return [...new Set(report.map(w => w.topic ?? w.topic_tag).filter(Boolean))].slice(0, 2)
}
function topicStatsEntries(attempt) {
  if (!attempt.topic_stats) return []
  return Object.entries(attempt.topic_stats)
}
function topicPct(stat) {
  if (typeof stat === 'number') return stat
  if (stat?.total) return (stat.correct / stat.total) * 100
  return 0
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Page card + gradient header */
.page-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(237, 64, 129, 0.22);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: linear-gradient(135deg, var(--primary-pink) 0%, #f06292 100%);
  padding: 1.5rem 1.75rem;
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

.header-text { display: flex; flex-direction: column; gap: 4px; }

.back-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px; height: 36px;
  border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.4);
  background: rgba(255,255,255,0.15);
  color: var(--white);
  cursor: pointer;
  flex-shrink: 0;
  backdrop-filter: blur(4px);
  transition: all 0.18s ease;
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
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--white);
  line-height: 1.15;
  letter-spacing: -0.01em;
}

/* Session open/closed badge (on header right) */
.session-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 14px;
  border-radius: 999px;
  position: relative;
  z-index: 1;
}

.session-badge.open { background: var(--light-green); color: var(--forest-green); }
.session-badge.closed { background: rgba(255,255,255,0.2); color: rgba(255,255,255,0.9); }

/* Stats bar */
.stats-bar {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.75rem;
}

.stat-card {
  background: var(--white);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 1rem 1.125rem;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: var(--shadow-sm);
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
}

.stat-card.accent { border-left: 3px solid var(--primary-pink); }

.stat-num { font-size: 1.5rem; font-weight: 800; color: var(--text-main); line-height: 1; }
.stat-num.green { color: var(--forest-green); }
.stat-num.red { color: #dc2626; }
.stat-label { font-size: 0.72rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }

/* Generic content card */
.card {
  background: var(--white);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
  box-shadow: var(--shadow-sm);
  transform: none;
}

.card-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
}

.card-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

/* Score distribution chart */
.chart-wrap  { display: flex; flex-direction: column; gap: 0.75rem; }

.chart-bars  {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 170px;
}

.chart-col { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; }
.bar-count { font-size: 0.68rem; font-weight: 700; color: var(--text-muted); }

.bar {
  width: 100%;
  border-radius: 5px 5px 0 0;
  transition: height 0.3s ease;
}

.bar-green { background: var(--forest-green); }
.bar-yellow { background: var(--primary-yellow); }
.bar-red { background: #ef4444; }

.bar-label {
  font-size: 0.62rem;
  color: var(--text-muted);
  white-space: nowrap;
  transform: rotate(-35deg);
  transform-origin: top center;
  margin-top: 6px;
}

.chart-legend {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding-top: 0.5rem;
  border-top: 1.5px solid var(--gray-light);
}

.legend-dot {
  width: 9px; height: 9px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.legend-dot.green  { background: var(--forest-green); }
.legend-dot.yellow { background: var(--primary-yellow); }
.legend-dot.red { background: #ef4444; }

.chart-legend span { font-size: 0.78rem; color: var(--text-muted); }

/* Percentile table */
.pct-table {
  width: 100%;
  border-collapse: collapse;
}

.pct-table thead tr {
  background: var(--gray-light);
  border-bottom: 1.5px solid var(--card-border);
}

.pct-table th {
  padding: 0.625rem 0.875rem;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-muted);
  text-align: left;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pct-table td {
  padding: 0.7rem 0.875rem;
  font-size: 0.84rem;
  color: var(--text-main);
  border-bottom: 1px solid var(--gray-light);
}

.pct-table tr:last-child td { border-bottom: none; }
.pct-label { font-weight: 600; }

.mini-bar-wrap { display: flex; align-items: center; gap: 0.5rem; }
.mini-bar {
  height: 6px;
  background: var(--primary-pink);
  border-radius: 999px;
  min-width: 2px;
  max-width: 120px;
}

/*  Filters + search (Student Results card) */
.filters {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--gray-light);
  border: 1.5px solid var(--card-border);
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  min-width: 180px;
  transition: all 0.2s ease;
}

.search-box:focus-within {
  background: var(--white);
  border-color: var(--primary-pink);
  box-shadow: 0 0 0 3px rgba(237, 64, 129, 0.08);
}

.search-box svg { color: var(--text-muted); flex-shrink: 0; }

.search-box input {
  border: none;
  outline: none;
  font-size: 0.82rem;
  font-family: inherit;
  background: transparent;
  color: var(--text-main);
  width: 100%;
}

.search-box input::placeholder { color: var(--text-muted); opacity: 0.7; }

.filter-tabs { display: flex; gap: 0.3rem; }

.tab {
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  border: 1.5px solid var(--card-border);
  background: transparent;
  font-size: 0.76rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 0.15s ease;
  white-space: nowrap;
}

.tab:hover:not(.active) {
  background: var(--light-pink);
  color: var(--primary-pink);
  border-color: var(--primary-pink);
}

.tab.active {
  background: var(--primary-pink);
  color: var(--white);
  border-color: var(--primary-pink);
}

/* Results table */
.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table thead tr {
  background: var(--gray-light);
  border-bottom: 1.5px solid var(--card-border);
}

.results-table th {
  padding: 0.625rem 0.875rem;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-muted);
  text-align: left;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.result-row {
  border-bottom: 1px solid var(--gray-light);
  cursor: pointer;
  transition: background 0.12s ease;
}

.result-row:last-child { border-bottom: none; }
.result-row:hover   { background: var(--gray-light); }
.result-row.selected { background: #eff6ff; }

.results-table td {
  padding: 0.7rem 0.875rem;
  font-size: 0.84rem;
  color: var(--text-main);
  vertical-align: middle;
}

.td-rank { width: 48px; }
.medal { font-size: 1rem; }
.rank-num { font-size: 0.82rem; font-weight: 600; color: var(--text-muted); }
.td-student { font-weight: 700; }
.score-val { font-weight: 700; }
.score-max { color: var(--text-muted); font-size: 0.75rem; }
.td-percentile { color: var(--text-muted); }
.td-time { color: var(--text-muted); font-size: 0.78rem; white-space: nowrap; }

/* Percent bar inside table */
.pct-bar-wrap { display: flex; align-items: center; gap: 0.5rem; min-width: 110px; }

.pct-bar {
  height: 6px;
  border-radius: 999px;
  flex-shrink: 0;
}

/* Result pass/fail badge */
.result-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
}

.result-badge.pass { background: var(--light-green); color: var(--forest-green); }
.result-badge.fail { background: #fee2e2; color: #dc2626; }

/* Weak topic tags */
.td-topics { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.topic-tag { font-size: 0.68rem; font-weight: 600; padding: 2px 8px; border-radius: 999px; background: var(--light-yellow); color: #92400e; white-space: nowrap; }
.no-weakness { color: var(--card-border); }

/* Empty / Loading / Error states  */
.empty-state {
  text-align: center;
  padding: 4rem 1.5rem;
  background: var(--white);
  border-radius: var(--radius-lg);
  border: 1.5px dashed var(--card-border);
}

.empty-icon { font-size: 2.5rem; margin-bottom: 0.875rem; }
.empty-state p { color: var(--text-muted); font-size: 0.9375rem; }

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
  font-weight: 500;
  color: #b91c1c;
}

/* Detail slide-in panel */
.panel-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 12, 22, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: flex-end;
  z-index: 1000;
}

.detail-panel {
  background: var(--white);
  width: 420px;
  max-width: 100%;
  height: 100%;
  overflow-y: auto;
  box-shadow: -8px 0 32px rgba(0,0,0,0.12);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.75rem;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--gray-light);
}

.panel-sub { font-size: 0.72rem; color: var(--text-muted); margin-bottom: 2px; font-weight: 500; }
.panel-title { font-size: 1.125rem; font-weight: 800; color: var(--text-main); }

.close-btn {
  width: 32px; height: 32px;
  border: none;
  background: var(--gray-light);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-muted);
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.close-btn:hover { background: #fee2e2; color: #ef4444; }

.panel-score-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.panel-score-big {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1;
}

.panel-score-big.pass { color: var(--forest-green); }
.panel-score-big.fail { color: #dc2626; }

.panel-score-meta { display: flex; flex-direction: column; gap: 4px; }
.panel-score-meta p { font-size: 0.82rem; color: var(--text-muted); }

.panel-section { display: flex; flex-direction: column; gap: 0.625rem; }

.panel-section-title {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* Topic stats inside panel */
.topic-stats-list { display: flex; flex-direction: column; gap: 0.6rem; }

.topic-stat-row {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.topic-name {
  font-size: 0.8rem;
  color: var(--text-main);
  width: 110px;
  flex-shrink: 0;
  font-weight: 500;
}

.topic-bar-wrap {
  flex: 1;
  background: var(--gray-light);
  border-radius: 999px;
  height: 7px;
  overflow: hidden;
}

.topic-bar {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s ease;
}

.topic-bar.good { background: var(--forest-green); }
.topic-bar.bad { background: #ef4444; }

.topic-pct {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
  width: 34px;
  text-align: right;
}

/* Weakness report inside panel */
.weakness-list { display: flex; flex-direction: column; gap: 0.5rem; }

.weakness-item {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  padding: 0.625rem 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.weakness-topic { font-size: 0.72rem; font-weight: 700; color: #dc2626; text-transform: uppercase; letter-spacing: 0.04em; }
.weakness-q { font-size: 0.82rem; color: var(--text-main); }

/* Responsive */
@media (max-width: 900px) {
  .page { padding: 1.25rem 1rem; }
  .stats-bar { grid-template-columns: repeat(3, 1fr); }
  .detail-panel { width: 100%; }
  .chart-bars { gap: 4px; }
}

@media (max-width: 600px) {
  .stats-bar { grid-template-columns: repeat(2, 1fr); }
  .results-table { font-size: 0.78rem; }
  .card-header-row { flex-direction: column; }
  .filters { flex-direction: column; align-items: stretch; }
}
</style>