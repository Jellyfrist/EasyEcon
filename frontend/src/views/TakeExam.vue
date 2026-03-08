<template>
  <div class="exam-page">

    <!-- Loading -->
    <div v-if="isLoading" class="loading-state">Loading exam...</div>

    <template v-else-if="session">

      <!-- Top Bar -->
      <div class="top-bar">
        <div class="top-bar-left">
          <h1 class="exam-title">{{ session.title }}</h1>
          <div class="progress-pill">
            <div class="progress-pill-fill" :style="{ width: progressPct + '%' }"></div>
            <span class="progress-pill-text">{{ currentIndex + 1 }} / {{ session.questions.length }}</span>
          </div>
        </div>
        <div class="top-bar-right">
          <div v-if="session.time_limit_minutes" :class="['timer', timerWarning ? 'warning' : '']">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            {{ formattedTime }}
          </div>
        </div>
      </div>

      <!-- Progress Bar (thin line) -->
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
      </div>

      <!-- Question Navigator -->
      <div class="q-nav-wrap">
        <button class="q-nav-arrow" :disabled="dotWindowStart === 0" @click="shiftWindow(-1)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15 18l-6-6 6-6"/></svg>
        </button>
        <div class="q-nav">
          <button
            v-for="q in visibleQuestions"
            :key="q.id"
            :class="['q-dot', {
              active: q.idx === currentIndex,
              answered: answers[q.id] !== undefined && answers[q.id] !== '' && answers[q.id] !== null,
            }]"
            @click="currentIndex = q.idx"
          >{{ q.idx + 1 }}</button>
        </div>
        <button class="q-nav-arrow" :disabled="dotWindowStart + DOT_WINDOW >= session.questions.length" @click="shiftWindow(1)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 18l6-6-6-6"/></svg>
        </button>
      </div>

      <!-- Question Card -->
      <div class="question-card">

        <div class="q-header">
          <span :class="['q-type-badge', currentQ.type]">{{ typeLabel(currentQ.type) }}</span>
          <span class="q-points">{{ currentQ.points ?? 1 }} pt{{ (currentQ.points ?? 1) > 1 ? 's' : '' }}</span>
        </div>

        <p class="q-text">{{ currentQ.text }}</p>

        <!-- Multiple Choice -->
        <div v-if="currentQ.type === 'multiple_choice'" class="options-list">
          <label
            v-for="(opt, oi) in currentQ.options"
            :key="oi"
            :class="['option', { selected: answers[currentQ.id] === opt }]"
          >
            <input
              type="radio"
              :name="currentQ.id"
              :value="opt"
              v-model="answers[currentQ.id]"
              hidden
            />
            <span class="option-letter">{{ String.fromCharCode(65 + oi) }}</span>
            <span class="option-text">{{ opt }}</span>
          </label>
        </div>

        <!-- True / False -->
        <div v-else-if="currentQ.type === 'true_false'" class="tf-group">
          <label :class="['tf-btn', { selected: answers[currentQ.id] === 'True' }]">
            <input type="radio" :name="currentQ.id" value="True" v-model="answers[currentQ.id]" hidden />
            True
          </label>
          <label :class="['tf-btn', { selected: answers[currentQ.id] === 'False' }]">
            <input type="radio" :name="currentQ.id" value="False" v-model="answers[currentQ.id]" hidden />
            False
          </label>
        </div>

        <!-- Short Answer -->
        <div v-else-if="currentQ.type === 'short_answer'" class="fill-wrap">
          <textarea
            v-model="answers[currentQ.id]"
            class="fill-input short"
            rows="5"
            placeholder="Write your answer..."
          ></textarea>
        </div>

      </div>

      <!-- Navigation Buttons -->
      <div class="nav-row">
        <button class="btn-prev" :disabled="currentIndex === 0" @click="currentIndex--">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
          Previous
        </button>
        <button
          v-if="currentIndex < session.questions.length - 1"
          class="btn-primary"
          @click="currentIndex++"
        >
          Next
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </button>
        <button
          v-else
          class="btn-submit"
          @click="confirmSubmit = true"
        >
          Submit Exam
        </button>
      </div>

    </template>

    <!-- Error -->
    <div v-if="error" class="error-banner">ERROR: {{ error }}</div>

    <!-- Submit Confirm Modal -->
    <Teleport to="body">
      <div v-if="confirmSubmit" class="modal-overlay" @click.self="confirmSubmit = false">
        <div class="modal">
          <h2 class="modal-title">Submit Exam?</h2>
          <p class="modal-body-text">
            You have answered
            <strong>{{ answeredCount }} / {{ session?.questions.length }}</strong> questions.
            <span v-if="unansweredCount > 0" class="warn-text"> {{ unansweredCount }} question{{ unansweredCount > 1 ? 's' : '' }} left unanswered.</span>
          </p>
          <p class="modal-hint">This action cannot be undone.</p>
          <div class="modal-actions">
            <button class="btn-ghost" @click="confirmSubmit = false" :disabled="isSubmitting">Review</button>
            <button class="btn-submit" @click="submit" :disabled="isSubmitting">
              {{ isSubmitting ? 'Submitting...' : 'Confirm Submit' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '@/services/examService'

const route = useRoute()
const router = useRouter()
const sessionId = route.params.sessionId

// --- State ---
const session       = ref(null)   // ExamSessionStudentResponse
const isLoading     = ref(false)
const isSubmitting  = ref(false)
const error         = ref(null)
const currentIndex  = ref(0)
const answers       = ref({})
const confirmSubmit = ref(false)

// --- Timer ---
const timeLeft = ref(0)
let timerInterval = null

const formattedTime = computed(() => {
  const m = Math.floor(timeLeft.value / 60).toString().padStart(2, '0')
  const s = (timeLeft.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})
const timerWarning = computed(() => timeLeft.value <= 300 && timeLeft.value > 0)  // last 5 min

function startTimer(minutes) {
  timeLeft.value = minutes * 60
  timerInterval = setInterval(() => {
    if (timeLeft.value <= 0) {
      clearInterval(timerInterval)
      submit() // auto-submit when time runs out
    } else {
      timeLeft.value--
    }
  }, 1000)
}

// --- Q-nav window ---
const isMobile       = ref(window.innerWidth <= 600)
const DOT_WINDOW     = computed(() => isMobile.value ? 5 : 10)
const dotWindowStart = ref(0)

function onResize() {
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth <= 600
  if (wasMobile !== isMobile.value) {
    // re-snap window on breakpoint change
    dotWindowStart.value = Math.floor(currentIndex.value / DOT_WINDOW.value) * DOT_WINDOW.value
  }
}

const visibleQuestions = computed(() => {
  if (!session.value) return []
  return session.value.questions
    .map((q, idx) => ({ ...q, idx }))
    .slice(dotWindowStart.value, dotWindowStart.value + DOT_WINDOW.value)
})

function shiftWindow(dir) {
  const total = session.value?.questions.length ?? 0
  const max = Math.max(0, total - DOT_WINDOW.value)
  dotWindowStart.value = Math.min(max, Math.max(0, dotWindowStart.value + dir * DOT_WINDOW.value))
}

// keep active dot inside the visible window
watch(currentIndex, (idx) => {
  if (idx < dotWindowStart.value || idx >= dotWindowStart.value + DOT_WINDOW.value) {
    dotWindowStart.value = Math.floor(idx / DOT_WINDOW.value) * DOT_WINDOW.value
  }
})

// --- Load ---
async function loadSession() {
  isLoading.value = true
  error.value = null
  try {
    const res = await examService.openSession(sessionId)
    session.value = res.data ?? res
    if (session.value.time_limit_minutes) {
      startTimer(session.value.time_limit_minutes)
    }
  } catch (err) {
    console.error('Failed to load session', err)
    error.value = err?.response?.data?.detail ?? 'Failed to load exam.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => loadSession())

onUnmounted(() => clearInterval(timerInterval))

// --- Computed ---
const currentQ = computed(() => session.value?.questions[currentIndex.value])

const progressPct = computed(() => {
  if (!session.value) return 0
  return ((currentIndex.value + 1) / session.value.questions.length) * 100
})

const answeredCount = computed(() =>
  session.value?.questions.filter(q => {
    const a = answers.value[q.id]
    return a !== undefined && a !== '' && a !== null
  }).length ?? 0
)
const unansweredCount = computed(() =>
  (session.value?.questions.length ?? 0) - answeredCount.value
)

// --- Submit ---
async function submit() {
  isSubmitting.value = true
  error.value = null
  clearInterval(timerInterval)
  try {
    // ExamAttemptSubmit: { session_id, answers: { q1: "A", q2: "demand", ... } }
    const payload = {
      session_id: Number(sessionId),
      answers: { ...answers.value },
    }
    const res = await examService.submitAttempt(payload)
    const attempt = res.data ?? res

    // Navigate to result page
    router.replace({ name: 'ExamResult', params: { attemptId: attempt.id } })
  } catch (err) {
    console.error('Failed to submit', err)
    error.value = err?.response?.data?.detail ?? 'Submission failed. Please try again.'
    isSubmitting.value = false
    confirmSubmit.value = false
  }
}

// --- Helpers ---
const TYPE_LABELS = {
  multiple_choice: 'Multiple Choice',
  true_false: 'True / False',
  fill_in_the_blank: 'Fill in the Blank',
  short_answer: 'Short Answer',
}

function typeLabel(type) { 
  return TYPE_LABELS[type] ?? type
}
</script>

<style scoped>
/* ── Page ── */
.exam-page {
  background: #f0ede8;
  min-height: 100vh;
  padding: 0 0 4rem;
  display: flex;
  flex-direction: column;
  gap: 0;
}

/* ── Top Bar ── */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 2rem 1rem;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--card-border);
  position: sticky;
  top: 0;
  z-index: 10;
  gap: 1.5rem;
}

.top-bar-left {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.exam-title {
  font-size: 1.0625rem;
  font-weight: 800;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Progress pill (replaces plain q-progress text) */
.progress-pill {
  position: relative;
  height: 20px;
  background: var(--gray-light);
  border-radius: 999px;
  overflow: hidden;
  width: 100%;
  max-width: 280px;
}

.progress-pill-fill {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  background: linear-gradient(90deg, var(--primary-pink), #f472b6);
  border-radius: 999px;
  transition: width 0.4s ease;
}

.progress-pill-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-main);
  z-index: 1;
  mix-blend-mode: multiply;
}

.timer {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-main);
  background: var(--white);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 0.5rem 1.125rem;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
  flex-shrink: 0;
}

.timer.warning {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
  box-shadow: 0 0 0 3px rgba(239,68,68,0.15);
}

/* ── Progress Bar ── */
.progress-track {
  height: 3px;
  background: var(--card-border);
}

.progress-fill {
  height: 100%;
  background: var(--primary-pink);
  transition: width 0.3s ease;
}

/* ── Question Navigator ── */
.q-nav-wrap {
  display: flex;
  align-items: center;
  background: var(--white);
  border-bottom: 1px solid var(--card-border);
  padding: 0.75rem 1.25rem;
  gap: 0.75rem;
}

.q-nav {
  display: flex;
  gap: 0.5rem;
  flex: 1;
  justify-content: center;
}

.q-nav-arrow {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--white);
  border: 1.5px solid var(--card-border);
  border-radius: 50%;
  cursor: pointer;
  color: var(--text-muted);
  transition: all 0.15s ease;
  box-shadow: var(--shadow-sm);
}

.q-nav-arrow:hover:not(:disabled) {
  border-color: var(--primary-pink);
  color: var(--primary-pink);
  box-shadow: 0 0 0 3px var(--light-pink);
}

.q-nav-arrow:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.q-dot {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: 1.5px solid var(--card-border);
  background: var(--white);
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.18s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

.q-dot:hover {
  border-color: var(--primary-pink);
  color: var(--primary-pink);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(237,64,129,0.18);
}

.q-dot.active {
  background: var(--primary-pink);
  color: var(--white);
  border-color: var(--primary-pink);
  box-shadow: 0 4px 14px rgba(237,64,129,0.4);
  transform: scale(1.1);
}

.q-dot.answered {
  background: var(--light-green);
  border-color: #86efac;
  color: var(--forest-green);
}

.q-dot.active.answered {
  background: var(--primary-pink);
  color: var(--white);
  border-color: var(--primary-pink);
  box-shadow: 0 4px 14px rgba(237,64,129,0.4);
  transform: scale(1.1);
}

/* ── Question Card ── */
.question-card {
  margin: 1.5rem auto;
  width: calc(100% - 4rem);
  max-width: 760px;
  background: var(--white);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-shadow: var(--shadow-sm);
}

.q-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.q-type-badge {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 999px;
  letter-spacing: 0.03em;
}

.q-type-badge.multiple_choice { background: #eff6ff; color: #2563eb; }
.q-type-badge.true_false { background: var(--light-green); color: var(--forest-green); }
.q-type-badge.fill_in_the_blank { background: #faf5ff; color: #7c3aed; }
.q-type-badge.short_answer { background: var(--light-yellow); color: #b45309; }

.q-points {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.q-text {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-main);
  line-height: 1.65;
}

/* ── Multiple Choice ── */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.option {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  padding: 0.8125rem 1rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.option:hover { border-color: var(--light-pink); background: #fff7fa; }
.option.selected { border-color: var(--primary-pink); background: #fff0f5; }

.option-letter {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  flex-shrink: 0;
  background: var(--gray-light);
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.option.selected .option-letter {
  background: var(--primary-pink);
  color: var(--white);
}

.option-text {
  font-size: 0.875rem;
  color: var(--text-main);
}

/* ── True / False ── */
.tf-group {
  display: flex;
  gap: 0.75rem;
}

.tf-btn {
  flex: 1;
  padding: 0.875rem;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--card-border);
  background: var(--white);
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-muted);
  text-align: center;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.tf-btn:hover { border-color: var(--light-pink); background: #fff7fa; }
.tf-btn.selected { border-color: var(--primary-pink); background: #fff0f5; color: var(--primary-pink); }

/* ── Fill / Short Answer ── */
.fill-wrap {
  display: flex;
  flex-direction: column;
}

.fill-input {
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-family: inherit;
  color: var(--text-main);
  outline: none;
  transition: border-color 0.15s ease;
  background: var(--white);
  width: 100%;
}

.fill-input:focus { border-color: var(--primary-pink); }
.fill-input.short { resize: vertical; }

/* ── Nav Row ── */
.nav-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  max-width: 760px;
  width: 100%;
  margin: 0 auto;
}

/* ── Buttons ── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--primary-pink);
  color: var(--white);
  border: none;
  border-radius: 999px;
  padding: 0.6875rem 1.75rem;
  font-size: 0.875rem;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 4px 14px rgba(237,64,129,0.35);
}

.btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); box-shadow: 0 6px 18px rgba(237,64,129,0.45); }
.btn-primary:active { transform: scale(0.98); }

.btn-ghost {
  background: transparent;
  color: var(--text-muted);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  padding: 0.6875rem 1.5rem;
  font-size: 0.875rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-ghost:hover:not(:disabled) { background: var(--gray-light); color: var(--text-main); }
.btn-ghost:disabled { opacity: 0.35; cursor: not-allowed; }

.btn-prev {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
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

.btn-prev:hover:not(:disabled) {
  border-color: var(--primary-pink);
  color: var(--primary-pink);
  box-shadow: 0 0 0 3px var(--light-pink);
}

.btn-prev:disabled { opacity: 0.3; cursor: not-allowed; }

.btn-submit {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--forest-green);
  color: var(--white);
  border: none;
  border-radius: 999px;
  padding: 0.6875rem 1.75rem;
  font-size: 0.875rem;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.15s ease;
}

.btn-submit:hover:not(:disabled) { background: #085f32; transform: translateY(-1px); }
.btn-submit:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(30, 35, 60, 0.5);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1.5rem;
}

.modal {
  background: var(--white);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 420px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  box-shadow: 0 24px 60px rgba(0,0,0,0.18);
}

.modal-title { font-size: 1.125rem; font-weight: 700; color: var(--text-main); }
.modal-body-text { font-size: 0.9rem; color: var(--text-main); line-height: 1.6; }
.modal-hint { font-size: 0.8125rem; color: var(--text-muted); }
.warn-text { color: #d97706; font-weight: 600; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.625rem;
  padding-top: 0.375rem;
}

/* ── States ── */
.loading-state {
  text-align: center;
  padding: 5rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 2rem;
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
  .top-bar,
  .q-nav,
  .nav-row { padding-left: 1rem; padding-right: 1rem; }
  .question-card { margin: 1rem auto; width: calc(100% - 2rem); }
  .error-banner { margin: 0 1rem; }
  .tf-group { flex-direction: column; }
}
</style>