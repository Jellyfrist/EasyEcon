<template>
    <div class="editor-page">
    
        <!-- top bar -->
        <div class="editor-topbar">
            <router-link :to="backLink" class="back-btn">
                <span class="material-symbols-outlined">arrow_back</span>
            </router-link>
            <h1 class="topbar-title">
                {{ isEditMode ? 'Edit Flashcard Set' : 'Create a new flashcard set' }}
            </h1>
            <div class="topbar-actions">
                <button class="btn-light" :disabled="store.loading || !setForm.title.trim()" @click="saveSet">
                  {{ isEditMode ? 'Save' : 'Create' }}
                </button>
                <button v-if="!isEditMode" class="btn-primary-pill" :disabled="store.loading || !setForm.title.trim()" @click="saveAndStudy">
                  Create and practice
                </button>
            </div>
        </div>
    
        <!-- set title + description -->
        <div class="meta-section">
            <div class="meta-card">
                <div class="meta-field">
                    <label class="meta-label">SET TITLE</label>
                    <input v-model="setForm.title" class="meta-input" placeholder="Enter a title..." maxlength="100" />
                </div>
                <div class="meta-divider"></div>
                <div class="meta-field">
                    <label class="meta-label">DESCRIPTION</label>
                    <input v-model="setForm.description" class="meta-input" placeholder="Add a description (optional)..." maxlength="300" />
                </div>
            </div>
        </div>
    
        <!-- cards -->
        <div v-if="setReady" class="cards-section">
    
            <!-- existing cards: always inline editable -->
            <div v-for="(card, idx) in localCards" :key="card.id" class="card-row">
                <!-- number + delete -->
                <div class="row-header">
                    <span class="row-num">{{ idx + 1 }}</span>
                    <button class="row-delete-btn" title="delete" @click="cardToDelete = card">
                    <span class="material-symbols-outlined">delete</span>
                  </button>
                </div>
    
                <!-- term + definition + image -->
                <div class="row-body">
                    <div class="input-col">
                        <textarea v-model="card.term" class="card-textarea" placeholder="Enter term" rows="1" @input="autoResize" @blur="autoSaveCard(card)"></textarea>
                        <span class="input-label">TERM</span>
                    </div>
                    <div class="input-col">
                        <textarea v-model="card.definition" class="card-textarea" placeholder="Enter definition" rows="1" @input="autoResize" @blur="autoSaveCard(card)"></textarea>
                        <span class="input-label">DEFINITION</span>
                    </div>
                    <!-- image -->
                    <div class="input-col-img">
                        <div v-if="card.image_url" class="img-preview-wrap">
                            <img :src="card.image_url" class="img-preview" alt="image" />
                            <button class="img-remove-btn" @click="removeImage(card)">
                        <span class="material-symbols-outlined">close</span>
                      </button>
                        </div>
                        <label v-else class="img-upload-label">
                      <span class="material-symbols-outlined">image</span>
                      <span>Image</span>
                      <input
                        type="file"
                        accept="image/*"
                        class="file-input"
                        @change="e => onImageChange(e, card)"
                      />
                    </label>
                    </div>
                </div>
    
                <!-- hint row: always visible below -->
                <div class="hint-row">
                    <span class="material-symbols-outlined hint-icon">lightbulb</span>
                    <input v-model="card.hint" class="hint-input" placeholder="Add a hint (optional)" @blur="autoSaveCard(card)" />
                </div>
            </div>
    
            <!-- new card form -->
            <div v-if="showAddForm" class="card-row card-row-new">
                <div class="row-header">
                    <span class="row-num">{{ localCards.length + 1 }}</span>
                    <button class="row-delete-btn" @click="showAddForm = false">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
                <div class="row-body">
                    <div class="input-col">
                        <textarea v-model="newCardForm.term" class="card-textarea" placeholder="Enter term" rows="1" ref="newTermInput" @input="autoResize"></textarea>
                        <span class="input-label">TERM</span>
                    </div>
                    <div class="input-col">
                        <textarea v-model="newCardForm.definition" class="card-textarea" placeholder="Enter definition" rows="1" @input="autoResize"></textarea>
                        <span class="input-label">DEFINITION</span>
                    </div>
                    <div class="input-col-img">
                        <div v-if="newCardForm.image_url" class="img-preview-wrap">
                            <img :src="newCardForm.image_url" class="img-preview" alt="preview" />
                            <button class="img-remove-btn" @click="newCardForm.image_url = ''">
                        <span class="material-symbols-outlined">close</span>
                      </button>
                        </div>
                        <label v-else class="img-upload-label">
                      <span class="material-symbols-outlined">image</span>
                      <span>Image</span>
                      <input type="file" accept="image/*" class="file-input" @change="onNewImageChange" />
                    </label>
                    </div>
                </div>
                <div class="hint-row">
                    <span class="material-symbols-outlined hint-icon">lightbulb</span>
                    <input v-model="newCardForm.hint" class="hint-input" placeholder="Add a hint (optional)" />
                </div>
                <!-- add button inside the new card row -->
                <div class="new-card-footer">
                    <button class="btn-add-confirm" :disabled="store.loading || !newCardForm.term.trim() || !newCardForm.definition.trim()" @click="addCard">
                    <span class="material-symbols-outlined">add</span>
                    Add card
                  </button>
                </div>
            </div>
    
        </div>
    
        <!-- hint: create set first -->
        <div v-else-if="!store.loading" class="save-first-hint">
            <span class="material-symbols-outlined">info</span> Fill in the title above and click <strong>Create</strong> to start adding cards.
        </div>
    
        <!-- add card button -->
        <button v-if="setReady" class="add-card-btn" @click="openAddCard">
              <span class="material-symbols-outlined">add</span>
              Add a card
            </button>
    
        <!-- delete confirm modal -->
        <div v-if="cardToDelete" class="modal-overlay" @click.self="cardToDelete = null">
            <div class="modal">
                <h3 class="modal-title">Delete this card?</h3>
                <p class="modal-body">"{{ cardToDelete.term }}"</p>
                <div class="modal-actions">
                    <button class="btn-cancel" @click="cardToDelete = null">Cancel</button>
                    <button class="btn-delete" :disabled="store.loading" @click="doDeleteCard">
                    {{ store.loading ? 'Deleting...' : 'Delete' }}
                  </button>
                </div>
            </div>
        </div>
    
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFlashcardStore } from '../store/flashcardStore'
import flashcardService from '../services/flashcardService'

const route = useRoute()
const router = useRouter()
const store = useFlashcardStore()

const routeSetId = computed(() => route.params.setId)
const courseId = computed(() => route.params.courseId ? parseInt(route.params.courseId, 10) : null)
const isEditMode = computed(() => !!routeSetId.value)
const createdSetId = ref(null)
const currentSetId = computed(() => routeSetId.value || createdSetId.value)
const setReady = computed(() => !!currentSetId.value)

// local copy of cards so inline edits don't go through store on every keystroke
const localCards = ref([])

const backLink = computed(() => ({
    name: 'TeacherFlashcardDashboard',
    params: { courseId: courseId.value }
}))

const setForm = ref({ title: '', description: '' })
const newCardForm = ref({ term: '', definition: '', hint: '', image_url: '' })
const showAddForm = ref(false)
const cardToDelete = ref(null)
const newTermInput = ref(null)

// sync localCards when store.currentSet.cards changes
watch(
    () => store.currentSet ?.cards,
    (cards) => {
        if (cards) {
            localCards.value = cards.map(c => ({ ...c }))
            resizeAll()
        }
    }, { immediate: true, flush: 'post' }
)

// upload image to supabase storage and return url
async function onImageChange(e, card) {
    const file = e.target.files[0]
    if (!file) return
    card.image_url = null // clear while uploading
    const url = await store.uploadImage(file)
    if (url) {
        card.image_url = url
        autoSaveCard(card)
    }
}

async function removeImage(card) {
    card.image_url = ''
    autoSaveCard(card)
}

async function onNewImageChange(e) {
    const file = e.target.files[0]
    if (!file) return
    const url = await store.uploadImage(file)
    if (url) newCardForm.value.image_url = url
}

// resize a textarea to fit its content
function autoResize(e) {
    const el = e.target
    el.style.height = 'auto'
    el.style.height = el.scrollHeight + 'px'
}

// resize all textareas already on screen (for loaded cards with existing text)
function resizeAll() {
    nextTick(() => {
        document.querySelectorAll('.card-textarea').forEach(el => {
            el.style.height = 'auto'
            el.style.height = el.scrollHeight + 'px'
        })
    })
}

async function autoSaveCard(card) {
    if (!card.term.trim() || !card.definition.trim()) return
    await store.updateCard(card.id, {
        term: card.term,
        definition: card.definition,
        hint: card.hint || undefined,
        image_url: card.image_url || undefined,
    })
}

async function loadSet() {
    store.loading = true
    store.error = null
    try {
        const res = await flashcardService.listSets(courseId.value)
        const found = res.data.find(s => String(s.id) === String(routeSetId.value))
        if (found) {
            setForm.value.title = found.title || ''
            setForm.value.description = found.description || ''
            const cardsRes = await flashcardService.getCards(routeSetId.value)
            store.currentSet = { ...found, cards: cardsRes.data }
        } else {
            store.error = 'set not found.'
        }
    } catch (err) {
        store.error = err ?.response ?.data ?.detail || err.message || 'failed to load'
    } finally {
        store.loading = false
    }
}

onMounted(async () => { if (isEditMode.value) await loadSet() })
watch(routeSetId, async (id) => { if (id) await loadSet() })
onUnmounted(() => { store.clearCurrent() })

async function saveSet() {
    if (!setForm.value.title.trim()) return
    const payload = { title: setForm.value.title, description: setForm.value.description || null }
    if (!isEditMode.value) {
        const created = await store.createSet({ course_id: courseId.value, ...payload })
        if (created) {
            createdSetId.value = created.id
            store.currentSet = { ...created, cards: [] }
            router.replace({ name: 'FlashcardEditor', params: { courseId: courseId.value, setId: created.id } })
            openAddCard()
        }
    } else {
        await store.updateSet(currentSetId.value, payload)
    }
}

async function saveAndStudy() {
    if (!setForm.value.title.trim()) return
    const created = await store.createSet({
        course_id: courseId.value,
        title: setForm.value.title,
        description: setForm.value.description || null
    })
    if (created) {
        router.push({ name: 'FlashcardStudy', params: { courseId: courseId.value, setId: created.id } })
    }
}

function openAddCard() {
    newCardForm.value = { term: '', definition: '', hint: '', image_url: '' }
    showAddForm.value = true
    nextTick(() => { newTermInput.value ?.focus() })
}

async function addCard() {
    const res = await store.addCard(parseInt(currentSetId.value), {
        term: newCardForm.value.term,
        definition: newCardForm.value.definition,
        hint: newCardForm.value.hint || undefined,
        image_url: newCardForm.value.image_url || undefined,
    })
    if (res) {
        newCardForm.value = { term: '', definition: '', hint: '', image_url: '' }
        showAddForm.value = false
    }
}

async function doDeleteCard() {
    if (!cardToDelete.value) return
    const ok = await store.deleteCard(cardToDelete.value.id)
    if (ok) cardToDelete.value = null
}
</script>

<style scoped>
.editor-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    padding-bottom: 5rem;
}

/* top bar */

.editor-topbar {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 2.5rem;
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--card-border);
    position: sticky;
    top: 0;
    z-index: 10;
}

.back-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    border-radius: 12px;
    background: var(--white);
    border: 1px solid var(--card-border);
    color: var(--text-main);
    text-decoration: none;
    flex-shrink: 0;
    transition: all 0.2s;
    box-shadow: var(--shadow-sm);
}

.back-btn:hover {
    background: var(--gray-light);
    transform: translateX(-2px);
}

.topbar-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-main);
    flex: 1;
}

.topbar-actions {
    display: flex;
    gap: 0.75rem;
    align-items: center;
}

.btn-light {
    padding: 0.55rem 1.4rem;
    border-radius: 99px;
    background: rgba(255, 255, 255, 0.8);
    border: 1.5px solid var(--card-border);
    color: var(--text-muted);
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
    box-shadow: var(--shadow-sm);
}

.btn-light:hover:not(:disabled) {
    background: var(--white);
    color: var(--text-main);
}

.btn-light:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.btn-primary-pill {
    padding: 0.55rem 1.4rem;
    border-radius: 99px;
    background: var(--primary-pink);
    border: none;
    color: white;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(237, 64, 130, 0.3);
}

.btn-primary-pill:hover:not(:disabled) {
    background: var(--primary-hover);
    box-shadow: 0 6px 16px rgba(237, 64, 130, 0.4);
    transform: translateY(-1px);
}

.btn-primary-pill:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

/* meta section */

.meta-section {
    padding: 2rem 2.5rem 1.5rem;
    max-width: 960px;
    width: 100%;
    margin: 0 auto;
}

.meta-card {
    background: var(--white);
    border-radius: var(--radius-lg);
    padding: 1.75rem 2rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--card-border);
    display: flex;
    gap: 0;
    align-items: stretch;
}

.meta-field {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
}

.meta-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--text-muted);
}

.meta-input {
    background: transparent;
    border: none;
    outline: none;
    color: var(--text-main);
    font-family: inherit;
    font-size: 1rem;
    font-weight: 500;
    padding: 0.5rem 0;
    border-bottom: 2px solid transparent;
    transition: border-color 0.2s;
    width: 100%;
}

.meta-input:focus {
    border-color: var(--primary-pink);
}

.meta-input::placeholder {
    color: #d1d5db;
}

.meta-divider {
    width: 1px;
    background: var(--card-border);
    margin: 0 2rem;
    flex-shrink: 0;
}

/* cards section */

.cards-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 0 2.5rem;
    max-width: 960px;
    width: 100%;
    margin: 0 auto;
}

/* card row */

.card-row {
    background: var(--white);
    border-radius: var(--radius-lg);
    border: 1.5px solid var(--card-border);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
    transition: box-shadow 0.2s, border-color 0.2s;
}

.card-row:focus-within {
    border-color: rgba(237, 64, 130, 0.4);
    box-shadow: 0 0 0 3px rgba(237, 64, 130, 0.08), var(--shadow-sm);
}

.card-row-new {
    border-color: rgba(237, 64, 130, 0.3);
    box-shadow: 0 0 0 3px rgba(237, 64, 130, 0.08), var(--shadow-sm);
}

/* row header: number + delete */

.row-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1.5rem 0;
}

.row-num {
    font-size: 0.78rem;
    font-weight: 800;
    color: var(--text-muted);
    letter-spacing: 0.05em;
}

.row-delete-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: transparent;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.15s;
}

.row-delete-btn:hover {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.08);
}

.row-delete-btn .material-symbols-outlined {
    font-size: 18px;
}

/* row body: term + definition + image side by side */

.row-body {
    display: grid;
    grid-template-columns: 1fr 1fr auto;
    gap: 1rem;
    padding: 0.75rem 1.5rem 0;
    align-items: start;
}

.input-col {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.input-col:last-of-type {
    border-right: none;
    margin-right: 0;
}

/* textarea box */

.card-textarea {
    background: var(--gray-light);
    border: 1.5px solid var(--card-border);
    border-radius: var(--radius-md);
    outline: none;
    color: var(--text-main);
    font-family: inherit;
    font-size: 0.95rem;
    font-weight: 500;
    padding: 0.75rem 1rem;
    width: 100%;
    resize: none;
    overflow: hidden;
    line-height: 1.5;
    transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
    min-height: 42px;
}

.card-textarea:focus {
    border-color: var(--primary-pink);
    background: var(--white);
    box-shadow: 0 0 0 3px rgba(237, 64, 130, 0.1);
}

.card-textarea::placeholder {
    color: #c0c4ce;
    font-weight: 400;
}

.input-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--text-muted);
}

/* image column */

.input-col-img {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 0;
}

.img-preview-wrap {
    position: relative;
}

.img-preview {
    width: 80px;
    height: 80px;
    object-fit: cover;
    border-radius: 10px;
    border: 1.5px solid var(--card-border);
    display: block;
}

.img-remove-btn {
    position: absolute;
    top: -6px;
    right: -6px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #ef4444;
    border: none;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    padding: 0;
}

.img-remove-btn .material-symbols-outlined {
    font-size: 13px;
}

.img-upload-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    border: 2px dashed rgba(237, 64, 130, 0.25);
    border-radius: 10px;
    color: var(--primary-pink);
    font-size: 0.65rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    gap: 3px;
    letter-spacing: 0.04em;
}

.img-upload-label:hover {
    border-color: var(--primary-pink);
    background: rgba(237, 64, 130, 0.04);
}

.img-upload-label .material-symbols-outlined {
    font-size: 24px;
}

.file-input {
    display: none;
}

/* hint row */

.hint-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 1.5rem 1rem;
    margin-top: 0.25rem;
    border-top: 1px dashed var(--card-border);
}

.hint-icon {
    font-size: 16px;
    color: #f59e0b;
    flex-shrink: 0;
}

.hint-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #92400e;
    font-family: inherit;
    font-size: 0.85rem;
    padding: 0.25rem 0;
}

.hint-input::placeholder {
    color: #d1d5db;
}

/* new card footer */

.new-card-footer {
    display: flex;
    justify-content: flex-end;
    padding: 0.75rem 1.5rem 1rem;
    border-top: 1px solid var(--card-border);
    background: var(--gray-light);
}

.btn-add-confirm {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0.6rem 1.4rem;
    border-radius: 99px;
    background: var(--primary-pink);
    border: none;
    color: white;
    font-size: 0.875rem;
    font-weight: 700;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(237, 64, 130, 0.25);
}

.btn-add-confirm:hover:not(:disabled) {
    background: var(--primary-hover);
    transform: translateY(-1px);
}

.btn-add-confirm:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.btn-add-confirm .material-symbols-outlined {
    font-size: 18px;
}

/* save first hint */

.save-first-hint {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 1.25rem;
    margin: 1rem 2.5rem;
    max-width: 912px;
    background: rgba(237, 64, 130, 0.04);
    border: 1px dashed rgba(237, 64, 130, 0.2);
    border-radius: var(--radius-md);
    color: var(--text-muted);
    font-size: 0.875rem;
}

.save-first-hint .material-symbols-outlined {
    color: var(--primary-pink);
    font-size: 18px;
}

/* add card button */

.add-card-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    width: calc(100% - 5rem);
    max-width: 912px;
    margin: 1rem auto 0;
    padding: 1.2rem;
    border: 2px dashed rgba(237, 64, 130, 0.2);
    border-radius: var(--radius-lg);
    background: rgba(255, 255, 255, 0.5);
    color: var(--text-muted);
    font-size: 0.95rem;
    font-weight: 700;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
    backdrop-filter: blur(6px);
}

.add-card-btn:hover {
    border-color: var(--primary-pink);
    color: var(--primary-pink);
    background: rgba(237, 64, 130, 0.04);
}

.add-card-btn .material-symbols-outlined {
    font-size: 22px;
}

/* modal */

.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 300;
}

.modal {
    background: var(--white);
    border-radius: var(--radius-lg);
    padding: 2rem;
    max-width: 400px;
    width: 90%;
    box-shadow: var(--shadow-md);
}

.modal-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 0.5rem;
}

.modal-body {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-bottom: 1.5rem;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
}

.btn-cancel {
    padding: 0.55rem 1.25rem;
    border-radius: 99px;
    background: transparent;
    border: 1.5px solid var(--card-border);
    color: var(--text-muted);
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
    transition: background 0.15s;
}

.btn-cancel:hover {
    background: var(--gray-light);
}

.btn-delete {
    padding: 0.55rem 1.25rem;
    border-radius: 99px;
    background: #ef4444;
    border: none;
    color: white;
    font-weight: 700;
    font-size: 0.875rem;
    cursor: pointer;
    font-family: inherit;
    transition: background 0.15s;
}

.btn-delete:hover:not(:disabled) {
    background: #dc2626;
}

.btn-delete:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

@media (max-width: 700px) {
    .editor-topbar {
        padding: 0.75rem 1rem;
    }
    .meta-section {
        padding: 1rem;
    }
    .meta-card {
        flex-direction: column;
        gap: 1rem;
    }
    .meta-divider {
        width: 100%;
        height: 1px;
        margin: 0;
    }
    .cards-section {
        padding: 0 1rem;
    }
    .row-body {
        grid-template-columns: 1fr;
        gap: 0.75rem;
    }
    .input-col-img {
        display: none;
    }
    .add-card-btn {
        width: calc(100% - 2rem);
    }
}
</style>