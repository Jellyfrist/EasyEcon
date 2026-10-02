<template>
    <div class="exam-page">
    
        <div v-if="isLoading" class="loading-state">
            <div class="spinner"></div>
            <p>Preparing your exam...</p>
        </div>
    
        <template v-else-if="session">
    
          <div class="top-bar">
            <div class="top-bar-left">
              <div class="header-title-row">
                <button class="back-btn" aria-label="Back to exam session" @click="goExamSet">
                  <span class="material-symbols-outlined">arrow_back</span>
                </button>
                <div class="header-text-group">
                  <span class="course-badge">COURSE EXAM</span>
                  <h1 class="exam-title">{{ session.title }}</h1>
                </div>
              </div>
            </div>
            
            <div class="top-bar-right">
              <div class="progress-pill">
                <span class="progress-pill-text">{{ answeredCount }} of {{ session.questions.length }} answered</span>
              </div>
              <div v-if="session.time_limit_minutes" :class="['timer', timerWarning ? 'warning' : '']">
                <span class="material-symbols-outlined timer-icon">timer</span>
                {{ formattedTime }}
              </div>
            </div>
          </div>
    
          <div class="progress-track-container">
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
            </div>
          </div>
    
          <form class="question-container" @submit.prevent="submit">
            <div v-for="(q, index) in session.questions" :key="q.id" class="question-card">
    
              <p class="q-points">Question {{ index + 1 }} of {{ session.questions.length }}</p>
              <div class="q-header">
                <span :class="['q-type-badge', q.type]">{{ typeLabel(q.type) }}</span>
                <span class="q-points">
                  <span class="material-symbols-outlined icon-sm">stars</span>
                  {{ q.points ?? 1 }} pt{{ (q.points ?? 1) > 1 ? 's' : '' }}
                </span>
              </div>
    
              <div class="q-text" v-html="questionHtml(q)"></div>
              <img v-for="(url, imageIndex) in q.image_urls || []" :key="imageIndex"
                :src="url" alt="Question image" class="q-image" />
    
              <div v-if="q.type === 'multiple_choice'" class="options-list">
                <label
                  v-for="(opt, oi) in q.options"
                  :key="oi"
                  :class="['option', { selected: answers[q.id] === opt }]"
                >
                  <input
                    type="radio"
                    :name="q.id"
                    :value="opt"
                    v-model="answers[q.id]"
                  :disabled="isSubmitting"
                    hidden
                  />
                  <span class="option-letter">{{ String.fromCharCode(65 + oi) }}</span>
                  <span class="option-text">{{ opt }}</span>
                  <span v-if="answers[q.id] === opt" class="material-symbols-outlined check-icon">check_circle</span>
                </label>
              </div>
    
              <div v-else-if="q.type === 'true_false'" class="tf-group">
                <label :class="['tf-btn', { selected: answers[q.id] === 'True' }]">
                  <input type="radio" :name="q.id" value="True" v-model="answers[q.id]"
                    :disabled="isSubmitting" hidden />
                  <span class="tf-label">True</span>
                </label>
                <label :class="['tf-btn', { selected: answers[q.id] === 'False' }]">
                  <input type="radio" :name="q.id" value="False" v-model="answers[q.id]"
                    :disabled="isSubmitting" hidden />
                  <span class="tf-label">False</span>
                </label>
              </div>
    
              <div v-else-if="q.type === 'short_answer' || q.type === 'fill_in_the_blank'" class="fill-wrap">
                <textarea
                  v-model="answers[q.id]"
                    :disabled="isSubmitting"
                  class="fill-input short"
                  :rows="q.type === 'short_answer' ? 5 : 1"
                  placeholder="Type your answer here..."
                ></textarea>
              </div>
    
            </div>
    
            <div class="question-card">
              <p class="modal-body-text" aria-live="polite">You have answered <strong>{{ answeredCount }} out of {{ session.questions.length }}</strong> questions.</p>
              <div v-if="unansweredCount > 0" class="warn-box">
                <span class="material-symbols-outlined">warning</span>
                <span>You have <strong>{{ unansweredCount }}</strong> unanswered question{{ unansweredCount > 1 ? 's' : '' }}.</span>
              </div>
              <p class="modal-hint">Once submitted, you cannot change your answers.</p>
              <div class="nav-row">
                <button type="submit" class="btn-primary" :disabled="isSubmitting">
                  <span class="material-symbols-outlined" aria-hidden="true">send</span>
                  {{ isSubmitting ? 'Submitting...' : 'Submit Exam' }}
                </button>
              </div>
              <div v-if="error" class="error-banner" role="alert">{{ error }}</div>
            </div>
          </form>
</template>

    <div v-if="error && !session" class="error-banner" role="alert">
      <span class="material-symbols-outlined">error</span>
      {{ error }}
    </div>



  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '@/services/examService'
import { questionHtml } from '@/utils/questionHtml'

const route = useRoute()
const router = useRouter()
const sessionId = route.params.sessionId

// --- State ---
const session = ref(null)
const isLoading = ref(false)
const isSubmitting = ref(false)
const error = ref(null)
const answers = ref({})

// --- Timer ---
const timeLeft = ref(0)
let timerInterval = null

const formattedTime = computed(() => {
    const m = Math.floor(timeLeft.value / 60).toString().padStart(2, '0')
    const s = (timeLeft.value % 60).toString().padStart(2, '0')
    return `${m}:${s}`
})
const timerWarning = computed(() => timeLeft.value <= 300 && timeLeft.value > 0) // last 5 min

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
        error.value = err ?.response ?.data ?.detail ?? 'Failed to load exam.'
    } finally {
        isLoading.value = false
    }
}

onMounted(() => loadSession())
onUnmounted(() => clearInterval(timerInterval))

// --- Computed ---
const progressPct = computed(() => {
    const total = session.value?.questions.length ?? 0
    return total ? (answeredCount.value / total) * 100 : 0
})

const answeredCount = computed(() =>
    session.value ?.questions.filter(q => {
        const a = answers.value[q.id]
        return a !== undefined && a !== null && String(a).trim() !== ''
    }).length ?? 0
)
const unansweredCount = computed(() =>
    (session.value ?.questions.length ?? 0) - answeredCount.value
)

// --- Submit ---
async function submit() {
    if (isSubmitting.value || !session.value) return
    isSubmitting.value = true
    error.value = null
    try {
        const payload = {
            session_id: Number(sessionId),
            answers: { ...answers.value },
        }
        const res = await examService.submitAttempt(payload)
        const attempt = res.data ?? res
        clearInterval(timerInterval)
        router.replace({ name: 'ExamResult', params: { attemptId: attempt.id } })
    } catch (err) {
        console.error('Failed to submit', err)
        error.value = err ?.response ?.data ?.detail ?? 'Submission failed. Please try again.'
        isSubmitting.value = false
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

function goExamSet() {
    router.push({
        name: 'ExamSession',
        params: { sessionId: sessionId }
    });
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap');
/* =====================================================
   Base Layout
   ===================================================== */

.exam-page {
    background: linear-gradient(135deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
    min-height: 100vh;
    font-family: 'DM Sans', 'Sarabun', sans-serif;
    display: flex;
    flex-direction: column;
}

.material-symbols-outlined {
    vertical-align: middle;
}

.icon-sm {
    font-size: 18px;
    margin-right: 4px;
}

/* =====================================================
   Top Bar
   ===================================================== */

.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 2.5rem 3rem 1.5rem;
    background: transparent;
    box-shadow: none;
    border-bottom: none !important;
    position: sticky;
    top: 0;
    z-index: 20;
}

.header-title-row {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.back-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: #ffffff;
    border: 1.5px solid #fce4ec;
    color: #df4a7d;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 10px rgba(223, 74, 125, 0.1);
    padding: 0;
}

.back-btn:hover {
    background: #df4a7d;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(223, 74, 125, 0.2);
}

.header-text-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.course-badge {
    font-size: 0.8rem;
    font-weight: 800;
    color: #df4a7d;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.exam-title {
    font-size: 1.8rem;
    font-weight: 900;
    color: #111827;
    margin: 0;
    letter-spacing: -0.02em;
}

.top-bar-right {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.progress-pill {
    background: rgba(255, 255, 255, 0.7);
    padding: 8px 24px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.progress-pill-text {
    font-size: 0.95rem;
    font-weight: 800;
    color: #4b5563;
}

.timer {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.15rem;
    font-weight: 800;
    color: #111827;
    background: #ffffff;
    border: 1.5px solid #e5e7eb;
    padding: 8px 24px;
    border-radius: 999px;
    min-width: 120px;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.timer-icon {
    color: #6b7280;
    font-size: 20px;
}

.timer.warning {
    border-color: #ef4444;
    color: #ef4444;
    background: #fef2f2;
    animation: pulse 1s infinite alternate;
}

.timer.warning .timer-icon {
    color: #ef4444;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
    }
    100% {
        box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
    }
}

/* =====================================================
   Progress Track
   ===================================================== */

.progress-track-container {
    display: flex;
    justify-content: center;
    width: 100%;
    padding: 0 2rem;
    box-sizing: border-box;
}

.progress-track {
    height: 6px;
    background: rgba(0, 0, 0, 0.05);
    width: 100%;
    max-width: 1000px;
    border-radius: 99px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #f59e0b, #df4a7d);
    transition: width 0.4s ease;
    border-radius: 99px;
}

/* =====================================================
   Question Navigator
   ===================================================== */

.question-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    max-width: 860px;
    margin: 0 auto;
    width: 100%;
    box-sizing: border-box;
}

.question-card {
    background: #ffffff;
    border-radius: 24px;
    padding: 3.5rem;
    width: 100%;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
    margin-bottom: 2.5rem;
    box-sizing: border-box;
}

.q-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
    border-bottom: 2px dashed #f3f4f6;
    padding-bottom: 1.5rem;
}

.q-type-badge {
    font-size: 0.8rem;
    font-weight: 800;
    padding: 6px 16px;
    border-radius: 99px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.q-type-badge.multiple_choice {
    background: #fef3c7;
    color: #b45309;
}

.q-type-badge.true_false {
    background: #fef3c7;
    color: #b45309;
}

.q-type-badge.fill_in_the_blank {
    background: #f3e8ff;
    color: #6d28d9;
}

.q-type-badge.short_answer {
    background: #fce4ec;
    color: #be185d;
}

.q-points {
    display: flex;
    align-items: center;
    font-size: 1rem;
    font-weight: 700;
    color: #6b7280;
}

.q-text {
    font-size: 1.4rem;
    font-weight: 400;
    color: #111827;
    line-height: 1.6;
    margin-bottom: 2.5rem;
    white-space: pre-wrap;
}
.q-text :deep(img) { display: block; max-width: 100%; max-height: 420px; object-fit: contain; margin: 12px 0 20px; }

/* Options */

.options-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.option {
    display: flex;
    align-items: center;
    gap: 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    background: #ffffff;
}

.option:hover {
    border-color: #ffc7db;
    background: #fffafb;
    transform: translateX(4px);
}

.option.selected {
    border-color: #df4a7d;
    background: #fff0f5;
    box-shadow: 0 4px 15px rgba(223, 74, 125, 0.1);
}

.option-letter {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    background: #f3f4f6;
    font-size: 0.9rem;
    font-weight: 800;
    color: #6b7280;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.option.selected .option-letter {
    background: #df4a7d;
    color: #ffffff;
}

.option-text {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1f2937;
    flex: 1;
}

.check-icon {
    color: #df4a7d;
    font-size: 24px;
}

/* True / False */

.tf-group {
    display: flex;
    gap: 1.5rem;
}

.tf-btn {
    flex: 1;
    padding: 1.5rem;
    border-radius: 16px;
    border: 2px solid #e5e7eb;
    background: #ffffff;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.tf-label {
    font-size: 1.2rem;
    font-weight: 800;
    color: #4b5563;
}

.tf-btn:hover {
    border-color: #d1d5db;
    background: #f9fafb;
}

.tf-btn.selected {
    border-color: #df4a7d;
    background: #fff0f5;
    box-shadow: 0 4px 15px rgba(223, 74, 125, 0.1);
}

.tf-btn.selected .tf-label {
    color: #df4a7d;
}

/* Fill Input */

.fill-input {
    width: 100%;
    border: 2px solid #e5e7eb;
    border-radius: 16px;
    padding: 1.25rem;
    font-size: 1.1rem;
    font-family: inherit;
    color: #111827;
    outline: none;
    transition: border-color 0.2s ease;
    background: #faf9f7;
    box-sizing: border-box;
}

.fill-input:focus {
    border-color: #df4a7d;
    background: #ffffff;
    box-shadow: 0 0 0 4px rgba(223, 74, 125, 0.1);
}

/* =====================================================
   Navigation Row
   ===================================================== */

.nav-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}

.btn-outline {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 32px;
    border-radius: 99px;
    font-size: 1.1rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
    background: rgba(255, 255, 255, 0.6);
    color: #6b7280;
    border: none;
}

.btn-outline:hover:not(:disabled) {
    background: #ffffff;
    color: #111827;
}

.btn-outline:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.btn-primary,
.btn-submit {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 32px;
    border-radius: 99px;
    font-size: 1.1rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
    margin-left: auto;
}

.btn-primary {
    background: #df4a7d;
    color: #ffffff;
    border: none;
    box-shadow: 0 4px 15px rgba(223, 74, 125, 0.25);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(223, 74, 125, 0.35);
}

.btn-submit {
    background: #10b981;
    color: #ffffff;
    border: none;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25);
}

.btn-submit:hover {
    transform: translateY(-2px);
    background: #059669;
}

/* =====================================================
   Modal
   ===================================================== */

.modal-body-text {
    font-size: 1.1rem;
    color: #4b5563;
    margin-bottom: 1.5rem;
}

.warn-box {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: #fef3c7;
    color: #b45309;
    padding: 12px;
    border-radius: 12px;
    margin-top: 1rem;
    font-size: 0.95rem;
}

.modal-hint {
    font-size: 0.9rem;
    color: #9ca3af;
    margin-bottom: 2rem;
}

/* Loading & Error */

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 60vh;
    gap: 1rem;
    color: #6b7280;
    font-weight: 600;
    font-size: 1.1rem;
}

.spinner {
    width: 48px;
    height: 48px;
    border: 4px solid #fce4ec;
    border-top-color: #df4a7d;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    100% {
        transform: rotate(360deg);
    }
}

.error-banner {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    color: #b91c1c;
    padding: 1rem;
    margin: 2rem auto;
    border-radius: 12px;
    max-width: 600px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
}

/* Responsive */

@media (max-width: 768px) {
    .top-bar {
        padding: 1.5rem;
        flex-direction: column;
        align-items: flex-start;
        gap: 1.5rem;
    }
    .top-bar-right {
        width: 100%;
        justify-content: space-between;
    }
    .question-container {
        padding: 1rem;
    }
    .question-card {
        padding: 2rem 1.5rem;
    }
    .tf-group {
        flex-direction: column;
    }
}
.q-image { display: block; max-width: 100%; max-height: 420px; object-fit: contain; margin: 12px 0 20px; }
</style>
