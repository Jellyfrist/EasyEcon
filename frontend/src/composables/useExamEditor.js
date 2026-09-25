/**
 * Exam Editor (compatible with exam.py backend)
 * All questions are stored in question_data JSON.
 */

import { ref, computed } from 'vue'
import examService from '@/services/examService'

let _lid = 0
const lid = () => `local_${++_lid}`

export function useExamTemplateEditor(courseId) {

  /* ================================
      Template metadata
  ================================= */

  const templateId = ref(null)
  const title = ref('')
  const examType = ref('midterm')
  const academicYear = ref('')

  /* ================================
      Questions (local JSON)
  ================================= */

  const localQuestions = ref([])

  const isSaving = ref(false)
  const isLoading = ref(false)
  const error = ref(null)
  const lastSaved = ref(null)

  /* ================================
      Computed
  ================================= */

  const totalQuestions = computed(() => localQuestions.value.length)

  const totalPoints = computed(() =>
    localQuestions.value.reduce((sum, q) => sum + (q.points || 0), 0)
  )

  const incompleteCount = computed(() =>
    localQuestions.value.filter(q =>
      !q.question_text?.trim() ||
      q.options.some(o => !o.text?.trim()) ||
      !q.correct_answer
    ).length
  )

  /* ================================
      Helpers
  ================================= */

  const defaultOptions = () => [
    { key: 'A', text: '' },
    { key: 'B', text: '' },
    { key: 'C', text: '' },
    { key: 'D', text: '' }
  ]

  /* ================================
      Load existing template
  ================================= */

  async function load(existingTemplateId) {

    if (!existingTemplateId) return

    isLoading.value = true
    error.value = null

    try {

      const data = await examService.getTemplate(existingTemplateId)

      templateId.value = data.id
      title.value = data.title
      examType.value = data.exam_type
      academicYear.value = data.academic_year ?? ''

      const questions = data.question_data ?? []

      localQuestions.value = questions.map((q, i) => ({
        _lid: lid(),
        type: q.type || 'mcq', // Add to handel DYNAMIC QUESTION COMPONENT in ExamQuestionEditor.vue
        question_text: q.question_text,
        options: q.options,
        correct_answer: q.correct_answer,
        explanation: q.explanation ?? '',
        topic_tag: q.topic_tag ?? '',
        points: q.points ?? 5,
        order_index: i
      }))

    } catch (e) {

      error.value = e?.response?.data?.detail ?? 'Failed to load exam template'

    } finally {

      isLoading.value = false

    }
  }

  /* ================================
      Question manipulation
  ================================= */

  function addEmptyQuestion() {

    localQuestions.value.push({
      _lid: lid(),
      type: 'mcq', // Add to handel DYNAMIC QUESTION COMPONENT in ExamQuestionEditor.vue
      question_text: '',
      options: defaultOptions(),
      correct_answer: '',
      explanation: '',
      topic_tag: '',
      points: 5,
      order_index: localQuestions.value.length
    })
  }

  function updateLocalQuestion(localId, field, value) {

    const q = localQuestions.value.find(q => q._lid === localId)

    if (!q) return

    q[field] = value
  }

  function updateOption(localId, optionKey, text) {

    const q = localQuestions.value.find(q => q._lid === localId)

    if (!q) return

    const opt = q.options.find(o => o.key === optionKey)

    if (opt) opt.text = text
  }

  function removeLocalQuestion(localId) {

    localQuestions.value = localQuestions.value.filter(q => q._lid !== localId)

    localQuestions.value.forEach((q, i) => {
      q.order_index = i
    })
  }

  /* ================================
      Save template
  ================================= */

  async function save() {

    isSaving.value = true
    error.value = null

    try {

      const questionData = localQuestions.value
        .filter(q => q.question_text.trim() && q.correct_answer)
        .map((q, i) => ({
          question_text: q.question_text,
          options: q.options,
          correct_answer: q.correct_answer,
          explanation: q.explanation || null,
          topic_tag: q.topic_tag || null,
          points: q.points ?? 5
        }))

      const payload = {
        course_id: courseId,
        title: title.value,
        exam_type: examType.value,
        academic_year: academicYear.value,
        question_data: questionData
      }

      if (!templateId.value) {

        const created = await examService.createExamTemplate(payload)

        templateId.value = created.id

      } else {

        await examService.updateExamTemplate(templateId.value, payload)

      }

      lastSaved.value = new Date()

    } catch (e) {

      error.value = e?.response?.data?.detail ?? 'Save failed'

    } finally {

      isSaving.value = false

    }
  }

  /* ================================
      Return
  ================================= */

  return {

    // metadata
    templateId,
    title,
    examType,
    academicYear,

    // questions
    localQuestions,

    // state
    isSaving,
    isLoading,
    error,
    lastSaved,

    // computed
    totalQuestions,
    totalPoints,
    incompleteCount,

    // actions
    load,
    addEmptyQuestion,
    updateLocalQuestion,
    updateOption,
    removeLocalQuestion,
    save
  }
}