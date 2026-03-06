<template>

  <!-- This has MOCK DATA for you to test -->

  <div class="page">

    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <button class="back-btn" @click="$router.back()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
        </button>
        <div>
          <p class="breadcrumb">Session #{{ sessionId }}</p>
          <h1 class="page-title">{{ session?.title ?? 'Exam Results' }}</h1>
        </div>
      </div>
      <span :class="['session-badge', session?.is_open ? 'open' : 'closed']">
        {{ session?.is_open ? 'Open' : 'Closed' }}
      </span>
    </div>

    <div v-if="isLoading" class="loading-state">Loading results...</div>

    <template v-else-if="!results.length">
      <div class="empty-state">
        <div class="empty-icon">📭</div>
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
              <button :class="['tab', { active: filterStatus === 'all' }]"    @click="filterStatus = 'all'">All</button>
              <button :class="['tab', { active: filterStatus === 'passed' }]" @click="filterStatus = 'passed'">Passed</button>
              <button :class="['tab', { active: filterStatus === 'failed' }]" @click="filterStatus = 'failed'">Failed</button>
            </div>
            <div class="filter-tabs">
              <button :class="['tab', { active: sortBy === 'rank' }]"       @click="sortBy = 'rank'">Rank</button>
              <button :class="['tab', { active: sortBy === 'score_asc' }]"  @click="sortBy = 'score_asc'">Score ↑</button>
              <button :class="['tab', { active: sortBy === 'submitted' }]"  @click="sortBy = 'submitted'">Time</button>
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

    <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

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
const session         = ref(null)
const results         = ref([])
const isLoading       = ref(false)
const error           = ref(null)
const searchQuery     = ref('')
const filterStatus    = ref('all')
const sortBy          = ref('rank')
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

// ─── MOCK (remove when API is ready) ───────────────────────────────────────
function loadMock() {
  session.value = {
    id: 1,
    title: 'Midterm 2025 — Microeconomics Sec.1',
    is_open: false,
  }

  const TOPICS = ['Demand & Supply', 'Elasticity', 'Market Structure', 'Cost Theory', 'Game Theory']
  const students = [
    'Alice', 'Bob', 'Charlie', 'Diana', 'Eve',
    'Frank', 'Grace', 'Henry', 'Iris', 'James',
    'Karen', 'Leo', 'Mia', 'Nathan', 'Olivia',
    'Paul', 'Quinn', 'Rachel', 'Sam', 'Tina',
  ]

  const MAX = 50
  const PASSING_PCT = 60

  results.value = students.map((name, i) => {
    const score = Math.round(10 + Math.random() * 40)   // 10–50
    const score_pct = Math.round((score / MAX) * 100 * 10) / 10
    const passed = score_pct >= PASSING_PCT

    // Random weak topics (0–2)
    const weakCount = Math.floor(Math.random() * 3)
    const weakness_report = Array.from({ length: weakCount }, () => {
      const topic = TOPICS[Math.floor(Math.random() * TOPICS.length)]
      return { topic, question_text: `Question related to ${topic}` }
    })

    // topic_stats
    const topic_stats = Object.fromEntries(
      TOPICS.map(t => [t, { correct: Math.floor(Math.random() * 5), total: 5 }])
    )

    return {
      id: i + 1,
      student_id: name,
      session_id: 1,
      score,
      max_score: MAX,
      score_pct,
      passed,
      percentile: Math.round(((students.length - i) / students.length) * 100),
      topic_stats,
      weakness_report,
      started_at: new Date(Date.now() - (90 + i * 3) * 60000).toISOString(),
      submitted_at: new Date(Date.now() - (10 + i * 2) * 60000).toISOString(),
    }
  })
}

onMounted(() => loadMock())   // <- swap to loadResults() before deploy
// // onMounted(() => loadResults())

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
* { box-sizing: border-box; margin: 0; padding: 0; }

.page {
  font-family: 'Sarabun', sans-serif;
  min-height: 100vh;
  padding: 32px;
  max-width: 1200px;
  margin: 0 auto;
  display: flex; flex-direction: column; gap: 20px;
}

/* Header */
.header { display: flex; align-items: center; justify-content: space-between; }
.header-left { display: flex; align-items: center; gap: 14px; }
.back-btn {
  width: 38px; height: 38px; border: 1.5px solid #dde1ea; background: #fff;
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #555; transition: all 0.15s; flex-shrink: 0;
}
.back-btn:hover { background: #f0f1f5; }
.breadcrumb { font-size: 12px; color: #9399aa; margin-bottom: 2px; }
.page-title { font-family: 'IBM Plex Sans Thai', sans-serif; font-size: 22px; font-weight: 700; color: #1a1d2e; }
.session-badge { font-size: 12px; font-weight: 600; padding: 5px 14px; border-radius: 999px; }
.session-badge.open   { background: #dcfce7; color: #16a34a; }
.session-badge.closed { background: #f3f4f6; color: #6b7280; }

/* Stats Bar */
.stats-bar { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; }
.stat-card {
  background: #fff; border: 1px solid #e8eaf2; border-radius: 14px;
  padding: 16px 18px; display: flex; flex-direction: column; gap: 4px;
}
.stat-card.accent { border-left: 3px solid #1a1d2e; }
.stat-num        { font-size: 24px; font-weight: 700; color: #1a1d2e; line-height: 1; }
.stat-num.green  { color: #16a34a; }
.stat-num.red    { color: #dc2626; }
.stat-label      { font-size: 12px; color: #7c82a0; }

/* Card */
.card {
  background: #fff; border: 1px solid #e8eaf2;
  border-radius: 14px; padding: 24px;
  display: flex; flex-direction: column; gap: 18px;
}
.card-title { font-size: 15px; font-weight: 700; color: #1a1d2e; }
.card-header-row { display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 12px; }

/* Distribution Chart */
.chart-wrap { display: flex; flex-direction: column; gap: 12px; }
.chart-bars { display: flex; align-items: flex-end; gap: 8px; height: 170px; }
.chart-col  { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 1; }
.bar-count  { font-size: 11px; font-weight: 600; color: #555; }
.bar        { width: 100%; border-radius: 5px 5px 0 0; transition: height 0.3s ease; }
.bar-green  { background: #22c55e; }
.bar-yellow { background: #f59e0b; }
.bar-red    { background: #ef4444; }
.bar-label  { font-size: 10px; color: #9399aa; white-space: nowrap; transform: rotate(-35deg); transform-origin: top center; margin-top: 6px; }
.chart-legend { display: flex; align-items: center; gap: 14px; padding-top: 8px; border-top: 1px solid #f0f1f5; }
.legend-dot   { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.legend-dot.green  { background: #22c55e; }
.legend-dot.yellow { background: #f59e0b; }
.legend-dot.red    { background: #ef4444; }
.chart-legend span { font-size: 12.5px; color: #555; }

/* Percentile Table */
.pct-table { width: 100%; border-collapse: collapse; }
.pct-table thead tr { background: #f7f8fc; border-bottom: 1.5px solid #e8eaf2; }
.pct-table th {
  padding: 10px 14px; font-size: 11.5px; font-weight: 700;
  color: #7c82a0; text-align: left; text-transform: uppercase; letter-spacing: 0.05em;
}
.pct-table td { padding: 11px 14px; font-size: 13.5px; color: #1a1d2e; border-bottom: 1px solid #f0f1f5; }
.pct-table tr:last-child td { border-bottom: none; }
.pct-label { font-weight: 600; }
.mini-bar-wrap { display: flex; align-items: center; gap: 8px; }
.mini-bar { height: 6px; background: #1a1d2e; border-radius: 999px; min-width: 2px; max-width: 120px; }

/* Filters */
.filters { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.search-box {
  display: flex; align-items: center; gap: 8px;
  background: #f7f8fc; border: 1.5px solid #e2e5ef;
  border-radius: 9px; padding: 7px 12px; min-width: 190px;
}
.search-box input {
  border: none; outline: none; font-size: 13.5px;
  font-family: 'Sarabun', sans-serif; background: transparent; color: #1a1d2e; width: 100%;
}
.filter-tabs { display: flex; gap: 5px; }
.tab {
  padding: 6px 13px; border-radius: 8px; border: 1.5px solid #e2e5ef;
  background: #fff; font-size: 12.5px; font-family: 'Sarabun', sans-serif;
  cursor: pointer; color: #555; transition: all 0.15s;
}
.tab.active { background: #1a1d2e; color: #fff; border-color: #1a1d2e; }
.tab:hover:not(.active) { background: #f0f1f5; }

/* Results Table */
.results-table { width: 100%; border-collapse: collapse; }
.results-table thead tr { background: #f7f8fc; border-bottom: 1.5px solid #e8eaf2; }
.results-table th {
  padding: 11px 14px; font-size: 11.5px; font-weight: 700;
  color: #7c82a0; text-align: left; text-transform: uppercase; letter-spacing: 0.05em; white-space: nowrap;
}
.result-row { border-bottom: 1px solid #f0f1f5; cursor: pointer; transition: background 0.12s; }
.result-row:last-child { border-bottom: none; }
.result-row:hover { background: #f7f8fc; }
.result-row.selected { background: #eff6ff; }
.results-table td { padding: 11px 14px; font-size: 13.5px; color: #1a1d2e; vertical-align: middle; }

.td-rank { width: 48px; }
.medal   { font-size: 16px; }
.rank-num { font-size: 13px; color: #9399aa; font-weight: 600; }
.td-student { font-weight: 600; }
.score-val  { font-weight: 700; }
.score-max  { color: #9399aa; font-size: 12px; }
.td-percentile { color: #7c82a0; }
.td-time { color: #7c82a0; font-size: 12.5px; white-space: nowrap; }

.pct-bar-wrap { display: flex; align-items: center; gap: 8px; min-width: 120px; }
.pct-bar { height: 6px; border-radius: 999px; }

.result-badge { font-size: 11.5px; font-weight: 600; padding: 3px 10px; border-radius: 999px; }
.result-badge.pass { background: #dcfce7; color: #16a34a; }
.result-badge.fail { background: #fef2f2; color: #dc2626; }

.td-topics { display: flex; gap: 5px; flex-wrap: wrap; }
.topic-tag { font-size: 11px; padding: 2px 9px; border-radius: 999px; background: #fef3c7; color: #b45309; white-space: nowrap; }
.no-weakness { color: #c4c8d8; }

/* Empty / Loading / Error */
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

/* Detail Panel */
.panel-overlay {
  position: fixed; inset: 0; background: rgba(10,12,22,0.45);
  backdrop-filter: blur(3px); display: flex; justify-content: flex-end; z-index: 1000;
}
.detail-panel {
  background: #fff; width: 420px; max-width: 100%; height: 100%;
  overflow-y: auto; box-shadow: -8px 0 32px rgba(0,0,0,0.12);
  display: flex; flex-direction: column; gap: 24px; padding: 28px;
}
.panel-header { display: flex; align-items: flex-start; justify-content: space-between; }
.panel-sub    { font-size: 12px; color: #9399aa; margin-bottom: 2px; }
.panel-title  { font-size: 18px; font-weight: 700; color: #1a1d2e; }
.close-btn {
  width: 32px; height: 32px; border: none; background: #f0f1f5;
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: #555; flex-shrink: 0;
}
.close-btn:hover { background: #e2e5ef; }
.panel-score-row { display: flex; align-items: center; gap: 20px; }
.panel-score-big { font-size: 48px; font-weight: 800; line-height: 1; }
.panel-score-big.pass { color: #16a34a; }
.panel-score-big.fail { color: #dc2626; }
.panel-score-meta { display: flex; flex-direction: column; gap: 4px; }
.panel-score-meta p { font-size: 13px; color: #555; }
.panel-section { display: flex; flex-direction: column; gap: 10px; }
.panel-section-title { font-size: 12px; font-weight: 700; color: #3a3d52; text-transform: uppercase; letter-spacing: 0.05em; }
.topic-stats-list { display: flex; flex-direction: column; gap: 9px; }
.topic-stat-row { display: flex; align-items: center; gap: 10px; }
.topic-name { font-size: 13px; color: #3a3d52; width: 110px; flex-shrink: 0; }
.topic-bar-wrap { flex: 1; background: #f0f1f5; border-radius: 999px; height: 7px; overflow: hidden; }
.topic-bar { height: 100%; border-radius: 999px; transition: width 0.3s; }
.topic-bar.good { background: #22c55e; }
.topic-bar.bad  { background: #ef4444; }
.topic-pct { font-size: 12px; font-weight: 600; color: #555; width: 34px; text-align: right; }
.weakness-list { display: flex; flex-direction: column; gap: 8px; }
.weakness-item { background: #fef2f2; border: 1px solid #fecaca; border-radius: 9px; padding: 10px 14px; display: flex; flex-direction: column; gap: 3px; }
.weakness-topic { font-size: 12px; font-weight: 700; color: #dc2626; }
.weakness-q     { font-size: 13px; color: #3a3d52; }

/* Responsive */
@media (max-width: 900px) {
  .page { padding: 20px 16px; }
  .stats-bar { grid-template-columns: repeat(3, 1fr); }
  .detail-panel { width: 100%; }
  .chart-bars { gap: 4px; }
}
@media (max-width: 600px) {
  .stats-bar { grid-template-columns: repeat(2, 1fr); }
  .results-table { font-size: 12px; }
  .card-header-row { flex-direction: column; }
}
</style>