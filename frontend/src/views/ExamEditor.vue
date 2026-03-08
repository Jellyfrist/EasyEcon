<template>

  <!--
    TODO: In CourseEditor replace button click with this line.
     <button class="btn btn-outline mt-2" @click.stop="router.push({ name: 'ExamEditor', params: { courseId: courseId } })">
  -->

  <div class="designer-page">
    
    <button class="btn btn-primary" @click="$router.back()">← Back</button>

    <!-- ================= TOP BAR ================= -->
    <div class="top-bar">

      <div class="top-bar-left">
        <h1 class="font-bold text-xl">Easy Econ Exam Designer</h1>

        <p class="status-dot" :class="{ 'is-published': isPublished }">
          {{ isPublished ? "Published" : "Draft mode" }} · Last saved {{ lastSavedText || 'never' }}
        </p>
      </div>

      <div class="top-bar-actions">

        <button class="btn btn-outline" @click="showPreview = true">
          Preview
        </button>

        <button
          class="btn btn-warning"
          @click="togglePublish"
        >
          {{ isPublished ? "Unpublish" : "Publish" }}
        </button>

        <button
          class="btn btn-primary"
          :disabled="isSaving"
          @click="save"
        >
          <span v-if="isSaving">Saving...</span>
          <span v-else>Save</span>
        </button>

        <div v-if="error" class="toast toast-error">⚠️ {{ error }}</div>

        <!-- Delete (Only on edit mode) -->
        <button
          v-if="templateId"
          @click="showDeleteConfirm = true"
          :disabled="isDeleting"
          class="btn-danger"
        >
          Delete Exam
        </button>

        <!-- Confirm Dialog -->

      </div>
    </div>

    <div v-if="showDeleteConfirm" class="modal-overlay">
      <div class="modal">
        <h3>Confirm Delete</h3>
        <p>Are you sure you want to delete the exam <strong>{{ title }}</strong>?</p>
        <p>This action cannot be undone.</p>

        <div class="modal-actions">
          <button
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
      <section class="card">

        <div class="section-header">
          <h2>Exam Settings</h2>
        </div>

        <div class="form-grid">

          <div class="form-group">
            <label>Exam Title</label>
            <input v-model="title" class="input-field" placeholder="e.g. Microeconomics Midterm"/>
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="description" class="input-field" rows="3" placeholder="Brief description..."/>
          </div>

          <div class="form-group">
            <label>Exam Type</label>
            <select v-model="examType" class="input-field select-field">
              <option value="midterm">Midterm</option>
              <option value="final">Final</option>
              <option value="summer">Summer</option>
              <option value="quiz">Quiz</option>
            </select>
          </div>

          <div class="form-group">
            <label>Academic Year</label>
            <input v-model="academicYear" class="input-field" placeholder="e.g. 2024"/>
          </div>

          <div class="form-group">
            <label>Term</label>
            <select v-model="term" class="input-field select-field">
              <option value="1">Term 1</option>
              <option value="2">Term 2</option>
              <option value="summer">Summer</option>
            </select>
          </div>

          <div class="form-group">
            <label>Duration (minutes)</label>
            <input v-model.number="durationMinutes" type="number" class="input-field" placeholder="60"/>
          </div>

          <div class="form-group">
            <label>Passing Score (%)</label>
            <input v-model.number="passingScore" type="number" class="input-field" placeholder="60"/>
          </div>

        </div>

      </section>


      <!-- ================= OPTIONS ================= -->
      <section class="card">

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
      <section class="card">

        <div class="section-header">
          <h2>Questions</h2>
          <span class="badge badge-yellow">
            {{ totalPoints }} point{{ totalPoints !== 1 ? 's' : '' }}
          </span>
          <span class="badge badge-pink">
            {{ localQuestions.length }} question{{ localQuestions.length !== 1 ? 's' : '' }}
          </span>
        </div>

        <div class="questions-list">
          <QuestionEditor
            v-for="(q, qi) in localQuestions"
            :key="q._lid"
            :q="q"
            :index="qi"
            @remove="removeLocalQuestion"
          />
        </div>

        <button class="btn btn-green w-full mt-3" @click="addEmptyQuestion">
          + Add Question
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

            <p class="font-semibold mb-2" v-html="q.text || '<em>(ยังไม่ได้พิมพ์คำถาม)</em>'"></p>

            <template v-if="q.type === 'multiple_choice'">
              <ul class="preview-options">
                <li v-for="(o,oi) in q.options" :key="oi" class="preview-option">
                  <span class="option-letter">{{ ['A','B','C','D'][oi] || oi + 1 }}</span>
                  {{ o || '(ยังไม่ได้พิมพ์ตัวเลือก)' }}
                </li>
              </ul>
            </template>

            <template v-else-if="q.type === 'true_false'">
              <ul class="preview-options">
                <li class="preview-option"><span class="option-letter">T</span> True (ถูก)</li>
                <li class="preview-option"><span class="option-letter">F</span> False (ผิด)</li>
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

const router = useRouter()
const route = useRoute()
const examStore = useExamStore()

/* =============================
   ROUTE
============================= */

const courseId = Number(route.params.courseId)
const templateId = route.params.templateId
  ? Number(route.params.templateId)
  : null


/* =============================
   EXAM SETTINGS
============================= */

const title = ref('')
const description = ref('')
const examType = ref('midterm')
const academicYear = ref('')
const term = ref('1')
const durationMinutes = ref(60)
const passingScore = ref(50)


/* =============================
   BEHAVIOUR
============================= */

const randomiseQuestions = ref(false)
const randomiseOptions = ref(false)
const showCorrectAfter = ref(false)
const allowReview = ref(false)
const isPublished = ref(false)

function togglePublish() {
  isPublished.value = !isPublished.value
}


/* =============================
   QUESTIONS
============================= */

const localQuestions = ref([])

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


/* =============================
   UI STATE
============================= */

const showPreview = ref(false)
const isSaving = ref(false)
const error = ref(null)
const lastSaved = ref(null)

const lastSavedText = computed(() => {
  if (!lastSaved.value) return null
  return new Date(lastSaved.value).toLocaleTimeString()
})


/* =============================
   PAYLOAD BUILDER
============================= */

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
      options: q.options ?? null,
      correct_answer: q.correct_answer,
      explanation: q.explanation || null,
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


/* =============================
   SAVE
============================= */

async function save() {

  isSaving.value = true
  error.value = null

  try {

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

/* =============================
   LOAD TEMPLATE (EDIT MODE)
============================= */

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

/* =============================
   DELETE
============================= */

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


/* =============================
   INIT
============================= */

onMounted(() => {

  if (templateId) {
    loadTemplate()
  }

  if (!templateId && localQuestions.value.length === 0) {
    addEmptyQuestion()
  }

})
</script>

<style scoped>
/* ─────────────────────────────────────────────────────
   Page & layout
───────────────────────────────────────────────────── */
.designer-page {
  min-height: 100vh;
}

.content-area {
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 2rem 4rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ─────────────────────────────────────────────────────
   Form grid  (specific to this page)
───────────────────────────────────────────────────── */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem 1.5rem;
}

/* ─────────────────────────────────────────────────────
   Toggle grid  (2-col layout for toggle-item)
───────────────────────────────────────────────────── */
.toggle-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

/* ─────────────────────────────────────────────────────
   Select custom arrow
───────────────────────────────────────────────────── */
.select-field {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.9rem center;
  padding-right: 2.2rem;
  cursor: pointer;
}

/* ─────────────────────────────────────────────────────
   Question list & cards
───────────────────────────────────────────────────── */
.questions-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.question-card {
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  background: #fafbfd;
  transition: all 0.2s ease;
}

.question-card:hover {
  border-color: #d8dbe6;
  background: white;
  box-shadow: var(--shadow-sm);
}

.question-row-group {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.75rem 1rem;
}

/* ─────────────────────────────────────────────────────
   Remove button
───────────────────────────────────────────────────── */
.btn-remove {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 0.9rem;
  padding: 3px 7px;
  border-radius: 8px;
  transition: all 0.15s;
  margin-left: auto;
  line-height: 1;
}

.btn-remove:hover {
  background: #fee2e2;
  color: #ef4444;
}

/* ─────────────────────────────────────────────────────
   Answer options block
───────────────────────────────────────────────────── */
.options-block {
  margin: 1rem 0;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
}

.option-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.4rem 0.5rem;
  border-radius: 10px;
  margin-bottom: 0.4rem;
  transition: background 0.15s;
}

.option-row:hover { background: #f0faf5; }

.option-row.is-correct { background: rgba(10, 112, 60, 0.06); }
.option-row.is-correct .option-letter {
  background: var(--forest-green);
  color: white;
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
  border-radius: 8px;
  background: var(--gray-light);
  font-size: 0.78rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  flex-shrink: 0;
  transition: all 0.15s;
}

.option-input { flex: 1; }

/* ─────────────────────────────────────────────────────
   Preview modal body contents
───────────────────────────────────────────────────── */
.preview-question {
  padding: 1rem;
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  background: #fafbfd;
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
  border-radius: 8px;
  background: white;
}

/* ─────────────────────────────────────────────────────
   Responsive
───────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .content-area { padding: 1rem 1rem 3rem; }
  .form-grid,
  .toggle-grid,
  .question-row-group { grid-template-columns: 1fr; }
  .top-bar { flex-direction: column; align-items: stretch; gap: 0.75rem; position: relative; }
  .top-bar-actions { flex-wrap: wrap; }
}
</style>