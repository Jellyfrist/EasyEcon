/**
 * Student Exam Session Composable
 * --------------------------------
 * Handles:
 *  - loading exam session
 *  - navigating questions
 *  - storing answers
 *  - countdown timer
 *  - submitting attempt
 */

import { ref, computed, onUnmounted } from 'vue'
import examService from '@/services/examService'

export function useExamSession(sessionId) {

  // ===============================
  // STATE
  // ===============================

  const session = ref(null)
  const questions = ref([])
  const currentIndex = ref(0)

  const answers = ref({}) // { questionId: answer }

  const isLoading = ref(false)
  const isSubmitting = ref(false)
  const error = ref(null)

  const result = ref(null)

  const timeLeft = ref(0)
  const timerExpired = ref(false)

  let timer = null

  // ===============================
  // COMPUTED
  // ===============================

  const currentQuestion = computed(() => questions.value[currentIndex.value] ?? null)

  const totalQuestions = computed(() => questions.value.length)

  const answeredCount = computed(() => Object.keys(answers.value).length)

  const progressPct = computed(() => {
    if (!totalQuestions.value) return 0
    return Math.round((answeredCount.value / totalQuestions.value) * 100)
  })

  const timeDisplay = computed(() => {
    const m = Math.floor(timeLeft.value / 60).toString().padStart(2, '0')
    const s = (timeLeft.value % 60).toString().padStart(2, '0')
    return `${m}:${s}`
  })

  const isTimeWarning = computed(() => timeLeft.value <= 300 && timeLeft.value > 0)

  // ===============================
  // LOAD SESSION
  // ===============================

  async function load() {
    isLoading.value = true
    error.value = null

    try {

      const { data } = await examService.getSession(sessionId)

      session.value = data

      // backend: question_snapshot
      questions.value = data.question_snapshot ?? []

      // backend: time_limit_minutes
      timeLeft.value = (data.time_limit_minutes ?? 60) * 60

      startTimer()

    } catch (err) {

      error.value = err?.response?.data?.detail ?? 'Failed to load exam session'

    } finally {
      isLoading.value = false
    }
  }

  // ===============================
  // TIMER
  // ===============================

  function startTimer() {

    timer = setInterval(() => {

      if (timeLeft.value <= 0) {
        timerExpired.value = true
        clearInterval(timer)
        submit()
        return
      }

      timeLeft.value--

    }, 1000)

  }

  // ===============================
  // ANSWERS
  // ===============================

  function selectAnswer(questionId, value) {

    answers.value = {
      ...answers.value,
      [questionId]: value
    }

  }

  // ===============================
  // NAVIGATION
  // ===============================

  function goTo(index) {
    if (index < 0 || index >= totalQuestions.value) return
    currentIndex.value = index
  }

  function next() {
    goTo(currentIndex.value + 1)
  }

  function prev() {
    goTo(currentIndex.value - 1)
  }

  function questionStatus(index) {

    const q = questions.value[index]

    if (!q) return 'pending'

    if (index === currentIndex.value) return 'current'

    return answers.value[q.id] ? 'answered' : 'pending'

  }

  // ===============================
  // SUBMIT
  // ===============================

  async function submit() {

    if (isSubmitting.value) return

    isSubmitting.value = true

    clearInterval(timer)

    try {

      const payload = {
        session_id: sessionId,
        answers: answers.value
      }

      const { data } = await examService.submitAttempt(payload)

      result.value = data

    } catch (err) {

      error.value = err?.response?.data?.detail ?? 'Submission failed'

    } finally {

      isSubmitting.value = false

    }

  }

  // ===============================
  // CLEANUP
  // ===============================

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  return {

    // state
    session,
    questions,
    currentIndex,
    answers,
    result,
    error,

    isLoading,
    isSubmitting,

    timeLeft,
    timerExpired,

    // computed
    currentQuestion,
    totalQuestions,
    answeredCount,
    progressPct,
    timeDisplay,
    isTimeWarning,

    // actions
    load,
    selectAnswer,
    goTo,
    next,
    prev,
    submit,
    questionStatus

  }
}