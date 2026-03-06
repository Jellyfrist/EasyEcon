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
        <label>Linked Learning Page ID</label>
        <input type="number" v-model.number="q.linked_learning_page_id" class="input-field" placeholder="Optional" />
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
          
          <span>
            <!-- Editable option string — updates List[str] in place -->
            <input
              :value="optText"
              placeholder="Option text"
              class="input-field option-input"
              @input="updateOption(oi, $event.target.value)"
            />
            <button
              v-if="q.options.length > 2"
              type="button"
              class="btn-close"
              @click="removeOption(oi)"
            >✕</button>
          </span>

          
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

    <!-- Explanation -->
    <div class="form-group mt-2">
      <label>
        Explanation
        <span class="text-xs text-muted">(shown after exam if enabled)</span>
      </label>
      <textarea
        v-model="q.explanation"
        class="input-field"
        rows="2"
        placeholder="Explain the correct answer…"
      />
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
    index: { type: Number, required: true }
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
    }
  },

  mounted() {
    // Populate contenteditable from q.text (plain text; _html is UI-only)
    if (this.$refs.editor) {
      this.$refs.editor.innerHTML = this.q._html || this.q.text || ''
    }
  },

  methods: {

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
          this.q.options        = ['True', 'False']
          this.q.correct_answer = 'True'
          break
        case 'short_answer':
          this.q.options        = null   // null per schema comment
          this.q.correct_answer = ''
          break
      }
    }
  }
}
</script>

<style scoped>
/* ══ Header ═══════════════════════════════════════════════ */
.qe-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}
.type-select {
  font-size: 12px;
  padding: 4px 10px;
  height: auto;
  max-width: 180px;
}
.multi-toggle {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  user-select: none;
}

/* ══ RTE toolbar ══════════════════════════════════════════ */
.rte-toolbar {
  display: flex;
  align-items: center;
  gap: 3px;
  background: #f8f9fb;
  border: 1px solid #e2e5ea;
  border-bottom: none;
  border-radius: 8px 8px 0 0;
  padding: 5px 10px;
  flex-wrap: wrap;
}
.rte-btn {
  background: none;
  border: 1px solid transparent;
  border-radius: 5px;
  padding: 3px 8px;
  font-size: 13px;
  cursor: pointer;
  color: #374151;
  line-height: 1.4;
  transition: background 0.12s, border-color 0.12s;
}
.rte-btn:hover { background: #e9ecf0; border-color: #cbd1d9; }
.img-btn  { cursor: pointer; }
.hidden-file { display: none; }
.math-icon { font-family: serif; font-style: italic; font-size: 15px; }
.rte-divider { width: 1px; height: 20px; background: #d1d5db; margin: 0 4px; }

.rte-editor {
  min-height: 80px;
  border-radius: 0 0 8px 8px !important;
  outline: none;
  line-height: 1.65;
  white-space: pre-wrap;
}
.rte-editor:empty::before {
  content: attr(data-placeholder);
  color: #9ca3af;
  pointer-events: none;
}

/* Math chip inside editor */
:deep(.math-inline) {
  display: inline-block;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 4px;
  padding: 1px 6px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #1d4ed8;
  margin: 0 2px;
  cursor: default;
}

/* Math preview in modal */
.math-preview {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f8f9fb;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
}
.math-preview code { font-family: 'Courier New', monospace; color: #1d4ed8; }

/* ══ Options ══════════════════════════════════════════════ */
.options-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.btn-sm { font-size: 12px; padding: 4px 12px; }

/* ══ True / False ═════════════════════════════════════════ */
.tf-row   { display: flex; gap: 12px; }
.tf-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  background: white;
  font-size: 14px;
  transition: border-color 0.15s, background 0.15s, color 0.15s;
}
.tf-option:hover { border-color: #94a3b8; }
.tf-option.is-correct {
  border-color: #22c55e;
  background: #f0fdf4;
  color: #15803d;
}
</style>