<template>

  <div class="designer-page">
    
    <!-- ================= PAGE CARD HEADER ================= -->
    <div class="page-card">
      <div class="header">
        <div class="header-left">
          <button class="back-btn" @click="$router.back()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
          </button>
          <div class="header-text">
            <p class="breadcrumb">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
              Course #{{ courseId }}
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 18l6-6-6-6"/></svg>
              Exam Editor
            </p>
            <h1 class="page-title">{{ templateId ? 'Edit Exam' : 'New Exam' }}</h1>
            <p class="page-subtitle">
              <span class="status-dot" :class="{ 'is-published': isPublished }">
                {{ isPublished ? 'Published' : 'Draft' }} · Last saved {{ lastSavedText || 'never' }}
              </span>
            </p>
          </div>
        </div>

        <div class="header-actions">
          <button v-if="templateId" class="btn-header-danger" @click="showDeleteConfirm = true" :disabled="isDeleting">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/></svg>
            Delete
          </button>
          <button class="btn-header-ghost" @click="showPreview = true">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            Preview
          </button>
          <button class="btn-header-ghost" @click="togglePublish">
            <svg v-if="!isPublished" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18M6 6l12 12"/></svg>
            {{ isPublished ? 'Unpublish' : 'Publish' }}
          </button>
          <button class="btn-header-save" :disabled="isSaving" @click="save">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
            {{ isSaving ? 'Saving…' : 'Save' }}
          </button>
          <div v-if="error" class="toast toast-error">
            ERROR: {{ error }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="showDeleteConfirm" class="modal-overlay">
      <div class="modal">
        <h3>Confirm Delete</h3>
        <p>Are you sure you want to delete the exam <strong>{{ title }}</strong>?</p>
        <p>This action cannot be undone.</p>

        <div class="modal-actions">
          <button
            class="btn btn-outline"
            @click="showDeleteConfirm = false"
            :disabled="isDeleting"
          >
            Cancel
          </button>
          <button
            @click="deleteExam"
            :disabled="isDeleting"
            class="btn-danger"
          >
            {{ isDeleting ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>


    <!-- ================= CONTENT AREA ================= -->
    <div class="content-area">

      <!-- ================= EXAM SETTINGS ================= -->
      <section class="settings-card">

        <div class="settings-header">
          <div class="settings-header-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          </div>
          <h2>Exam Settings</h2>
        </div>

        <!-- Title -->
        <div class="settings-field-full">
          <label class="field-label">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M4 6h16M4 12h10M4 18h6"/></svg>
            Exam Title
          </label>
          <input v-model="title" class="field-input" placeholder="e.g. Microeconomics Midterm"/>
        </div>

        <!-- Description -->
        <div class="settings-field-full">
          <label class="field-label">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Description
          </label>
          <textarea v-model="description" class="field-input field-textarea" rows="2" placeholder="Brief description…"/>
        </div>

        <!-- Type / Year / Term -->
        <div class="settings-row-3">
          <div class="settings-field">
            <label class="field-label">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
              Exam Type
            </label>
            <select v-model="examType" class="field-input field-select">
              <option value="midterm">Midterm</option>
              <option value="final">Final</option>
              <option value="summer">Summer</option>
              <option value="quiz">Quiz</option>
            </select>
          </div>
          <div class="settings-field">
            <label class="field-label">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v20M2 12h20"/></svg>
              Academic Year
            </label>
            <input v-model="academicYear" class="field-input" placeholder="e.g. 2024"/>
          </div>
          <div class="settings-field">
            <label class="field-label">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
              Term
            </label>
            <select v-model="term" class="field-input field-select">
              <option value="1">Term 1</option>
              <option value="2">Term 2</option>
              <option value="summer">Summer</option>
            </select>
          </div>
        </div>

        <!-- Duration + Passing Score -->
        <div class="settings-row-2">
          <div class="settings-field-stat">
            <div class="stat-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            </div>
            <div class="stat-body">
              <label class="field-label">Duration</label>
              <div class="stat-input-row">
                <input v-model.number="durationMinutes" type="number" class="field-input stat-input" placeholder="60"/>
                <span class="stat-unit">min</span>
              </div>
            </div>
          </div>
          <div class="settings-field-stat">
            <div class="stat-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <div class="stat-body">
              <label class="field-label">Passing Score</label>
              <div class="stat-input-row">
                <input v-model.number="passingScore" type="number" class="field-input stat-input" placeholder="60"/>
                <span class="stat-unit">%</span>
              </div>
            </div>
          </div>
        </div>

      </section>


      <!-- ================= OPTIONS ================= -->
      <section class="settings-card">

        <div class="section-header">
          <h2>Exam Behaviour</h2>
        </div>

        <div class="toggle-grid">

          <label class="toggle-item">
            <div class="toggle-info">
              <span class="toggle-title">Randomise Questions</span>
              <span class="toggle-desc">Shuffle question order for each student</span>
            </div>
            <div class="toggle-wrap">
              <input type="checkbox" v-model="randomiseQuestions" class="toggle-input"/>
              <span class="toggle-slider"></span>
            </div>
          </label>

          <label class="toggle-item">
            <div class="toggle-info">
              <span class="toggle-title">Randomise Options</span>
              <span class="toggle-desc">Shuffle answer choices within each question</span>
            </div>
            <div class="toggle-wrap">
              <input type="checkbox" v-model="randomiseOptions" class="toggle-input"/>
              <span class="toggle-slider"></span>
            </div>
          </label>

          <label class="toggle-item">
            <div class="toggle-info">
              <span class="toggle-title">Show Correct Answer After Exam</span>
              <span class="toggle-desc">Students see correct answers upon completion</span>
            </div>
            <div class="toggle-wrap">
              <input type="checkbox" v-model="showCorrectAfter" class="toggle-input"/>
              <span class="toggle-slider"></span>
            </div>
          </label>

          <label class="toggle-item">
            <div class="toggle-info">
              <span class="toggle-title">Allow Student Review</span>
              <span class="toggle-desc">Students can revisit completed exam</span>
            </div>
            <div class="toggle-wrap">
              <input type="checkbox" v-model="allowReview" class="toggle-input"/>
              <span class="toggle-slider"></span>
            </div>
          </label>

        </div>

      </section>


      <!-- ================= QUESTIONS ================= -->
      <section class="questions-card">

        <div class="questions-header">
          <div class="settings-header-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
          </div>
          <h2>Questions</h2>
          <div class="questions-stats">
            <span class="q-stat q-stat-yellow">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              {{ totalPoints }} pt
            </span>
            <span class="q-stat q-stat-pink">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              {{ localQuestions.length }} Q
            </span>
          </div>
        </div>

        <div class="questions-list">
          <div v-if="localQuestions.length === 0" class="questions-empty">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
            <p>No questions yet</p>
            <span>Click below to add your first question</span>
          </div>
          <QuestionEditor
            v-for="(q, qi) in localQuestions"
            :key="q._lid"
            :q="q"
            :index="qi"
            :lesson-options="lessonOptions"
            @remove="removeLocalQuestion"
          />
          <p v-if="lessonOptionsError" class="text-muted">{{ lessonOptionsError }}</p>
        </div>

        <button class="btn-add-question" @click="addEmptyQuestion">
          <span class="btn-add-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
          </span>
          Add Question
        </button>

      </section>

    </div>


    <!-- ================= PREVIEW ================= -->
    <div v-if="showPreview" class="modal-overlay">

      <div class="modal">

        <div class="modal-header">
          <div>
            <h2>{{ title || 'Untitled Exam' }}</h2>
            <p class="text-muted text-sm mt-1">{{ description }}</p>
          </div>
          <button class="btn-close" @click="showPreview=false">✕</button>
        </div>

        <div class="modal-body">

          <div
            v-for="(q,i) in localQuestions"
            :key="q._lid"
            class="preview-question"
          >

            <p class="preview-q-label">
              Question {{ i+1 }}
              <span class="badge badge-yellow">{{ q.points || 1 }} pt</span>
            </p>

            <p class="font-semibold mb-2" v-html="q.text || '<em>(No question text yet)</em>'"></p>
            <img v-for="(url, imageIndex) in q.image_urls || []" :key="imageIndex" :src="url"
              alt="Question image" style="display:block;max-width:100%;max-height:420px;object-fit:contain;margin:12px 0" />

            <template v-if="q.type === 'multiple_choice'">
              <ul class="preview-options">
                <li v-for="(o,oi) in q.options" :key="oi" class="preview-option">
                  <span class="option-letter">{{ ['A','B','C','D'][oi] || oi + 1 }}</span>
                  {{ o || '(No option text yet)' }}
                </li>
              </ul>
            </template>

            <template v-else-if="q.type === 'true_false'">
              <ul class="preview-options">
                <li class="preview-option"><span class="option-letter">T</span> True </li>
                <li class="preview-option"><span class="option-letter">F</span> False </li>
              </ul>
            </template>

            <template v-else>
               <div style="margin-top: 12px; border-bottom: 2px dashed #cbd5e1; height: 30px; width: 100%;"></div>
            </template>

          </div>

        </div>

        <div class="modal-footer">
          <button
            class="btn btn-primary"
            @click="showPreview=false"
          >
            Close Preview
          </button>
        </div>

      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useExamStore } from '@/store/examStore'
import QuestionEditor from '@/components/QuestionEditor.vue'
import learningService from '@/services/learningService'

const router = useRouter()
const route = useRoute()
const examStore = useExamStore()

const courseId = Number(route.params.courseId)
const templateId = route.params.templateId
  ? Number(route.params.templateId)
  : null

const title = ref('')
const description = ref('')
const examType = ref('midterm')
const academicYear = ref('')
const term = ref('1')
const durationMinutes = ref(60)
const passingScore = ref(50)

const randomiseQuestions = ref(false)
const randomiseOptions = ref(false)
const showCorrectAfter = ref(false)
const allowReview = ref(false)
const isPublished = ref(false)

function togglePublish() {
  isPublished.value = !isPublished.value
}


const localQuestions = ref([])
const lessonOptions = ref([])
const lessonOptionsError = ref('')

async function loadLessonOptions() {
  try {
    const res = await learningService.listLessonOptions(courseId)
    lessonOptions.value = res.data ?? []
    lessonOptionsError.value = ''
  } catch (err) {
    lessonOptionsError.value = 'Could not load published lessons for this course.'
  }
}

const totalPoints = computed(() => {
  return localQuestions.value.reduce((sum, q) => sum + (q.points ?? 0), 0)
})

/**
 * Creates a blank ExamQuestion-shaped object for the editor.
**/

function newQuestion() {
  return {
    _lid: Date.now() + Math.random(), // UI-only stable key
    id: '',
    type: 'multiple_choice',
    text: '',
    image_urls: [],
    _html: '',                        // UI-only rich HTML for RTE
    options: ['', '', '', ''],        // List[str]
    correct_answer: '',               // str (matches first option after user types)
    explanation: '',
    points: 1,
    topic_tag: '',
    order_index: 0,                    // filled in buildPayload
    linked_learning_page_id: null,
  }
}

function addEmptyQuestion() {
  localQuestions.value.push(newQuestion())
}

function removeLocalQuestion(lid) {
  localQuestions.value = localQuestions.value.filter(q => q._lid !== lid)
}


const showPreview = ref(false)
const isSaving = ref(false)
const error = ref(null)
const lastSaved = ref(null)

const lastSavedText = computed(() => {
  if (!lastSaved.value) return null
  return new Date(lastSaved.value).toLocaleTimeString()
})


function buildPayload() {

  return {
    course_id: courseId || null,

    title: title.value,
    description: description.value || null,

    exam_type: examType.value,
    academic_year: academicYear.value || null,
    term: term.value || null,
    
    question_data: localQuestions.value.map((q, i) => ({
      id: `q${i+1}`,
      type: q.type,
      text: q.text,
      image_urls: q.image_urls || [],
      options: q.options ?? null,
      correct_answer: q.correct_answer,
      explanation: (q.explanation || '').trim(),
      points: q.points,
      topic_tag: q.topic_tag || null,
      order_index: i,
      linked_learning_page_id: q.linked_learning_page_id
        ? Number(q.linked_learning_page_id)
        : null,
    })),

    time_limit_minutes: durationMinutes.value,
    passing_score_pct: passingScore.value,

    randomise_questions: randomiseQuestions.value,
    randomise_options: randomiseOptions.value,
    show_correct_after: showCorrectAfter.value,
    allow_review: allowReview.value,
    is_published: isPublished.value,
  }
}

/**
 * Questions missing a teacher-written explanation, as 1-based positions.
 * The backend rejects these too — this just catches them before the request.
**/
function questionsMissingExplanation() {
  return localQuestions.value
    .map((q, i) => ((q.explanation || '').trim() ? null : i + 1))
    .filter(n => n !== null)
}

async function save() {

  isSaving.value = true
  error.value = null

  try {
    if (localQuestions.value.some(q => q._pendingUploads)) {
      throw new Error('Wait for question images to finish uploading before saving.')
    }

    const missing = questionsMissingExplanation()
    if (missing.length) {
      throw new Error(
        `Write an explanation for question ${missing.join(', ')} before saving. ` +
        'Every question needs your own explanation of the correct answer.'
      )
    }

    const payload = buildPayload()

    let res

    if (templateId) {
      res = await examStore.updateTemplate(templateId, payload)
    } else {
      res = await examStore.createTemplate(payload)
    }

    if (!res) {
      throw new Error(examStore.error || 'Save failed')
    }

    lastSaved.value = Date.now()

  } catch (err) {
    error.value = err.message
  } finally {
    isSaving.value = false
  }
}

async function loadTemplate() {

  if (!templateId) return

  await examStore.fetchTemplate(templateId)

  const t = examStore.currentTemplate
  if (!t) return

  // Basic info
  title.value = t.title || ''
  description.value = t.description || ''
  examType.value = t.exam_type || 'midterm'
  academicYear.value = t.academic_year || ''
  term.value = t.term || '1'
  passingScore.value = t.passing_score_pct ?? 50
  durationMinutes.value = t.time_limit_minutes ?? 60

  // Behaviour
  randomiseQuestions.value = t.randomise_questions ?? false
  randomiseOptions.value = t.randomise_options ?? false
  showCorrectAfter.value = t.show_correct_after ?? false
  allowReview.value = t.allow_review ?? false

  const qd = t.question_data || []

  localQuestions.value = (t.question_data || []).map(q => ({
    _lid: Date.now() + Math.random(),
    id: q.id,
    type: q.type || 'multiple_choice',
    text: q.text || '',
    image_urls: q.image_urls || [],
    _html: q.text || '',                // plain text as initial HTML
    options: q.options ?? [],
    correct_answer: q.correct_answer ?? '',
    explanation: q.explanation || '',
    points: q.points ?? 1,
    topic_tag: q.topic_tag || '',
    order_index: q.order_index ?? 0,
    linked_learning_page_id: q.linked_learning_page_id ?? null,
  }))
}

const isDeleting = ref(false)
const showDeleteConfirm = ref(false)

async function deleteExam() {
  if (!templateId) return

  isDeleting.value = true
  error.value = null

  try {
    const res = await examStore.deleteTemplate(templateId)
    if (!res) throw new Error(examStore.error || 'Delete failed')
    router.push({ name: 'TeacherExamDashboard', params: { courseId } })

  } catch (err) {
    error.value = err.message
  } finally {
    isDeleting.value = false
    showDeleteConfirm.value = false
  }
}

onMounted(() => {
  loadLessonOptions()

  if (templateId) {
    loadTemplate()
  }

  if (!templateId && localQuestions.value.length === 0) {
    addEmptyQuestion()
  }

})
</script>

<style scoped>
/* Page & layout */
.designer-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 2rem;
  max-width: 1100px;
  margin: 0 auto;
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
  border: 1.5px solid rgba(255,255,255,0.4);
  background: rgba(255,255,255,0.15);
  color: var(--white);
  cursor: pointer;
  transition: all 0.18s ease;
  flex-shrink: 0;
  backdrop-filter: blur(4px);
}

.back-btn:hover {
  background: rgba(255,255,255,0.28);
  border-color: rgba(255,255,255,0.7);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  color: rgba(255,255,255,0.75);
  font-weight: 500;
}

.breadcrumb svg { flex-shrink: 0; opacity: 0.7; }

.page-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--white);
  line-height: 1.15;
  letter-spacing: -0.01em;
}

.page-subtitle {
  font-size: 0.8rem;
  color: rgba(255,255,255,0.78);
  margin: 0;
  display: flex;
  align-items: center;
}

.page-subtitle .status-dot {
  color: rgba(255,255,255,0.78);
  font-size: 0.78rem;
}

.page-subtitle .status-dot::before {
  background: rgba(255,255,255,0.5);
}

.page-subtitle .status-dot.is-published::before {
  background: var(--light-green);
  animation: none;
}

/* Header action buttons (right side) */
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  z-index: 1;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.btn-header-ghost {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: rgba(255,255,255,0.18);
  border: 1.5px solid rgba(255,255,255,0.45);
  border-radius: var(--radius-md);
  color: var(--white);
  font-size: 0.82rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.18s ease;
  backdrop-filter: blur(4px);
}

.btn-header-ghost:hover {
  background: rgba(255,255,255,0.30);
  border-color: rgba(255,255,255,0.75);
}

.btn-header-save {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.1rem;
  background: var(--white);
  border: none;
  border-radius: var(--radius-md);
  color: var(--primary-pink);
  font-size: 0.82rem;
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.18s ease;
}

.btn-header-save:hover:not(:disabled) { filter: brightness(0.96); }
.btn-header-save:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-header-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  background: rgba(220,38,38,0.18);
  border: 1.5px solid rgba(255,150,150,0.5);
  border-radius: var(--radius-md);
  color: var(--white);
  font-size: 0.82rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.18s ease;
}

.btn-header-danger:hover:not(:disabled) {
  background: rgba(220,38,38,0.35);
  border-color: rgba(255,150,150,0.8);
}

.btn-header-danger:disabled { opacity: 0.4; cursor: not-allowed; }

/* Content area */
.content-area {
  max-width: 860px;
  margin: 0 auto;
  width: 100%;
  padding-bottom: 4rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Form grid */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem 1.5rem;
}

/* Settings card (Exam Settings section) */
.settings-card {
  background: var(--white);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.settings-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--gray-light);
}

.settings-header h2 {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
}

.settings-header-icon {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-md);
  background: var(--light-pink);
  color: var(--primary-pink);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Field label with icon */
.field-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.4rem;
}

.field-label svg { flex-shrink: 0; opacity: 0.7; }

/* Base input */
.field-input {
  width: 100%;
  padding: 0.6rem 0.875rem;
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  background: var(--gray-light);
  font-size: 0.875rem;
  font-family: inherit;
  color: var(--text-main);
  outline: none;
  transition: all 0.18s ease;
}

.field-input:focus {
  border-color: var(--primary-pink);
  background: var(--white);
  box-shadow: 0 0 0 3px rgba(237, 64, 129, 0.08);
}

.field-textarea {
  resize: none;
  line-height: 1.5;
}

.field-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  padding-right: 2rem;
  cursor: pointer;
}

/* Full-width field row */
.settings-field-full { display: flex; flex-direction: column; }

/* 3-col row */
.settings-row-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.75rem;
}

.settings-field { display: flex; flex-direction: column; }

/* 2-col stat row */
.settings-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.settings-field-stat {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.875rem 1rem;
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  background: var(--gray-light);
  transition: border-color 0.18s ease;
}

.settings-field-stat:focus-within {
  border-color: var(--primary-pink);
  background: var(--white);
}

.stat-icon {
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  background: var(--white);
  border: 1.5px solid var(--card-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-pink);
  flex-shrink: 0;
}

.stat-body { flex: 1; display: flex; flex-direction: column; gap: 0.25rem; }

.stat-input-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.stat-input {
  padding: 0.25rem 0;
  background: transparent;
  border: none;
  border-bottom: 1.5px solid var(--card-border);
  border-radius: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
  width: 70px;
  box-shadow: none;
}

.stat-input:focus {
  border-color: var(--primary-pink);
  box-shadow: none;
  background: transparent;
}

.stat-unit {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

/* Toggle grid  */
.toggle-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

/* Select custom arrow  */
.select-field {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.9rem center;
  padding-right: 2.2rem;
  cursor: pointer;
}

/*  Question list & cards */
.questions-card {
  background: var(--white);
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.questions-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 2px solid var(--gray-light);
}

.questions-header h2 {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
  flex: 1;
}

.questions-stats {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.q-stat {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
}

.q-stat-yellow { background: var(--light-yellow); color: #92400e; }
.q-stat-pink   { background: var(--light-pink);   color: var(--primary-pink); }

.questions-list {
  display: flex;
  flex-direction: column;
  padding: 1.25rem 1.5rem;
  gap: 0.75rem;
}

/* Question number label inside each QuestionEditor */
.question-card {
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  background: var(--gray-light);
  transition: all 0.2s ease;
}

.question-card:hover {
  border-color: var(--primary-pink);
  background: var(--white);
  box-shadow: var(--shadow-sm);
}

.question-row-group {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.75rem 1rem;
}

/* Empty state */
.questions-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  padding: 2.5rem 1rem;
  color: var(--text-muted);
  text-align: center;
}

.questions-empty svg { opacity: 0.3; margin-bottom: 0.25rem; }
.questions-empty p   { font-weight: 600; font-size: 0.9rem; color: var(--text-muted); }
.questions-empty span { font-size: 0.78rem; }

/* Add Question button */
.btn-add-question {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.875rem;
  background: var(--gray-light);
  border: none;
  border-top: 2px dashed var(--card-border);
  border-radius: 0;
  font-size: 0.84rem;
  font-family: inherit;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.18s ease;
}

.btn-add-question:hover {
  background: var(--light-green);
  color: var(--forest-green);
  border-color: var(--forest-green);
}

.btn-add-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--white);
  border: 1.5px solid var(--card-border);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s ease;
  flex-shrink: 0;
}

.btn-add-question:hover .btn-add-icon {
  background: var(--forest-green);
  border-color: var(--forest-green);
  color: var(--white);
}

/* Remove button */
.btn-remove {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 0.9rem;
  padding: 3px 7px;
  border-radius: var(--radius-md);
  transition: all 0.15s ease;
  margin-left: auto;
  line-height: 1;
}

.btn-remove:hover {
  background: #fee2e2;
  color: #ef4444;
}

/* Answer options block */
.options-block {
  margin: 1rem 0;
  padding: 1rem;
  background: var(--white);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
}

.option-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.4rem 0.5rem;
  border-radius: var(--radius-md);
  margin-bottom: 0.4rem;
  transition: background 0.15s ease;
}

.option-row:hover { background: var(--light-green); }

.option-row.is-correct { background: var(--light-green); }
.option-row.is-correct .option-letter {
  background: var(--forest-green);
  color: var(--white);
}

.option-radio {
  width: 14px;
  height: 14px;
  accent-color: var(--forest-green);
  cursor: pointer;
}

.option-letter {
  width: 26px;
  height: 26px;
  border-radius: var(--radius-md);
  background: var(--gray-light);
  font-size: 0.78rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.option-input { flex: 1; }

/* Delete button */
.btn-danger {
  background: transparent;
  color: #dc2626;
  border: 1.5px solid #fca5a5;
  border-radius: var(--radius-md);
  padding: 0.55rem 1rem;
  font-size: 0.84rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-danger:hover:not(:disabled) {
  background: #fef2f2;
}

.btn-danger:disabled { opacity: 0.4; cursor: not-allowed; }

/* Warn button (Publish/Unpublish) */
.btn-warning {
  background: var(--primary-yellow);
  color: var(--text-main);
  border: none;
  border-radius: var(--radius-md);
  padding: 0.55rem 1rem;
  font-size: 0.84rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-warning:hover { filter: brightness(0.95); }

/* Delete confirm modal actions */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 2px solid var(--gray-light);
}

/* Preview modal body contents */
.preview-question {
  padding: 1rem;
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  background: var(--gray-light);
  margin-bottom: 1rem;
}

.preview-q-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--primary-pink);
  margin-bottom: 0.5rem;
}

.preview-options {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-top: 0.75rem;
}

.preview-option {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.88rem;
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--card-border);
  border-radius: var(--radius-md);
  background: var(--white);
}

/* Responsive */
@media (max-width: 768px) {
  .designer-page { padding: 1rem; }
  .form-grid,
  .toggle-grid,
  .question-row-group,
  .settings-row-3,
  .settings-row-2 { grid-template-columns: 1fr; }
  .header { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .header-actions { width: 100%; justify-content: flex-start; }
}
</style>
