<template>
  <div class="exam-page">

    <!-- Loading -->
    <div v-if="isLoading" class="loading-state">Loading exam...</div>

    <template v-else-if="session">

      <!-- Top Bar -->
      <div class="top-bar">
        <div class="top-bar-left">
          <h1 class="exam-title">{{ session.title }}</h1>
          <span class="q-progress">{{ currentIndex + 1 }} / {{ session.questions.length }}</span>
        </div>
        <div class="top-bar-right">
          <div v-if="session.time_limit_minutes" :class="['timer', timerWarning ? 'warning' : '']">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            {{ formattedTime }}
          </div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
      </div>

      <!-- Question Navigator -->
      <div class="q-nav">
        <button
          v-for="(q, idx) in session.questions"
          :key="q.id"
          :class="['q-dot', {
            active: idx === currentIndex,
            answered: answers[q.id] !== undefined && answers[q.id] !== '' && answers[q.id] !== null,
            unanswered: answers[q.id] === undefined || answers[q.id] === '' || answers[q.id] === null,
          }]"
          @click="currentIndex = idx"
        >{{ idx + 1 }}</button>
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

        <!-- Fill in the Blank -->
        <div v-else-if="currentQ.type === 'fill_in_the_blank'" class="fill-wrap">
          <input
            v-model="answers[currentQ.id]"
            type="text"
            class="fill-input"
            placeholder="Type your answer..."
          />
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
        <button class="btn-ghost" :disabled="currentIndex === 0" @click="currentIndex--">
          ← Previous
        </button>
        <button
          v-if="currentIndex < session.questions.length - 1"
          class="btn-primary"
          @click="currentIndex++"
        >
          Next →
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
    <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

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
const answers       = ref({})     // { [question_id]: answer }
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
      submit()   // auto-submit when time runs out
    } else {
      timeLeft.value--
    }
  }, 1000)
}

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

// ─── MOCK (remove when API is ready) ───────────────────────────────────────
function loadMock() {
  session.value = {
    id: 1,
    title: 'Midterm 2025 — Microeconomics',
    instructions: 'Closed book. No calculators.',
    time_limit_minutes: 1,
    questions: [
      { id: 'q1', type: 'multiple_choice',   text: 'Which of the following best describes a normal good?', points: 2,
        options: ['Income rises, demand rises', 'Income rises, demand falls', 'Price rises, demand rises', 'Price falls, demand falls'] },
      { id: 'q2', type: 'multiple_choice',   text: 'If the price elasticity of demand is -2, demand is considered?', points: 2,
        options: ['Perfectly elastic', 'Elastic', 'Inelastic', 'Unit elastic'] },
      { id: 'q3', type: 'true_false',        text: 'A monopolist always produces at the socially optimal output level.', points: 1 },
      { id: 'q4', type: 'true_false',        text: 'In perfect competition, economic profit is zero in the long run.', points: 1 },
      { id: 'q5', type: 'short_answer', text: 'The law of ________ states that as price rises, quantity demanded falls.', points: 2 },
      { id: 'q6', type: 'short_answer', text: 'A market with a single seller is called a ________.', points: 2 },
      { id: 'q7', type: 'short_answer',      text: 'Explain the difference between fixed costs and variable costs.', points: 4 },
      { id: 'q8', type: 'multiple_choice',   text: 'Which market structure features many sellers with differentiated products?', points: 2,
        options: ['Perfect competition', 'Monopoly', 'Monopolistic competition', 'Oligopoly'] },
      { id: 'q9', type: 'short_answer',      text: 'Define consumer surplus and illustrate with an example.', points: 4 },
      { id: 'q10', type: 'multiple_choice',  text: 'The Nash equilibrium is a concept in which branch of economics?', points: 2,
        options: ['Behavioral economics', 'Game theory', 'Welfare economics', 'Labor economics'] },
    ],
  }
  startTimer(session.value.time_limit_minutes)
}

onMounted(() => loadMock())   // <- swap to loadSession() before deploy
// onMounted(() => loadSession())
// ───────────────────────────────────────────────────────────────────────────

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
  multiple_choice:   'Multiple Choice',
  true_false:        'True / False',
  fill_in_the_blank: 'Fill in the Blank',
  short_answer:      'Short Answer',
}
function typeLabel(type) { return TYPE_LABELS[type] ?? type }
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.exam-page {
  font-family: 'Sarabun', sans-serif;
  min-height: 100vh;
  padding: 0 0 60px;
  max-width: 760px;
  margin: 0 auto;
  display: flex; flex-direction: column; gap: 0;
}

/* Top Bar */
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 32px 14px;
  background: #fff; border-bottom: 1px solid #e8eaf2;
  position: sticky; top: 0; z-index: 10;
}
.top-bar-left { display: flex; align-items: center; gap: 14px; }
.exam-title   { font-family: 'IBM Plex Sans Thai', sans-serif; font-size: 17px; font-weight: 700; color: #1a1d2e; }
.q-progress   { font-size: 13px; color: #9399aa; }
.timer {
  display: flex; align-items: center; gap: 6px;
  font-size: 15px; font-weight: 700; color: #1a1d2e;
  background: #f7f8fc; border: 1.5px solid #e2e5ef;
  border-radius: 10px; padding: 7px 16px;
  transition: all 0.3s;
}
.timer.warning { background: #fef2f2; border-color: #fca5a5; color: #dc2626; }

/* Progress Bar */
.progress-track {
  height: 3px; background: #e8eaf2;
}
.progress-fill {
  height: 100%; background: #1a1d2e;
  transition: width 0.3s ease;
}

/* Question Navigator */
.q-nav {
  display: flex; flex-wrap: wrap; gap: 7px;
  padding: 16px 32px;
  background: #fff; border-bottom: 1px solid #e8eaf2;
}
.q-dot {
  width: 32px; height: 32px; border-radius: 8px;
  border: 1.5px solid #e2e5ef; background: #fff;
  font-size: 12px; font-weight: 600; color: #555;
  cursor: pointer; transition: all 0.15s;
  display: flex; align-items: center; justify-content: center;
}
.q-dot.active   { background: #1a1d2e; color: #fff; border-color: #1a1d2e; }
.q-dot.answered { background: #dcfce7; border-color: #86efac; color: #16a34a; }
.q-dot.active.answered { background: #1a1d2e; color: #fff; border-color: #1a1d2e; }

/* Question Card */
.question-card {
  margin: 24px 32px;
  background: #fff; border: 1.5px solid #e8eaf2;
  border-radius: 16px; padding: 28px;
  display: flex; flex-direction: column; gap: 20px;
}
.q-header { display: flex; align-items: center; justify-content: space-between; }
.q-type-badge {
  font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 999px;
}
.q-type-badge.multiple_choice   { background: #eff6ff; color: #2563eb; }
.q-type-badge.true_false        { background: #f0fdf4; color: #16a34a; }
.q-type-badge.fill_in_the_blank { background: #faf5ff; color: #7c3aed; }
.q-type-badge.short_answer      { background: #fef3c7; color: #b45309; }
.q-points { font-size: 12.5px; font-weight: 600; color: #9399aa; }

.q-text { font-size: 16px; font-weight: 500; color: #1a1d2e; line-height: 1.6; }

/* Multiple Choice */
.options-list { display: flex; flex-direction: column; gap: 10px; }
.option {
  display: flex; align-items: center; gap: 14px;
  border: 1.5px solid #e2e5ef; border-radius: 11px;
  padding: 13px 16px; cursor: pointer;
  transition: all 0.15s;
}
.option:hover   { border-color: #c7d0e8; background: #f7f8fc; }
.option.selected { border-color: #1a1d2e; background: #f0f1f5; }
.option-letter {
  width: 28px; height: 28px; border-radius: 8px; flex-shrink: 0;
  background: #f0f1f5; font-size: 12px; font-weight: 700; color: #555;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.option.selected .option-letter { background: #1a1d2e; color: #fff; }
.option-text { font-size: 14px; color: #3a3d52; }

/* True / False */
.tf-group { display: flex; gap: 12px; }
.tf-btn {
  flex: 1; padding: 14px; border-radius: 12px;
  border: 1.5px solid #e2e5ef; background: #fff;
  font-size: 15px; font-weight: 600; color: #555;
  text-align: center; cursor: pointer; transition: all 0.15s;
}
.tf-btn:hover   { border-color: #c7d0e8; background: #f7f8fc; }
.tf-btn.selected { border-color: #1a1d2e; background: #f0f1f5; color: #1a1d2e; }

/* Fill / Short */
.fill-wrap { display: flex; flex-direction: column; }
.fill-input {
  border: 1.5px solid #e2e5ef; border-radius: 10px;
  padding: 12px 16px; font-size: 14px;
  font-family: 'Sarabun', sans-serif; color: #1a1d2e;
  outline: none; transition: border-color 0.15s; background: #fdfdff; width: 100%;
}
.fill-input:focus { border-color: #1a1d2e; }
.fill-input.short { resize: vertical; }

/* Nav Row */
.nav-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 32px;
}

/* Buttons */
.btn-primary {
  background: #1a1d2e; color: #fff;
  border: none; border-radius: 10px;
  padding: 11px 28px; font-size: 14px;
  font-family: 'Sarabun', sans-serif; font-weight: 500;
  cursor: pointer; transition: background 0.15s;
}
.btn-primary:hover { background: #2d3251; }

.btn-ghost {
  background: transparent; color: #555;
  border: 1.5px solid #e2e5ef; border-radius: 10px;
  padding: 11px 24px; font-size: 14px;
  font-family: 'Sarabun', sans-serif;
  cursor: pointer; transition: background 0.15s;
}
.btn-ghost:hover:not(:disabled) { background: #f7f8fc; }
.btn-ghost:disabled { opacity: 0.35; cursor: not-allowed; }

.btn-submit {
  background: #16a34a; color: #fff;
  border: none; border-radius: 10px;
  padding: 11px 28px; font-size: 14px;
  font-family: 'Sarabun', sans-serif; font-weight: 600;
  cursor: pointer; transition: background 0.15s;
}
.btn-submit:hover:not(:disabled) { background: #15803d; }
.btn-submit:disabled { opacity: 0.4; cursor: not-allowed; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(10,12,22,0.5);
  backdrop-filter: blur(3px); display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 24px;
}
.modal {
  background: #fff; border-radius: 18px; width: 100%; max-width: 420px;
  padding: 32px; display: flex; flex-direction: column; gap: 14px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.18);
}
.modal-title     { font-size: 18px; font-weight: 700; color: #1a1d2e; }
.modal-body-text { font-size: 14.5px; color: #3a3d52; line-height: 1.6; }
.modal-hint      { font-size: 13px; color: #9399aa; }
.warn-text       { color: #d97706; font-weight: 600; }
.modal-actions   { display: flex; justify-content: flex-end; gap: 10px; padding-top: 6px; }

/* States */
.loading-state { text-align: center; padding: 80px; color: #7c82a0; font-size: 14px; }
.error-banner {
  margin: 0 32px;
  background: #fef2f2; border: 1px solid #fca5a5;
  border-radius: 9px; padding: 12px 16px; font-size: 13.5px; color: #dc2626;
}

@media (max-width: 600px) {
  .top-bar, .q-nav, .question-card, .nav-row { padding-left: 16px; padding-right: 16px; }
  .question-card { margin: 16px; }
  .error-banner  { margin: 0 16px; }
  .tf-group      { flex-direction: column; }
}
</style>