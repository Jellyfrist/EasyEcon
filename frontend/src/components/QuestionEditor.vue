<template>
  <div class="question-card">

    <div class="qe-header">

      <span class="badge badge-pink">Q{{ index + 1 }}</span>
      <span v-if="q.points" class="badge badge-yellow">
        {{ q.points }} pt{{ q.points !== 1 ? 's' : '' }}
      </span>
      <span v-if="q.topic_tag" class="badge badge-green">{{ q.topic_tag }}</span>

      <!-- Type selector -->
      <select
        v-model="q.type"
        class="input-field select-field type-select"
        @change="onTypeChange"
      >
        <option value="multiple_choice">Multiple Choice</option>
        <option value="true_false">True / False</option>
        <option value="short_answer">Short Answer</option>
      </select>

      <button class="btn-close ml-auto" @click="$emit('remove', q._lid)">✕</button>
    </div>

    <!-- Rich-text: q.text -->
    <div class="form-group">
      <label>Question Text</label>

      <div class="rte-toolbar">
        <button type="button" class="rte-btn" title="Bold"      @click="execCmd('bold')">
          <strong>B</strong>
        </button>
        <button type="button" class="rte-btn" title="Italic"    @click="execCmd('italic')">
          <em>I</em>
        </button>
        <button type="button" class="rte-btn" title="Underline" @click="execCmd('underline')">
          <u>U</u>
        </button>

        <div class="rte-divider"></div>

        <button type="button" class="rte-btn" title="Math formula" @click="openMath">
          <span class="math-icon">∑</span>
        </button>

        <label class="rte-btn img-btn" title="Insert image">
          🖼 <input type="file" accept="image/*" class="hidden-file" @change="insertImage" />
        </label>
      </div>

      <div
        ref="editor"
        class="rte-editor input-field"
        contenteditable="true"
        data-placeholder="Enter your question here…"
        @input="onEditorInput"
        @blur="syncText"
      ></div>
      
      <!-- Math modal -->
      <div v-if="showMathModal" @click.self="showMathModal = false">
        <div class="modal" style="max-width:440px">
          <div class="modal-header">
            <h3>Insert Math Formula</h3>
            <button class="btn-close" @click="showMathModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>LaTeX expression</label>
              <input
                v-model="mathInput"
                class="input-field"
                placeholder="e.g. x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}"
                @keyup.enter="confirmMath"
              />
            </div>
            <div v-if="mathInput" class="math-preview">
              Preview: <code>{{ mathInput }}</code>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-primary" @click="confirmMath">Insert</button>
            <button class="btn btn-outline" @click="showMathModal = false">Cancel</button>
          </div>
        </div>
      </div>

    </div>

    <!-- Meta row -->
    <div class="question-row-group">
      <div class="form-group">
        <label>Points</label>
        <input type="number" v-model.number="q.points" class="input-field" placeholder="1" min="1" />
      </div>
      <div class="form-group">
        <label>Topic Tag</label>
        <input v-model="q.topic_tag" class="input-field" placeholder="e.g. Supply & Demand" />
      </div>
      <div class="form-group">
        <label>Review Lesson</label>
        <select :value="q.linked_learning_page_id ?? ''" class="input-field" @change="selectLesson">
          <option value="">No linked lesson</option>
          <option v-for="page in lessonOptions" :key="page.page_id" :value="page.page_id">
            {{ page.module_title }} → {{ page.title }}
          </option>
        </select>
      </div>
    </div>

    <!-- TYPE-SPECIFIC ANSWER AREA  -->

    <!-- Multiple Choice — options: List[str], correct_answer: str -->
    <template v-if="q.type === 'multiple_choice'">
      <div class="options-block">

        <div class="options-block-header">
          <h4 class="text-sm font-semibold text-muted">OPTIONS</h4>
        </div>

        <div
          v-for="(optText, oi) in (q.options || [])"
          :key="oi"
          class="option-row"
          :class="{ 'is-correct': isOptionCorrect(optText) }"
        >

          <input
            v-if="!isMultiSelect"
            type="radio"
            :name="'mc_' + q.id"
            :value="optText"
            :checked="q.correct_answer === optText"
            class="option-radio"
            @change="q.correct_answer = optText"
          />

          <span class="option-letter">{{ letters[oi] || oi + 1 }}</span>

          <input
            :value="optText"
            placeholder="Option text"
            class="input-field option-input"
            @input="updateOption(oi, $event.target.value)"
          />

          <button
            v-if="q.options.length > 2"
            type="button"
            class="btn-remove"
            @click="removeOption(oi)"
          >
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>

          
        </div>

        <button
          v-if="(q.options || []).length < 6"
          type="button"
          class="btn btn-outline mt-2 btn-sm"
          @click="addOption"
        >+ Add Option</button>

      </div>
    </template>

    <!-- True / False — correct_answer: "True" | "False" -->
    <template v-else-if="q.type === 'true_false'">
      <div class="options-block">
        <div class="options-block-header">
          <h4 class="text-sm font-semibold text-muted">CORRECT ANSWER</h4>
        </div>
        <div class="tf-row">
          <button
            type="button"
            class="tf-option"
            :class="{ 'is-correct': q.correct_answer === 'True' }"
            @click="q.correct_answer = 'True'"
          >True</button>
          <button
            type="button"
            class="tf-option"
            :class="{ 'is-correct': q.correct_answer === 'False' }"
            @click="q.correct_answer = 'False'"
          >False</button>
        </div>
      </div>
    </template>

    <!-- Short Answer — correct_answer: str | list[str] for accepted variants -->
    <template v-else-if="q.type === 'short_answer'">
      <div class="options-block">
        <div class="options-block-header">
          <h4 class="text-sm font-semibold text-muted">ACCEPTED ANSWERS</h4>
          <span class="text-xs text-muted">Add variants for common phrasings</span>
        </div>

        <div
          v-for="(ans, ai) in shortAnswers"
          :key="ai"
          class="option-row"
        >
          <span class="option-letter">{{ ai + 1 }}</span>
          <input
            :value="ans"
            class="input-field option-input"
            placeholder="Accepted answer variant…"
            @input="updateShortAnswer(ai, $event.target.value)"
          />
          <button
            v-if="shortAnswers.length > 1"
            type="button"
            class="btn-remove"
            @click="removeShortAnswer(ai)"
          >✕</button>
        </div>

        <button type="button" class="btn btn-outline mt-2 btn-sm" @click="addShortAnswer">
          + Add Variant
        </button>

        <p class="text-xs text-muted mt-2">Case-insensitive. Each variant saves as a separate accepted answer.</p>
      </div>
    </template>

    <!-- Explanation (required, written by the teacher) -->
    <div class="form-group mt-2">
      <label>
        Explanation <span class="required-mark">*</span>
        <span class="text-xs text-muted">(your own words — shown after exam if enabled)</span>
      </label>
      <textarea
        v-model="q.explanation"
        class="input-field"
        :class="{ 'input-invalid': !hasExplanation }"
        rows="2"
        placeholder="Explain why the correct answer is correct…"
      />
      <p v-if="!hasExplanation" class="field-error">
        Required — write your own explanation before saving.
      </p>
    </div>

  </div>
</template>

<script>
// import katex from 'katex'
// import 'katex/dist/katex.min.css'

// const katexPreview = computed(() => {
//   if (!mathInput.value) return ''
//   try {
//     return katex.renderToString(mathInput.value, {
//       throwOnError: false,
//       displayMode: false
//     })
//   } catch {
//     return '<span style="color:red">Invalid formula</span>'
//   }
// })

export default {
  name: 'QuestionEditor',

  props: {
    // ExamQuestion object — mutated reactively in-place (parent holds the array)
    q:     { type: Object, required: true },
    index: { type: Number, required: true },
    lessonOptions: { type: Array, default: () => [] }
  },

  emits: ['remove'],

  data() {
    return {
      letters:       ['A', 'B', 'C', 'D', 'E', 'F'],
      showMathModal: false,
      mathInput:     '',
      savedRange:    null,
      // Derive from initial value — true when correct_answer is already a list
      isMultiSelect: Array.isArray(this.q.correct_answer)
    }
  },

  computed: {
    /**
     * short_answer: always expose as array for the editor rows,
     * but persist as str (single) or list[str] (multiple) in q.correct_answer
     */
    shortAnswers() {
      if (Array.isArray(this.q.correct_answer))  return this.q.correct_answer
      if (this.q.correct_answer != null && this.q.correct_answer !== '') return [this.q.correct_answer]
      return ['']
    },

    // the backend rejects a question without a teacher-written explanation
    hasExplanation() {
      return !!(this.q.explanation || '').trim()
    }
  },

  mounted() {
    // Populate contenteditable from q.text (plain text; _html is UI-only)
    if (this.$refs.editor) {
      this.$refs.editor.innerHTML = this.q._html || this.q.text || ''
    }
  },

  methods: {
    selectLesson(event) {
      const id = Number(event.target.value) || null
      this.q.linked_learning_page_id = id
      const lesson = this.lessonOptions.find(page => page.page_id === id)
      if (lesson && (!this.q.topic_tag || this.q.topic_tag === 'untagged')) {
        this.q.topic_tag = lesson.topic_tag || lesson.title
      }
    },

    /*  Rich-text  */
    execCmd(cmd) {
      this.$refs.editor.focus()
      document.execCommand(cmd, false, null)
    },

    onEditorInput() {
      // q.text  → plain text → stored in DB / schema
      // q._html → rich HTML  → UI display only (not in schema)
      this.q.text  = this.$refs.editor.innerText
      this.q._html = this.$refs.editor.innerHTML
    },

    syncText() {
      this.q.text  = this.$refs.editor.innerText
      this.q._html = this.$refs.editor.innerHTML
    },

    /* Math  */
    openMath() {
      const sel = window.getSelection()
      if (sel?.rangeCount) this.savedRange = sel.getRangeAt(0).cloneRange()
      this.mathInput     = ''
      this.showMathModal = true
    },

    confirmMath() {
      if (!this.mathInput.trim()) { this.showMathModal = false; return }
      this.$refs.editor.focus()
      if (this.savedRange) {
        const sel = window.getSelection()
        sel.removeAllRanges()
        sel.addRange(this.savedRange)
      }
      const html = `<span class="math-inline" data-latex="${this.mathInput}" contenteditable="false">[${this.mathInput}]</span>`
      document.execCommand('insertHTML', false, html)
      this.syncText()
      this.showMathModal = false
    },

    /* KaTex version */
    // confirmMath() {
    //   if (!mathInput.value.trim()) { showMathModal.value = false; return }

    //   this.$refs.editor.focus()
    //   if (savedRange.value) {
    //     const sel = window.getSelection()
    //     sel.removeAllRanges()
    //     sel.addRange(savedRange.value)
    //   }

    //   // Render KaTeX and wrap it with span(also store latex) // Don't forgot to npm install KaTex and import it
    //   const rendered = katex.renderToString(mathInput.value, {
    //     throwOnError: false,
    //     displayMode: false
    //   })
    //   const html = `<span 
    //     class="math-inline" 
    //     data-latex="${mathInput.value}" 
    //     contenteditable="false"
    //   >${rendered}</span>`

    //   document.execCommand('insertHTML', false, html)
    //   syncText()
    //   showMathModal.value = false
    // }

    /*  Image  */
    insertImage(evt) {
      const file = evt.target.files[0]
      if (!file) return
      const reader = new FileReader()
      reader.onload = (e) => {
        this.$refs.editor.focus()
        document.execCommand(
          'insertHTML', false,
          `<img src="${e.target.result}" style="max-width:100%;border-radius:6px;margin:4px 0" />`
        )
        this.syncText()
      }
      reader.readAsDataURL(file)
      evt.target.value = ''
    },

    /*  Multiple Choice helpers (options: List[str])  */
    addOption() {
      if (!this.q.options) this.q.options = []
      this.q.options.push('')
    },

    removeOption(oi) {
      const removed = this.q.options[oi]
      this.q.options.splice(oi, 1)
      // Keep correct_answer valid
      if (this.isMultiSelect && Array.isArray(this.q.correct_answer)) {
        this.q.correct_answer = this.q.correct_answer.filter(a => a !== removed)
      } else if (this.q.correct_answer === removed) {
        this.q.correct_answer = this.q.options[0] ?? ''
      }
    },

    updateOption(oi, newVal) {
      const old = this.q.options[oi]
      this.q.options[oi] = newVal

      // Patch correct_answer references to the old string
      if (this.isMultiSelect && Array.isArray(this.q.correct_answer)) {
        const idx = this.q.correct_answer.indexOf(old)
        if (idx !== -1) this.q.correct_answer[idx] = newVal
      } else if (this.q.correct_answer === old) {
        this.q.correct_answer = newVal
      }
    },

    isOptionCorrect(optText) {
      return this.isMultiSelect
        ? Array.isArray(this.q.correct_answer) && this.q.correct_answer.includes(optText)
        : this.q.correct_answer === optText
    },

    toggleMultiAnswer(optText) {
      if (!Array.isArray(this.q.correct_answer)) this.q.correct_answer = []
      const idx = this.q.correct_answer.indexOf(optText)
      if (idx === -1) this.q.correct_answer.push(optText)
      else            this.q.correct_answer.splice(idx, 1)
    },

    onMultiSelectToggle() {
      if (this.isMultiSelect) {
        // → list mode: wrap current single string
        const cur = this.q.correct_answer
        this.q.correct_answer = (cur && !Array.isArray(cur)) ? [cur] : []
      } else {
        // → single mode: take first element of list
        const arr = Array.isArray(this.q.correct_answer) ? this.q.correct_answer : []
        this.q.correct_answer = arr[0] ?? (this.q.options?.[0] ?? '')
      }
    },

    /* Short Answer helpers (correct_answer: str | list[str])  */
    updateShortAnswer(idx, val) {
      const arr = [...this.shortAnswers]
      arr[idx]  = val
      this.q.correct_answer = arr.length === 1 ? arr[0] : arr
    },

    addShortAnswer() {
      this.q.correct_answer = [...this.shortAnswers, '']
    },

    removeShortAnswer(idx) {
      const arr = this.shortAnswers.filter((_, i) => i !== idx)
      this.q.correct_answer = arr.length === 1 ? arr[0] : arr
    },

    /*  Type change  */
    onTypeChange() {
      this.isMultiSelect = false
      switch (this.q.type) {
        case 'multiple_choice':
          if (!this.q.options || this.q.options.length < 2)
            this.q.options = ['', '', '', '']
          this.q.correct_answer = this.q.options[0] ?? ''
          break
        case 'true_false':
          // schema allows options to store ['True','False'] for display
          this.q.options = ['True', 'False']
          this.q.correct_answer = 'True'
          break
        case 'short_answer':
          this.q.options = null   // null per schema comment
          this.q.correct_answer = ''
          break
      }
    }
  }
}
</script>

<style scoped>
.required-mark {
  color: #dc2626;
  font-weight: 700;
}

.input-invalid {
  border-color: #fca5a5;
  background: #fff7f7;
}

.field-error {
  margin-top: 0.25rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: #dc2626;
}

/* ══ Question card header ══════════════════════════════════ */
.qe-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding-bottom: 0.875rem;
  margin-bottom: 0.875rem;
  border-bottom: 1.5px solid var(--gray-light);
}

.type-select {
  font-size: 0.78rem;
  padding: 0.3rem 1.8rem 0.3rem 0.7rem;
  height: auto;
  max-width: 170px;
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  background-color: var(--gray-light);
  color: var(--text-main);
  font-family: inherit;
  font-weight: 600;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.6rem center;
  cursor: pointer;
  transition: border-color 0.15s ease;
}

.type-select:focus {
  outline: none;
  border-color: var(--primary-pink);
  background-color: var(--white);
}

.multi-toggle {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  cursor: pointer;
  user-select: none;
  font-weight: 500;
}

/* ══ RTE toolbar ══════════════════════════════════════════ */
.rte-toolbar {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  background: var(--gray-light);
  border: 1.5px solid var(--card-border);
  border-bottom: none;
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  padding: 0.3rem 0.6rem;
  flex-wrap: wrap;
}

.rte-btn {
  background: none;
  border: 1px solid transparent;
  border-radius: 5px;
  padding: 0.2rem 0.55rem;
  font-size: 0.82rem;
  cursor: pointer;
  color: var(--text-main);
  font-family: inherit;
  line-height: 1.4;
  transition: background 0.12s ease, border-color 0.12s ease;
}

.rte-btn:hover {
  background: var(--card-border);
  border-color: var(--card-border);
}

.img-btn    { cursor: pointer; }
.hidden-file { display: none; }
.math-icon  { font-family: serif; font-style: italic; font-size: 0.95rem; }

.rte-divider {
  width: 1px;
  height: 18px;
  background: var(--card-border);
  margin: 0 0.25rem;
}

.rte-editor {
  min-height: 80px;
  border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
  outline: none;
  line-height: 1.65;
  white-space: pre-wrap;
  background: var(--gray-light);
}

.rte-editor:focus {
  background: var(--white);
  border-color: var(--primary-pink) !important;
  box-shadow: 0 0 0 3px rgba(237, 64, 129, 0.08);
}

.rte-editor:empty::before {
  content: attr(data-placeholder);
  color: var(--text-muted);
  opacity: 0.6;
  pointer-events: none;
}

/* Math chip inside editor */
:deep(.math-inline) {
  display: inline-block;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: var(--radius-md);
  padding: 1px 6px;
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  color: #1d4ed8;
  margin: 0 2px;
  cursor: default;
}

/* Math preview in modal */
.math-preview {
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--gray-light);
  border-radius: var(--radius-md);
  font-size: 0.82rem;
  color: var(--text-main);
}

.math-preview code {
  font-family: 'Courier New', monospace;
  color: #1d4ed8;
}

/* ══ Options block ════════════════════════════════════════ */
.options-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.6rem;
}

.options-block-header h4 {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.btn-sm {
  font-size: 0.75rem;
  padding: 0.25rem 0.75rem;
}

/* ══ True / False ═════════════════════════════════════════ */
.tf-row { display: flex; gap: 0.75rem; }

.tf-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.5rem;
  border: 1.5px solid var(--card-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 600;
  font-family: inherit;
  font-size: 0.875rem;
  background: var(--gray-light);
  color: var(--text-main);
  transition: all 0.15s ease;
}

.tf-option:hover {
  border-color: var(--forest-green);
  background: var(--light-green);
  color: var(--forest-green);
}

.tf-option.is-correct {
  border-color: var(--forest-green);
  background: var(--light-green);
  color: var(--forest-green);
}

/* ═══════════════════════════════════════════════════════════
   7. Option rows  (Multiple Choice & Short Answer)
═══════════════════════════════════════════════════════════ */
.option-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.4rem 0.5rem;
  border-radius: var(--radius-md);
  margin-bottom: 0.35rem;
  transition: background 0.15s ease;
}

.option-row:hover                     { background: var(--white); }
.option-row.is-correct                { background: var(--light-green); }
.option-row.is-correct .option-letter {
  background: var(--forest-green);
  color: var(--white);
  border-color: var(--forest-green);
}

.option-radio {
  width: 15px;
  height: 15px;
  accent-color: var(--forest-green);
  cursor: pointer;
  flex-shrink: 0;
}

.option-letter {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-md);
  background: var(--white);
  border: 1.5px solid var(--card-border);
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  flex-shrink: 0;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}

.option-input {
  flex: 1;
  padding: 0.45rem 0.75rem;
  font-size: 0.875rem;
  background: var(--white);
  min-width: 0;
}

.btn-remove {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s ease, color 0.15s ease;
}

.btn-remove:hover {
  background: #fee2e2;
  color: #ef4444;
}
</style>
