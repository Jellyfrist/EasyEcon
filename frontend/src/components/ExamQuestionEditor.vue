<template>
  <div
    class="card question-card"
    :class="isIncomplete ? 'state-warning' : 'state-ready'"
  >

    <!-- ===== HEADER ===== -->
    <div class="question-header">

      <div class="question-left">
        <span class="question-index">
          Question {{ index + 1 }}
        </span>
      </div>

      <div class="question-right">

        <div class="points-wrapper">
          <label>Points</label>
          <input
            class="input-field points-input"
            :value="question.points"
            type="number"
            min="1"
            @input="$emit('update-question', question._lid, 'points', Number($event.target.value))"
          />
        </div>

        <span
          class="status-badge"
          :class="isIncomplete ? 'badge-warning' : 'badge-success'"
        >
          {{ isIncomplete ? 'Incomplete' : 'Ready' }}
        </span>

      </div>

    </div>


    <!-- ===== QUESTION TYPE ===== -->
    <div class="form-group">
      <label>Question Type</label>

      <select
        class="input-field"
        v-model="question.type"
        @change="updateQuestionType"
      >
        <option value="mcq">Multiple Choice</option>
        <option value="truefalse">True / False</option>
        <option value="short">Short Answer</option>
      </select>
    </div>


    <!-- ===== EDITOR ===== -->
    <div class="editor-wrapper">

      <div class="editor-toolbar">
        <button type="button" @click="format('bold')"><b>B</b></button>
        <button type="button" @click="format('italic')"><i>I</i></button>

        <button type="button" @click="insertMath('a+b')">∑</button>
        <button type="button" @click="insertMath('\\sqrt{x}')">√</button>
        <button type="button" @click="insertMath('\\frac{a}{b}')">a/b</button>
        <button type="button" @click="insertMath('\\int_a^b f(x)dx')">∫</button>

        <button type="button" @click="triggerImageUpload">🖼</button>

        <input
          ref="imageInput"
          type="file"
          accept="image/*"
          class="hidden-input"
          @change="insertImage"
        />
      </div>

      <div
        ref="editor"
        class="editor-content"
        contenteditable="true"
        :innerHTML="question.question_text"
        @input="handleInput"
      ></div>

    </div>


    <!-- ===== DYNAMIC QUESTION COMPONENT ===== -->

    <component
      :is="questionComponent"
      :key="question.type"
      :question="question"
      @update-option="$emit('update-option', question._lid, ...arguments)"
      @update-question="$emit('update-question', question._lid, ...arguments)"
    />


    <!-- ===== META ===== -->
    <div class="meta-section grid-2">

      <div class="form-group">
        <label>Topic Tag</label>
        <input
          class="input-field"
          :value="question.topic_tag"
          type="text"
          placeholder="e.g. Elasticity"
          @input="$emit('update-question', question._lid, 'topic_tag', $event.target.value)"
        />
      </div>

      <div class="form-group">
        <label>Explanation</label>
        <input
          class="input-field"
          :value="question.explanation"
          type="text"
          placeholder="Shown after submission"
          @input="$emit('update-question', question._lid, 'explanation', $event.target.value)"
        />
      </div>

    </div>


    <!-- ===== FOOTER ===== -->
    <div class="question-footer">
      <button
        class="btn btn-outline btn-remove"
        @click="removeQuestion"
      >
        Remove Question
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

import MultipleChoice from '@/components/exam/MultipleChoice.vue'
import TrueFalse from '@/components/exam/TrueFalse.vue'
import ShortAnswer from '@/components/exam/ShortAnswer.vue'

// import katex from 'katex'
// import 'katex/dist/katex.min.css'

const props = defineProps({
  question: Object,
  index: Number
})

const emit = defineEmits([
  'update-question',
  'update-option',
  'remove'
])

const editor = ref(null)
const imageInput = ref(null)

/* =========================
   QUESTION TYPE MAP
========================= */

const updateQuestionType = (event) => {
  const newType = event.target.value;
  emit('update-question', question._lid, 'type', newType);
}

const components = {
  mcq: MultipleChoice,
  truefalse: TrueFalse,
  short: ShortAnswer
}

const questionComponent = computed(() =>
  components[props.question.type] || MultipleChoice
)

/* =========================
   TEXT EDITOR
========================= */

const handleInput = () => {

  renderMath()

  emit(
    'update-question',
    props.question._lid,
    'question_text',
    editor.value.innerHTML
  )
}

function format(command, value = null) {
  document.execCommand(command, false, value)
}

const triggerImageUpload = () => {
  imageInput.value.click()
}

const removeQuestion = () => {
  emit('remove', props.question._lid);
}

const insertImage = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()

  reader.onload = (e) => {
    document.execCommand('insertImage', false, e.target.result)
  }

  reader.readAsDataURL(file)
}

function renderMath() {
  if (!editor.value) return

  const elements = editor.value.querySelectorAll('.math')

  elements.forEach(el => {
    const latex = el.dataset.latex

    katex.render(latex, el, {
      throwOnError: false
    })
  })
}

function insertMath(latex) {

  const html = `
    <span
      class="math"
      data-latex="${latex}"
      contenteditable="false"
    >
      ${latex}
    </span>
  `

  document.execCommand("insertHTML", false, html)

  setTimeout(renderMath)
}

watch(
  () => props.question.question_text,
  (val) => {
    if (editor.value && editor.value.innerHTML !== val) {
      editor.value.innerHTML = val
    }
  }
)

/* =========================
   STATE
========================= */

const isIncomplete = computed(() =>
  !props.question.question_text?.trim() ||
  !props.question.correct_answer
)
</script>


<style scoped>
/* =========================================================
   Question Card Styling
========================================================= */
.question-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* HEADER */

.question-header{
  display:flex;
  justify-content:space-between;
  align-items:center;
}

.question-index{
  font-weight:700;
  font-size:1.1rem;
}

.question-right{
  display:flex;
  align-items:center;
  gap:1rem;
}

.points-wrapper{
  display:flex;
  align-items:center;
  gap:.5rem;
}

.points-input{
  width:80px;
}

/* BADGE */

.status-badge{
  padding:4px 10px;
  border-radius:999px;
  font-size:.8rem;
  font-weight:600;
}

.badge-warning{
  background:var(--light-yellow);
  color:#a16207;
}

.badge-success{
  background:var(--light-green);
  color:#065f46;
}

/* EDITOR */

.editor-wrapper{
  border:1px solid var(--card-border);
  border-radius:var(--radius-md);
  overflow:hidden;
}

.editor-toolbar {
  display: flex;
  gap: 6px;
  padding: 6px;
  border-bottom: 1px solid #ddd;
}

.editor-toolbar button {
  border: none;
  background: #f3f4f6;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.15s ease;
}

.editor-toolbar button:hover {
  background: #e5e7eb;
}

/* ACTIVE STATE */
.editor-toolbar button.active {
  background: var(--primary-pink);
  color: white;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
.editor-content{
  min-height:120px;
  padding:1rem;
  outline:none;
}

.math {
  padding: 2px 4px;
  background: #f8fafc;
  border-radius: 4px;
  display: inline-block;
}

/* OPTIONS */

.options-section{
  display:flex;
  flex-direction:column;
  gap:.7rem;
}

.option-row{
  display:grid;
  grid-template-columns:30px 30px 1fr;
  align-items:center;
  gap:.6rem;
}

.option-key{
  font-weight:700;
}

.hint-text{
  font-size:.8rem;
  color:var(--text-muted);
}

/* META */

.meta-section{
  gap:1rem;
}

/* FOOTER */

.question-footer{
  display:flex;
  justify-content:flex-end;
}

.btn-remove{
  color:#dc2626;
  border-color:#fecaca;
}
</style>
