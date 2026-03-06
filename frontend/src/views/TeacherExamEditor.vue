<template>
  <div class="designer-page">
    

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
          <span class="badge badge-pink">{{ localQuestions.length }} question{{ localQuestions.length !== 1 ? 's' : '' }}</span>
        </div>

        <div class="questions-list">

          <div
            v-for="(q, qi) in localQuestions"
            :key="q._lid"
            class="question-card"
          >

            <div class="flex items-center gap-2 mb-2">
              <span class="badge badge-pink">Q{{ qi + 1 }}</span>
              <span v-if="q.points" class="badge badge-yellow">{{ q.points }} pt{{ q.points !== 1 ? 's' : '' }}</span>
              <span v-if="q.topic_tag" class="badge badge-green">{{ q.topic_tag }}</span>
              <button
                class="btn-remove"
                @click="removeLocalQuestion(q._lid)"
              >✕</button>
            </div>

            <div class="form-group">
              <label>Question Text</label>
              <textarea
                v-model="q.question_text"
                class="input-field"
                rows="3"
                placeholder="Enter your question here..."
              />
            </div>

            <div class="question-row-group">

              <div class="form-group">
                <label>Points</label>
                <input
                  type="number"
                  v-model.number="q.points"
                  class="input-field"
                  placeholder="1"
                />
              </div>

              <div class="form-group">
                <label>Topic Tag</label>
                <input v-model="q.topic_tag" class="input-field" placeholder="e.g. Supply & Demand"/>
              </div>

              <div class="form-group">
                <label>Linked Learning Page ID</label>
                <input
                  type="number"
                  v-model.number="q.linked_learning_page_id"
                  class="input-field"
                  placeholder="Optional page id"
                />
              </div>

            </div>


            <!-- OPTIONS -->
            <div class="options-block">

              <div class="flex justify-between items-center mb-2">
                <h4 class="text-sm font-semibold text-muted">OPTIONS</h4>
                <span class="text-xs text-muted">Select the correct answer</span>
              </div>

              <div
                v-for="(opt, oi) in q.options"
                :key="oi"
                class="option-row"
                :class="{ 'is-correct': q.correct_answer === oi }"
              >

                <label class="flex items-center gap-2">
                  <input
                    type="radio"
                    :name="'correct'+qi"
                    :value="oi"
                    v-model="q.correct_answer"
                    class="option-radio"
                  />
                  <span class="option-letter">{{ ['A','B','C','D'][oi] || oi + 1 }}</span>
                </label>

                <input
                  v-model="opt.text"
                  placeholder="Option text"
                  class="input-field option-input"
                />

              </div>

            </div>


            <div class="form-group">
              <label>Explanation <span class="text-xs text-muted">(shown after exam if enabled)</span></label>
              <textarea v-model="q.explanation" class="input-field" rows="2" placeholder="Explain the correct answer..."/>
            </div>

          </div>

        </div>

        <button
          class="btn btn-green w-full mt-3"
          @click="addEmptyQuestion"
        >
          +
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

            <p class="font-semibold mb-2">{{ q.question_text }}</p>

            <ul class="preview-options">
              <li v-for="(o,oi) in q.options" :key="oi" class="preview-option">
                <span class="option-letter">{{ ['A','B','C','D'][oi] || oi + 1 }}</span>
                {{ o.text }}
              </li>
            </ul>

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
import { useRoute } from 'vue-router'
import { useExamStore } from '@/store/examStore'
// import { examService } from '@/services/examService.js'
/* TODO: update services/examService.js and apply into this script */


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


/* =============================
   QUESTIONS
============================= */

const localQuestions = ref([])

function newQuestion() {
  return {
    _lid: Date.now() + Math.random(),
    type: "multiple_choice",
    text: '',
    options: [
      { text: '' },
      { text: '' },
      { text: '' },
      { text: '' }
    ],
    correct_answer: 0,
    explanation: '',
    points: 1,
    topic_tag: '',
    linked_learning_page_id: ''
  }
}

function addEmptyQuestion() {
  localQuestions.value.push(newQuestion())
}

function removeLocalQuestion(lid) {
  localQuestions.value = localQuestions.value.filter(q => q._lid !== lid)
}

function togglePublish() {
  isPublished.value = !isPublished.value
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
    module_id: courseId || null,

    title: title.value,
    description: description.value || null,

    exam_type: examType.value,
    academic_year: academicYear.value || null,
    term: term.value || null,
    
    question_data: localQuestions.value.map((q, i) => ({
      id: `q${i+1}`,
      type: "multiple_choice",
      text: q.text,
      options: q.options.map(o => o.text),
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

  /* =============================
     BASIC INFO
  ============================= */

  title.value = t.title || ''
  description.value = t.description || ''
  examType.value = t.exam_type || 'midterm'
  academicYear.value = t.academic_year || ''
  term.value = t.term || '1'

  passingScore.value = t.passing_score_pct ?? 50
  durationMinutes.value = t.time_limit_minutes ?? 60


  /* =============================
     BEHAVIOUR (root level)
  ============================= */

  randomiseQuestions.value = t.randomise_questions ?? false
  randomiseOptions.value = t.randomise_options ?? false
  showCorrectAfter.value = t.show_correct_after ?? false
  allowReview.value = t.allow_review ?? false


  /* =============================
     QUESTIONS
  ============================= */

  const qd = t.question_data || []

  localQuestions.value = qd.map(q => ({
    _lid: Date.now() + Math.random(),

    text: q.text || '',
    points: q.points ?? 1,
    topic_tag: q.topic_tag || '',
    linked_learning_page_id: q.linked_learning_page_id ?? null,
    correct_answer: q.correct_answer ?? 0,
    explanation: q.explanation || '',

    options: (q.options || []).map(o => ({
      text: o
    }))
  }))
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