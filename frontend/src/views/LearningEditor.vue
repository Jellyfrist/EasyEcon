<template>
  <div class="le-root">

    <!-- sticky topbar -->
    <header class="le-topbar">
      <div class="le-topbar-left">
        <button class="le-back-btn" @click="router.push(`/teacher/modules/${courseIdParam}`)">
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <nav class="le-breadcrumb">
          <button class="le-bc-link" @click="router.push(`/teacher/modules/${courseIdParam}`)">Modules</button>
          <span class="le-bc-sep">›</span>
          <span class="le-bc-cur">{{ isEditMode ? 'Edit Lesson' : 'New Lesson' }}</span>
        </nav>
      </div>

      <div class="le-topbar-center">
        <!-- tab switcher -->
        <div class="le-tabs">
          <button class="le-tab" :class="{ 'le-tab-active': activeTab === 'content' }" @click="activeTab = 'content'">
            <span class="material-symbols-outlined">article</span> Content
          </button>
          <button class="le-tab" :class="{ 'le-tab-active': activeTab === 'quiz' }" @click="activeTab = 'quiz'">
            <span class="material-symbols-outlined">quiz</span> Mini Quiz
            <span v-if="quiz.isEnabled && quiz.questions.length > 0" class="le-tab-badge">{{ quiz.questions.length }}</span>
          </button>
        </div>
      </div>

      <div class="le-topbar-right">
        <span class="le-publish-label">Published</span>
        <label class="le-toggle">
          <input type="checkbox" v-model="isPublished">
          <span class="le-toggle-track"></span>
        </label>
        <button
          class="le-save-btn"
          :disabled="isSaving || !lesson.title.trim()"
          @click="saveLesson"
        >
          <span class="material-symbols-outlined">{{ isSaving ? 'hourglass_empty' : (isEditMode ? 'save' : 'add_circle') }}</span>
          {{ isSaving ? 'Saving…' : (isEditMode ? 'Save' : 'Create Lesson') }}
        </button>
      </div>
    </header>

    <!-- loading -->
    <div v-if="isLoading" class="le-loading">
      <div class="le-spinner"></div>
      <p>Loading lesson…</p>
    </div>

    <template v-else>

      <!-- ===== CONTENT TAB ===== -->
      <div v-show="activeTab === 'content'" class="le-content-layout">

        <!-- left: section outline -->
        <aside class="le-outline">
          <p class="le-outline-label">SECTIONS</p>
          <div class="le-outline-list">
            <button
              v-for="(section, i) in lesson.sections"
              :key="section.id"
              class="le-outline-item"
              :class="{ 'le-outline-item-active': activeSectionId === section.id }"
              @click="setActiveSection(section.id)"
            >
              <span class="le-outline-num">{{ i + 1 }}</span>
              <span class="le-outline-name">{{ section.title || `Section ${i + 1}` }}</span>
              <button
                v-if="lesson.sections.length > 1"
                class="le-outline-del"
                @click.stop="removeSection(section.id)"
                title="Remove section"
              >
                <span class="material-symbols-outlined">close</span>
              </button>
            </button>
          </div>
          <button class="le-add-section-btn" @click="addSection">
            <span class="material-symbols-outlined">add</span> Add section
          </button>
        </aside>

        <!-- center: editor -->
        <main class="le-editor-area">

          <!-- lesson title (only once, top of editor) -->
          <input
            v-model="lesson.title"
            class="le-lesson-title-input"
            placeholder="Lesson title…"
            maxlength="120"
          />

          <!-- section name -->
          <input
            v-if="activeSection"
            v-model="activeSection.title"
            class="le-section-name-input"
            placeholder="Section name (e.g. Why Prices Change)"
          />

          <!-- sticky formatting toolbar -->
          <div class="le-toolbar">
            <div class="le-tool-group">
              <button class="le-tool-btn" @mousedown.prevent="execCmd('undo')" title="Undo">
                <span class="material-symbols-outlined">undo</span>
              </button>
              <button class="le-tool-btn" @mousedown.prevent="execCmd('redo')" title="Redo">
                <span class="material-symbols-outlined">redo</span>
              </button>
            </div>
            <div class="le-tool-divider"></div>
            <select class="le-format-select" v-model="currentFormat" @change="changeFormat($event)" title="Text format">
              <option value="P">Normal</option>
              <option value="H1">Heading 1</option>
              <option value="H2">Heading 2</option>
              <option value="H3">Heading 3</option>
            </select>
            <div class="le-tool-divider"></div>
            <div class="le-tool-group">
              <button class="le-tool-btn" @click="execCmd('bold')" title="Bold"><span class="material-symbols-outlined">format_bold</span></button>
              <button class="le-tool-btn" @click="execCmd('italic')" title="Italic"><span class="material-symbols-outlined">format_italic</span></button>
              <button class="le-tool-btn" @click="execCmd('underline')" title="Underline"><span class="material-symbols-outlined">format_underlined</span></button>
              <button class="le-tool-btn" @click="clearFormat" title="Clear formatting"><span class="material-symbols-outlined">format_clear</span></button>
            </div>
            <div class="le-tool-divider"></div>
            <div class="le-tool-group">
              <button class="le-tool-btn" @click="execCmd('insertUnorderedList')" title="Bullet list"><span class="material-symbols-outlined">format_list_bulleted</span></button>
              <button class="le-tool-btn" @click="execCmd('insertOrderedList')" title="Numbered list"><span class="material-symbols-outlined">format_list_numbered</span></button>
            </div>
            <div class="le-tool-spacer"></div>
            <button class="le-img-btn" @click="triggerImageUpload">
              <span class="material-symbols-outlined">image</span> Photo
            </button>
            <input type="file" accept="image/*" ref="imageInput" class="le-file-input" @change="onImageUpload" />
          </div>

          <!-- rich text area -->
          <div
            class="le-rich-text"
            contenteditable="true"
            ref="contentArea"
            @input="updateContent"
            @keyup="checkFormat"
            @mouseup="checkFormat"
            @keydown="handleKeydown"
          ></div>

        </main>
      </div>

      <!-- ===== QUIZ TAB ===== -->
      <div v-show="activeTab === 'quiz'" class="le-quiz-layout">
        <div class="le-quiz-inner">

          <div class="le-quiz-header">
            <div class="le-quiz-header-info">
              <div class="le-quiz-icon" :class="quiz.isEnabled ? 'le-quiz-icon-on' : 'le-quiz-icon-off'">
                <span class="material-symbols-outlined">quiz</span>
              </div>
              <div>
                <h2 class="le-quiz-title-heading">Mini Quiz</h2>
                <p class="le-quiz-subtitle">Auto-graded questions shown after the lesson content.</p>
              </div>
            </div>
            <button
              class="le-quiz-toggle-btn"
              :class="quiz.isEnabled ? 'le-quiz-toggle-off' : 'le-quiz-toggle-on'"
              @click="toggleQuiz"
            >
              {{ quiz.isEnabled ? 'Disable quiz' : 'Enable quiz' }}
            </button>
          </div>

          <template v-if="quiz.isEnabled">
            <input
              v-model="quiz.title"
              class="le-quiz-name-input"
              placeholder="Quiz title (e.g. Check Your Understanding)"
            />

            <div class="le-question-list">
              <div
                v-for="(q, qi) in quiz.questions"
                :key="q.id"
                class="le-question-card"
              >
                <div class="le-question-top">
                  <span class="le-q-badge">Q{{ qi + 1 }}</span>
                  <button class="le-q-del" @click="removeQuizQuestion(qi)" title="Remove question">
                    <span class="material-symbols-outlined">delete</span>
                  </button>
                </div>

                <textarea
                  v-model="q.text"
                  rows="2"
                  class="le-q-text"
                  placeholder="Question text…"
                ></textarea>

                <div class="le-options">
                  <div
                    v-for="(opt, oi) in q.options"
                    :key="oi"
                    class="le-option-row"
                    :class="{ 'le-option-correct': q.correct_answer_index === oi }"
                  >
                    <input
                      type="radio"
                      :name="'q_' + q.id"
                      :value="oi"
                      v-model="q.correct_answer_index"
                      class="le-radio"
                      title="Mark as correct answer"
                    />
                    <input
                      v-model="q.options[oi]"
                      type="text"
                      class="le-option-input"
                      :placeholder="'Option ' + (oi + 1)"
                    />
                  </div>
                </div>

                <textarea
                  v-model="q.explanation"
                  rows="2"
                  class="le-q-explanation"
                  placeholder="Explanation shown after student answers (optional)…"
                ></textarea>
              </div>
            </div>

            <button class="le-add-q-btn" @click="addQuizQuestion">
              <span class="material-symbols-outlined">add</span> Add question
            </button>
          </template>

          <div v-else class="le-quiz-empty">
            <span class="material-symbols-outlined le-quiz-empty-icon">quiz</span>
            <p>Enable the quiz to add questions for this lesson.</p>
          </div>

        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import learningService from '@/services/learningService'

const route  = useRoute()
const router = useRouter()

const isSaving   = ref(false)
const isLoading  = ref(true)
const activeTab  = ref('content')
const isPublished = ref(true)

const courseIdParam = route.params.courseId
const moduleIdParam = route.params.moduleId
const pageIdParam   = route.params.pageId

const isEditMode = computed(() => !!pageIdParam)

const lesson = ref({
  id: isEditMode.value ? parseInt(pageIdParam, 10) : null,
  title: '',
  module_id: parseInt(moduleIdParam, 10),
  sections: [{ id: Date.now(), title: '', content: '' }]
})

const quiz = ref({
  isEnabled: false,
  title: 'Check Your Understanding',
  questions: []
})

const activeSectionId = ref(lesson.value.sections[0].id)
const contentArea     = ref(null)
const imageInput      = ref(null)
const currentFormat   = ref('P')

const activeSection = computed(() =>
  lesson.value.sections.find(s => s.id === activeSectionId.value)
)

// ── image upload ──────────────────────────────────────────
const fileToBase64 = file => new Promise((res, rej) => {
  const r = new FileReader()
  r.onload = () => res(r.result)
  r.onerror = rej
  r.readAsDataURL(file)
})

const triggerImageUpload = () => imageInput.value.click()

const onImageUpload = async e => {
  const file = e.target.files[0]
  if (!file) return
  try {
    const b64 = await fileToBase64(file)
    execCmd('insertImage', b64)
  } catch {
    alert('Image upload failed.')
  }
  e.target.value = ''
}

// ── toolbar ───────────────────────────────────────────────
const changeFormat = e => {
  document.execCommand('formatBlock', false, e.target.value)
  updateContent()
  currentFormat.value = e.target.value
}

const checkFormat = () => {
  const block = document.queryCommandValue('formatBlock').toUpperCase()
  currentFormat.value = ['H1','H2','H3','P'].includes(block) ? block : 'P'
}

const clearFormat = () => { document.execCommand('removeFormat', false, null); updateContent() }

const handleKeydown = e => {
  if (e.key === 'Tab') {
    e.preventDefault()
    document.execCommand('insertHTML', false, '&nbsp;&nbsp;&nbsp;&nbsp;')
    updateContent()
  }
}

const execCmd = (cmd, value = null) => {
  contentArea.value?.focus()
  document.execCommand(cmd, false, value)
  updateContent()
}

const updateContent = () => {
  if (activeSection.value && contentArea.value)
    activeSection.value.content = contentArea.value.innerHTML
}

// ── sections ──────────────────────────────────────────────
const setActiveSection = async id => {
  updateContent()
  activeSectionId.value = id
  await nextTick()
  if (contentArea.value && activeSection.value)
    contentArea.value.innerHTML = activeSection.value.content || ''
}

const addSection = () => {
  const s = { id: Date.now(), title: '', content: '' }
  lesson.value.sections.push(s)
  setActiveSection(s.id)
}

const removeSection = id => {
  lesson.value.sections = lesson.value.sections.filter(s => s.id !== id)
  if (activeSectionId.value === id)
    setActiveSection(lesson.value.sections[0].id)
}

// ── quiz ──────────────────────────────────────────────────
const toggleQuiz = () => {
  quiz.value.isEnabled = !quiz.value.isEnabled
  if (quiz.value.isEnabled && quiz.value.questions.length === 0) addQuizQuestion()
}

const addQuizQuestion = () => {
  quiz.value.questions.push({
    id: 'q_' + Date.now(),
    text: '',
    options: ['', '', '', ''],
    correct_answer_index: 0,
    explanation: ''
  })
}

const removeQuizQuestion = i => {
  if (confirm('Remove this question?')) quiz.value.questions.splice(i, 1)
}

// ── load ──────────────────────────────────────────────────
const loadLessonData = async () => {
  if (!isEditMode.value) { isLoading.value = false; return }
  try {
    const res  = await learningService.getPage(lesson.value.id)
    const data = res.data
    lesson.value.title     = data.title
    lesson.value.module_id = data.module_id
    isPublished.value      = data.is_published ?? true

    let blocks = data.content_blocks
    if (typeof blocks === 'string') blocks = JSON.parse(blocks)

    if (blocks?.length) {
      const loadedSections = []
      blocks.forEach(block => {
        if (block.type === 'rich_text_section') {
          loadedSections.push({
            id: block.id || Date.now() + Math.random(),
            title: block.data?.title || '',
            content: block.data?.html || ''
          })
        } else if (block.type === 'mini_quiz') {
          quiz.value.isEnabled = true
          quiz.value.title     = block.data?.title || 'Check Your Understanding'
          if (block.data?.questions) {
            quiz.value.questions = block.data.questions.map(q => ({
              ...q,
              correct_answer_index: q.correct_index ?? 0
            }))
          }
        }
      })
      if (loadedSections.length) {
        lesson.value.sections  = loadedSections
        activeSectionId.value  = loadedSections[0].id
      }
    }
  } catch (err) {
    console.error('Load Error:', err)
    alert('Could not load lesson data.')
  } finally {
    isLoading.value = false
    await nextTick()
    if (contentArea.value && activeSection.value)
      contentArea.value.innerHTML = activeSection.value.content || ''
  }
}

// ── save ──────────────────────────────────────────────────
const saveLesson = async () => {
  if (!lesson.value.module_id || isNaN(lesson.value.module_id)) {
    alert('Module ID not found. Open this page from the course editor.')
    return
  }
  if (!lesson.value.title.trim()) {
    alert('Please enter a lesson title.')
    return
  }

  updateContent()
  isSaving.value = true

  try {
    const contentBlocks = lesson.value.sections.map((sec, i) => ({
      id: `sec_${i}_${Date.now()}`,
      type: 'rich_text_section',
      data: { title: sec.title, html: sec.content }
    }))

    if (quiz.value.isEnabled && quiz.value.questions.length > 0) {
      contentBlocks.push({
        id: `quiz_${Date.now()}`,
        type: 'mini_quiz',
        data: {
          title: quiz.value.title,
          questions: quiz.value.questions.map(q => ({
            id: q.id,
            type: 'multiple_choice',
            text: q.text,
            options: q.options,
            correct_answer: q.options[q.correct_answer_index] || q.options[0],
            correct_index: q.correct_answer_index,
            explanation: q.explanation
          }))
        }
      })
    }

    const payload = {
      title: lesson.value.title.trim(),
      module_id: lesson.value.module_id,
      order_index: 0,
      template_type: 'standard_text',
      is_published: isPublished.value,
      content_blocks: contentBlocks
    }

    if (isEditMode.value) {
      await learningService.updatePage(lesson.value.id, payload)
    } else {
      await learningService.createPage(payload)
    }

    router.push(`/teacher/modules/${courseIdParam}`)

  } catch (err) {
    console.error('Save Error:', err)
    alert('Failed to save. Please try again.')
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  loadLessonData()
  document.execCommand('defaultParagraphSeparator', false, 'p')
})
</script>

<style scoped>
/* ── tokens ───────────────────────────────────────────── */
.le-root {
  --pink: #ed4081;
  --pink-h: #d13570;
  --pink-bg: #fce7ef;
  --pink-light: #ffc7db;
  --ink: #0f172a;
  --ink2: #334155;
  --muted: #64748b;
  --border: #e2e8f0;
  --bg: #f8f9fb;
  --white: #ffffff;
  --topbar-h: 56px;
  --outline-w: 220px;
  font-family: 'DM Sans', 'Helvetica Neue', sans-serif;
  background: var(--bg);
  min-height: 100vh;
}

/* ── topbar ───────────────────────────────────────────── */
.le-topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  height: var(--topbar-h);
  background: var(--white);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.25rem;
  gap: 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.le-topbar-left  { display: flex; align-items: center; gap: 0.75rem; min-width: 0; flex: 1; }
.le-topbar-center { flex-shrink: 0; }
.le-topbar-right { display: flex; align-items: center; gap: 0.75rem; flex: 1; justify-content: flex-end; }

.le-back-btn {
  width: 34px; height: 34px;
  border-radius: 8px;
  background: transparent;
  border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: var(--muted);
  transition: background 0.15s, color 0.15s;
  flex-shrink: 0;
}
.le-back-btn:hover { background: var(--bg); color: var(--ink); }
.le-back-btn .material-symbols-outlined { font-size: 18px; }

.le-breadcrumb { display: flex; align-items: center; gap: 4px; font-size: 0.8rem; }
.le-bc-link { background: none; border: none; color: var(--muted); cursor: pointer; padding: 0; font-size: 0.8rem; font-family: inherit; }
.le-bc-link:hover { color: var(--pink); }
.le-bc-sep { color: var(--border); }
.le-bc-cur { color: var(--ink2); font-weight: 600; }

/* tabs */
.le-tabs { display: flex; background: var(--bg); border-radius: 10px; padding: 3px; gap: 2px; border: 1px solid var(--border); }
.le-tab {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 14px;
  border-radius: 7px;
  border: none; background: transparent;
  font-size: 0.82rem; font-weight: 600; font-family: inherit;
  color: var(--muted); cursor: pointer;
  transition: background 0.15s, color 0.15s;
  position: relative;
}
.le-tab .material-symbols-outlined { font-size: 16px; }
.le-tab:hover { color: var(--ink2); }
.le-tab-active { background: var(--white) !important; color: var(--pink) !important; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.le-tab-badge {
  background: var(--pink); color: #fff;
  font-size: 0.65rem; font-weight: 700;
  padding: 1px 6px; border-radius: 99px;
  line-height: 1.6;
}

/* publish toggle */
.le-publish-label { font-size: 0.78rem; color: var(--muted); font-weight: 500; }
.le-toggle { position: relative; display: inline-block; width: 36px; height: 20px; cursor: pointer; }
.le-toggle input { opacity: 0; width: 0; height: 0; }
.le-toggle-track {
  position: absolute; inset: 0;
  background: #cbd5e1; border-radius: 99px;
  transition: background 0.2s;
}
.le-toggle-track::after {
  content: ''; position: absolute;
  left: 3px; top: 3px;
  width: 14px; height: 14px;
  background: #fff; border-radius: 50%;
  transition: transform 0.2s;
}
.le-toggle input:checked + .le-toggle-track { background: var(--pink); }
.le-toggle input:checked + .le-toggle-track::after { transform: translateX(16px); }

/* save button */
.le-save-btn {
  display: flex; align-items: center; gap: 6px;
  background: var(--pink); color: #fff;
  border: none; padding: 0 18px; height: 36px;
  border-radius: 9px; font-size: 0.85rem; font-weight: 700;
  font-family: inherit; cursor: pointer;
  box-shadow: 0 2px 8px rgba(237,64,129,0.25);
  transition: background 0.15s, transform 0.15s, opacity 0.15s;
  white-space: nowrap;
}
.le-save-btn .material-symbols-outlined { font-size: 17px; }
.le-save-btn:hover:not(:disabled) { background: var(--pink-h); transform: translateY(-1px); }
.le-save-btn:disabled { opacity: 0.45; cursor: not-allowed; transform: none; }

/* ── loading ──────────────────────────────────────────── */
.le-loading {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: calc(100vh - var(--topbar-h));
  gap: 1rem; color: var(--muted); font-size: 0.9rem;
}
.le-spinner {
  width: 36px; height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--pink);
  border-radius: 50%;
  animation: le-spin 0.8s linear infinite;
}
@keyframes le-spin { to { transform: rotate(360deg); } }

/* ── content tab layout ───────────────────────────────── */
.le-content-layout {
  display: flex;
  height: calc(100vh - var(--topbar-h));
  overflow: hidden;
}

/* ── outline sidebar ──────────────────────────────────── */
.le-outline {
  width: var(--outline-w);
  flex-shrink: 0;
  border-right: 1px solid var(--border);
  background: var(--white);
  display: flex;
  flex-direction: column;
  padding: 1.25rem 0.75rem;
  overflow-y: auto;
  gap: 0.5rem;
}

.le-outline-label {
  font-size: 0.68rem; font-weight: 700;
  letter-spacing: 0.08em; color: var(--muted);
  padding: 0 0.5rem; margin-bottom: 0.25rem;
}

.le-outline-list { display: flex; flex-direction: column; gap: 3px; }

.le-outline-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px; border-radius: 8px;
  background: transparent; border: none;
  font-family: inherit; font-size: 0.82rem;
  color: var(--ink2); cursor: pointer;
  text-align: left; width: 100%;
  transition: background 0.15s;
}
.le-outline-item:hover { background: var(--bg); }
.le-outline-item-active { background: var(--pink-bg) !important; color: var(--pink); font-weight: 600; }

.le-outline-num {
  width: 20px; height: 20px; border-radius: 5px;
  background: var(--bg); font-size: 0.7rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; color: var(--muted);
}
.le-outline-item-active .le-outline-num { background: var(--pink-light); color: var(--pink); }

.le-outline-name { flex: 1; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }

.le-outline-del {
  opacity: 0; background: none; border: none; cursor: pointer;
  color: var(--muted); padding: 0; line-height: 1;
  transition: opacity 0.15s, color 0.15s;
  display: flex; align-items: center;
}
.le-outline-del .material-symbols-outlined { font-size: 15px; }
.le-outline-item:hover .le-outline-del { opacity: 1; }
.le-outline-del:hover { color: #ef4444; }

.le-add-section-btn {
  display: flex; align-items: center; gap: 6px;
  margin-top: 0.5rem; padding: 8px 10px;
  background: none; border: 1.5px dashed var(--border);
  border-radius: 8px; font-size: 0.8rem; font-weight: 600;
  color: var(--muted); cursor: pointer; font-family: inherit;
  transition: border-color 0.15s, color 0.15s;
  width: 100%;
}
.le-add-section-btn .material-symbols-outlined { font-size: 16px; }
.le-add-section-btn:hover { border-color: var(--pink); color: var(--pink); }

/* ── editor area ──────────────────────────────────────── */
.le-editor-area {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  background: var(--white);
}

.le-lesson-title-input {
  font-size: 1.85rem; font-weight: 800;
  color: var(--ink); border: none; outline: none;
  padding: 2rem 3rem 0.25rem;
  font-family: inherit;
  background: transparent;
  width: 100%; box-sizing: border-box;
}
.le-lesson-title-input::placeholder { color: #c0c8d4; }

.le-section-name-input {
  font-size: 1rem; font-weight: 600;
  color: var(--pink); border: none; outline: none;
  padding: 0.25rem 3rem 1.25rem;
  font-family: inherit;
  background: transparent;
  width: 100%; box-sizing: border-box;
  border-bottom: 1px solid var(--border);
}
.le-section-name-input::placeholder { color: var(--pink-light); }

/* ── toolbar ──────────────────────────────────────────── */
.le-toolbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex; align-items: center; flex-wrap: wrap; gap: 4px;
  padding: 8px 3rem;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}

.le-tool-group { display: flex; align-items: center; gap: 2px; }

.le-tool-btn {
  width: 32px; height: 32px;
  border-radius: 7px; border: none;
  background: transparent; cursor: pointer;
  color: var(--ink2); display: flex; align-items: center; justify-content: center;
  transition: background 0.12s, color 0.12s;
}
.le-tool-btn .material-symbols-outlined { font-size: 18px; }
.le-tool-btn:hover { background: var(--bg); color: var(--pink); }

.le-tool-divider { width: 1px; height: 20px; background: var(--border); margin: 0 4px; }
.le-tool-spacer  { flex: 1; }

.le-format-select {
  height: 32px; padding: 0 8px;
  border: 1px solid var(--border); border-radius: 7px;
  background: var(--white); font-size: 0.8rem;
  font-weight: 600; color: var(--ink2);
  font-family: inherit; cursor: pointer; outline: none;
}
.le-format-select:focus { border-color: var(--pink); }

.le-img-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 5px 12px; border-radius: 7px;
  background: var(--pink-bg); color: var(--pink);
  border: 1px solid var(--pink-light);
  font-size: 0.8rem; font-weight: 700;
  font-family: inherit; cursor: pointer;
  transition: background 0.15s;
}
.le-img-btn .material-symbols-outlined { font-size: 16px; }
.le-img-btn:hover { background: var(--pink-light); }

.le-file-input { display: none; }

/* ── rich text ────────────────────────────────────────── */
.le-rich-text {
  flex: 1;
  outline: none;
  padding: 1.75rem 3rem 4rem;
  min-height: 400px;
  font-size: 1rem; line-height: 1.8;
  color: var(--ink2);
  caret-color: var(--pink);
}
.le-rich-text :deep(h1) { font-size: 2rem; font-weight: 800; margin: 1.5rem 0 0.75rem; color: var(--ink); }
.le-rich-text :deep(h2) { font-size: 1.5rem; font-weight: 700; margin: 1.25rem 0 0.6rem; color: var(--ink); }
.le-rich-text :deep(h3) { font-size: 1.2rem; font-weight: 600; margin: 1rem 0 0.5rem; color: var(--ink2); }
.le-rich-text :deep(p)  { margin: 0.5rem 0; }
.le-rich-text :deep(ul), .le-rich-text :deep(ol) { padding-left: 1.5rem; margin: 0.5rem 0; }
.le-rich-text :deep(img) {
  max-width: 100%; height: auto; border-radius: 10px;
  margin: 1.5rem 0; display: block;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

/* ── quiz tab ─────────────────────────────────────────── */
.le-quiz-layout {
  height: calc(100vh - var(--topbar-h));
  overflow-y: auto;
  background: var(--bg);
  display: flex; justify-content: center;
  padding: 2rem 1.5rem 4rem;
}

.le-quiz-inner { width: 100%; max-width: 760px; display: flex; flex-direction: column; gap: 1.5rem; }

.le-quiz-header {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.5rem;
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  flex-wrap: wrap;
}
.le-quiz-header-info { display: flex; align-items: center; gap: 1rem; }

.le-quiz-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.le-quiz-icon .material-symbols-outlined { font-size: 24px; }
.le-quiz-icon-on  { background: #ecfdf5; color: #10b981; }
.le-quiz-icon-off { background: var(--bg); color: var(--muted); }

.le-quiz-title-heading { margin: 0; font-size: 1.1rem; font-weight: 700; color: var(--ink); }
.le-quiz-subtitle { margin: 2px 0 0; font-size: 0.82rem; color: var(--muted); }

.le-quiz-toggle-btn {
  padding: 8px 18px; border-radius: 9px;
  font-size: 0.83rem; font-weight: 700;
  font-family: inherit; cursor: pointer;
  border: none; transition: all 0.15s; white-space: nowrap;
}
.le-quiz-toggle-on  { background: #10b981; color: #fff; box-shadow: 0 2px 8px rgba(16,185,129,0.25); }
.le-quiz-toggle-on:hover  { background: #059669; }
.le-quiz-toggle-off { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
.le-quiz-toggle-off:hover { background: #fee2e2; }

.le-quiz-name-input {
  width: 100%; box-sizing: border-box;
  padding: 0.9rem 1.1rem;
  font-size: 1rem; font-weight: 700;
  border: 1.5px solid var(--border); border-radius: 10px;
  background: var(--white); color: var(--ink);
  font-family: inherit; outline: none;
  transition: border-color 0.15s;
}
.le-quiz-name-input:focus { border-color: var(--pink); }

.le-question-list { display: flex; flex-direction: column; gap: 1rem; }

.le-question-card {
  background: var(--white);
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  display: flex; flex-direction: column; gap: 0.85rem;
  transition: border-color 0.15s;
}
.le-question-card:focus-within { border-color: var(--pink-light); }

.le-question-top { display: flex; align-items: center; justify-content: space-between; }

.le-q-badge {
  background: var(--pink-bg); color: var(--pink);
  font-size: 0.72rem; font-weight: 700;
  padding: 3px 10px; border-radius: 6px; letter-spacing: 0.04em;
}

.le-q-del {
  background: none; border: none; cursor: pointer;
  color: var(--muted); display: flex; align-items: center;
  padding: 4px; border-radius: 6px;
  transition: background 0.12s, color 0.12s;
}
.le-q-del .material-symbols-outlined { font-size: 17px; }
.le-q-del:hover { background: #fef2f2; color: #ef4444; }

.le-q-text, .le-q-explanation {
  width: 100%; box-sizing: border-box;
  padding: 0.75rem 0.9rem;
  border: 1.5px solid var(--border); border-radius: 9px;
  font-family: inherit; font-size: 0.9rem;
  color: var(--ink2); resize: vertical; outline: none;
  transition: border-color 0.15s;
}
.le-q-text:focus, .le-q-explanation:focus { border-color: var(--pink); }
.le-q-explanation { background: #f0fdf4; border-color: #bbf7d0; font-size: 0.83rem; color: #065f46; }
.le-q-explanation::placeholder { color: #86efac; }

.le-options { display: flex; flex-direction: column; gap: 6px; }

.le-option-row {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 12px; border-radius: 9px;
  border: 1.5px solid var(--border);
  background: var(--white);
  transition: border-color 0.15s, background 0.15s;
}
.le-option-correct { border-color: #86efac; background: #f0fdf4; }

.le-radio { width: 17px; height: 17px; accent-color: #10b981; cursor: pointer; flex-shrink: 0; }

.le-option-input {
  flex: 1; border: none; outline: none;
  font-family: inherit; font-size: 0.88rem;
  color: var(--ink2); background: transparent;
}
.le-option-input::placeholder { color: #c0c8d4; }

.le-add-q-btn {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 14px; width: 100%;
  border: 2px dashed var(--border); border-radius: 12px;
  background: none; font-family: inherit;
  font-size: 0.88rem; font-weight: 700; color: var(--muted);
  cursor: pointer; transition: border-color 0.15s, color 0.15s;
}
.le-add-q-btn .material-symbols-outlined { font-size: 18px; }
.le-add-q-btn:hover { border-color: var(--pink); color: var(--pink); }

.le-quiz-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 1rem; padding: 5rem 2rem;
  background: var(--white); border: 1px solid var(--border); border-radius: 14px;
  color: var(--muted); font-size: 0.9rem; text-align: center;
}
.le-quiz-empty-icon { font-size: 3rem; color: var(--border); }

/* ── responsive ───────────────────────────────────────── */
@media (max-width: 768px) {
  .le-outline { display: none; }
  .le-lesson-title-input,
  .le-section-name-input { padding-left: 1.25rem; padding-right: 1.25rem; }
  .le-toolbar { padding-left: 1.25rem; padding-right: 1.25rem; }
  .le-rich-text { padding: 1.25rem 1.25rem 4rem; }
  .le-topbar-center .le-bc-link,
  .le-topbar-center .le-bc-sep { display: none; }
  .le-publish-label { display: none; }
}
</style>