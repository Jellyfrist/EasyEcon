<template>
    <div class="editor-page">
    
        <!-- breadcrumb -->
        <div class="breadcrumb-bar">
            <router-link :to="backLink" class="breadcrumb-link">Dashboard</router-link>
            <span class="material-symbols-outlined breadcrumb-sep">chevron_right</span>
            <span class="breadcrumb-current">Flashcard Creator</span>
        </div>
    
        <!-- loading -->
        <div v-if="store.loading && !setReady" class="state-box">
            <div class="spinner"></div>
            <p>Loading...</p>
        </div>
    
        <template v-else>
          <div class="editor-layout">
    
            <!-- left: main content -->
            <div class="editor-main">
    
              <!-- set metadata -->
              <div class="panel">
                <div class="panel-grid">
                  <div class="form-group">
                    <label class="field-label">Set Title</label>
                    <input
                      v-model="setForm.title"
                      class="input-field"
                      placeholder="e.g. Chapter 4: Supply and Demand"
                      maxlength="100"
                    />
                  </div>
                  <div class="form-group">
                    <label class="field-label">Description</label>
                    <input
                      v-model="setForm.description"
                      class="input-field"
                      placeholder="Short description (optional)"
                      maxlength="300"
                    />
                  </div>
                </div>
              </div>
    
              <!-- cards section: only show after set is saved -->
              <div v-if="setReady" class="cards-section">
    
                <div class="cards-header">
                  <h2 class="cards-title">
                    <span class="material-symbols-outlined">layers</span>
                    Cards in Set ({{ cards.length }})
                  </h2>
                  <button
                    v-if="cards.length > 0"
                    class="text-action text-action-danger"
                    @click="showClearConfirm = true"
                  >
                    <span class="material-symbols-outlined">delete_sweep</span>
                    Clear All
                  </button>
                </div>
    
                <p v-if="store.error" class="error-msg">{{ store.error }}</p>
    
                <!-- empty state -->
                <div v-if="cards.length === 0 && !showAddForm" class="empty-cards">
                  <span class="material-symbols-outlined">layers_clear</span>
                  <p>No cards yet. Click "Add New Card" below to start.</p>
                </div>
    
                <!-- card rows -->
                <div class="cards-list">
                  <div
                    v-for="(card, idx) in cards"
                    :key="card.id"
                    class="card-row"
                    :class="{ 'card-row-active': editingCardId === card.id }"
                  >
                    <span class="row-num" :class="{ 'row-num-active': editingCardId === card.id }">
                      {{ String(idx + 1).padStart(2, '0') }}
                    </span>
    
                    <!-- view mode -->
                    <template v-if="editingCardId !== card.id">
                      <div class="card-fields">
                        <div class="card-col">
                          <span class="col-label">Term (Front)</span>
                          <p class="term-text">{{ card.term }}</p>
                        </div>
                        <div class="card-col">
                          <span class="col-label">Definition (Back)</span>
                          <p class="def-text">{{ card.definition }}</p>
                          <p v-if="card.hint" class="hint-text">
                            <span class="material-symbols-outlined">lightbulb</span>
                            {{ card.hint }}
                          </p>
                        </div>
                        <!-- image preview -->
                        <div v-if="card.image_url" class="card-col card-col-img">
                          <span class="col-label">Image</span>
                          <img :src="card.image_url" class="card-img-preview" alt="card image" />
                        </div>
                      </div>
                      <div class="row-actions">
                        <button class="row-btn" title="edit" @click="startEdit(card)">
                          <span class="material-symbols-outlined">edit</span>
                        </button>
                        <button class="row-btn row-btn-delete" title="delete" @click="cardToDelete = card">
                          <span class="material-symbols-outlined">remove_circle_outline</span>
                        </button>
                      </div>
</template>

                <!-- inline edit mode -->
<template v-else>
    <div class="inline-edit">
        <div class="card-fields">
            <div class="card-col">
                <span class="col-label col-label-active">Term (Front)</span>
                <textarea v-model="cardForm.term" class="inline-textarea" placeholder="Enter term..." rows="2"></textarea>
            </div>
            <div class="card-col">
                <span class="col-label">Definition (Back)</span>
                <textarea v-model="cardForm.definition" class="inline-textarea" placeholder="Enter definition..." rows="2"></textarea>
                <input v-model="cardForm.hint" class="hint-input" placeholder="Hint (optional)" />
            </div>
        </div>
        <!-- image upload for edit -->
        <div class="image-upload-row">
            <span class="col-label">Image (optional)</span>
            <div class="image-upload-area">
                <img v-if="cardForm.image_url" :src="cardForm.image_url" class="card-img-preview" alt="preview" />
                <label class="upload-btn">
                              <span class="material-symbols-outlined">upload</span>
                              {{ cardForm.image_url ? 'Change Image' : 'Upload Image' }}
                              <input type="file" accept="image/*" class="file-input" @change="onEditImageChange" />
                            </label>
                <button v-if="cardForm.image_url" class="remove-img-btn" @click="cardForm.image_url = ''">
                              <span class="material-symbols-outlined">close</span> Remove
                            </button>
            </div>
        </div>
        <div class="inline-edit-btns">
            <button class="btn btn-outline btn-sm" @click="cancelEdit">Cancel</button>
            <button class="btn btn-green btn-sm" :disabled="store.loading || !cardForm.term.trim() || !cardForm.definition.trim()" @click="saveCard">
                            Save
                          </button>
        </div>
    </div>
</template>

              </div>
            </div>

            <!-- add new card inline form -->
            <div v-if="showAddForm" class="card-row card-row-new">
              <span class="row-num row-num-active">{{ String(cards.length + 1).padStart(2, '0') }}</span>
              <div class="inline-edit">
                <div class="card-fields">
                  <div class="card-col">
                    <span class="col-label col-label-active">Term (Front)</span>
                    <textarea v-model="newCardForm.term" class="inline-textarea" placeholder="Type term here..." rows="2"></textarea>
                  </div>
                  <div class="card-col">
                    <span class="col-label">Definition (Back)</span>
                    <textarea v-model="newCardForm.definition" class="inline-textarea" placeholder="Type definition here..." rows="2"></textarea>
                    <input v-model="newCardForm.hint" class="hint-input" placeholder="Hint (optional)" />
                  </div>
                </div>
                <!-- image upload for new card -->
                <div class="image-upload-row">
                  <span class="col-label">Image (optional)</span>
                  <div class="image-upload-area">
                    <img v-if="newCardForm.image_url" :src="newCardForm.image_url" class="card-img-preview" alt="preview" />
                    <label class="upload-btn">
                      <span class="material-symbols-outlined">upload</span>
                      {{ newCardForm.image_url ? 'Change Image' : 'Upload Image' }}
                      <input type="file" accept="image/*" class="file-input" @change="onNewImageChange" />
                    </label>
                    <button v-if="newCardForm.image_url" class="remove-img-btn" @click="newCardForm.image_url = ''">
                      <span class="material-symbols-outlined">close</span> Remove
                    </button>
                  </div>
                </div>
                <div class="inline-edit-btns">
                  <button class="btn btn-outline btn-sm" @click="showAddForm = false">Cancel</button>
                  <button
                    class="btn btn-primary btn-sm"
                    :disabled="store.loading || !newCardForm.term.trim() || !newCardForm.definition.trim()"
                    @click="addCard"
                  >
                    <span class="material-symbols-outlined">add</span>
                    Add
                  </button>
                </div>
              </div>
            </div>

            <!-- single add card button at the bottom (dashed) -->
            <button class="add-card-btn" @click="openAddCard">
              <div class="add-card-icon">
                <span class="material-symbols-outlined">add</span>
              </div>
              <span class="add-card-label">Add New Card</span>
            </button>

          </div>

          <!-- hint to save set first -->
          <div v-else-if="!store.loading" class="save-first-hint">
            <span class="material-symbols-outlined">info</span>
            <p>Save the set details first to start adding cards.</p>
          </div>

        </div>

        <!-- right: sidebar -->
        <aside class="editor-sidebar">
          <div class="sidebar-panel">

            <h3 class="sidebar-title">
              <span class="material-symbols-outlined">analytics</span>
              Set Overview
            </h3>

            <div class="overview-stats">
              <div class="stat-row">
                <span class="stat-label">Total Cards</span>
                <span class="stat-value">{{ cards.length }}</span>
              </div>
            </div>

            <div class="sidebar-actions">
              <button
                class="btn btn-primary sidebar-btn"
                :disabled="store.loading || !setForm.title.trim()"
                @click="saveSet"
              >
                <span class="material-symbols-outlined">{{ isEditMode ? 'save' : 'add_circle' }}</span>
                {{ store.loading ? 'Saving...' : isEditMode ? 'Save Changes' : 'Create Set' }}
              </button>
            </div>

            <p class="autosave-note">
              <span class="material-symbols-outlined">cloud_done</span>
              {{ setReady ? 'Set saved' : 'Not saved yet' }}
            </p>

          </div>
        </aside>

      </div>
    </template>

    <!-- delete card modal -->
    <div v-if="cardToDelete" class="modal-overlay" @click.self="cardToDelete = null">
      <div class="modal">
        <h3 class="modal-title">Delete this card?</h3>
        <p class="modal-body">"{{ cardToDelete.term }}"</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="cardToDelete = null">Cancel</button>
          <button class="btn btn-danger" :disabled="store.loading" @click="doDeleteCard">
            {{ store.loading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>

    <!-- clear all modal -->
    <div v-if="showClearConfirm" class="modal-overlay" @click.self="showClearConfirm = false">
      <div class="modal">
        <h3 class="modal-title">Clear all cards?</h3>
        <p class="modal-body">This will delete all {{ cards.length }} cards. This cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showClearConfirm = false">Cancel</button>
          <button class="btn btn-danger" :disabled="store.loading" @click="doClearAll">
            {{ store.loading ? 'Clearing...' : 'Clear All' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
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
const cards = computed(() => store.currentSet ?.cards ?? [])

const backLink = computed(() => ({
    name: 'TeacherFlashcardDashboard',
    params: { courseId: courseId.value }
}))

const setForm = ref({ title: '', description: '' })
const cardForm = ref({ term: '', definition: '', hint: '', image_url: '' })
const editingCardId = ref(null)
const newCardForm = ref({ term: '', definition: '', hint: '', image_url: '' })
const showAddForm = ref(false)
const cardToDelete = ref(null)
const showClearConfirm = ref(false)

// convert file to base64 string and store in image_url
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result)
        reader.onerror = reject
        reader.readAsDataURL(file)
    })
}

async function onNewImageChange(e) {
    const file = e.target.files[0]
    if (!file) return
    newCardForm.value.image_url = await fileToBase64(file)
}

async function onEditImageChange(e) {
    const file = e.target.files[0]
    if (!file) return
    cardForm.value.image_url = await fileToBase64(file)
}

// load set metadata and cards on mount (edit mode only)
async function loadSet() {
    store.loading = true
    store.error = null
    try {
        // get set metadata from teacher list endpoint
        const res = await flashcardService.listSets(courseId.value)
        const found = res.data.find(s => String(s.id) === String(routeSetId.value))
        if (found) {
            setForm.value.title = found.title || ''
            setForm.value.description = found.description || ''
            // get actual cards from teacher card-list endpoint
            // GET /flashcards/sets/:setId/cards (require_teacher)
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

onMounted(async () => {
    if (isEditMode.value) await loadSet()
})

// watch for route change after create redirect
watch(routeSetId, async (newId) => {
    if (newId) await loadSet()
})

onUnmounted(() => {
    store.clearCurrent()
})

// save set: create or update
async function saveSet() {
    if (!setForm.value.title.trim()) return
    const payload = {
        title: setForm.value.title,
        description: setForm.value.description || null,
    }
    if (!isEditMode.value) {
        const created = await store.createSet({ course_id: courseId.value, ...payload })
        if (created) {
            createdSetId.value = created.id
            store.currentSet = { ...created, cards: [] }
            router.replace({
                name: 'FlashcardEditor',
                params: { courseId: courseId.value, setId: created.id },
            })
            openAddCard()
        }
    } else {
        await store.updateSet(currentSetId.value, payload)
    }
}

// open add card form (close edit form if open)
function openAddCard() {
    newCardForm.value = { term: '', definition: '', hint: '', image_url: '' }
    showAddForm.value = true
    editingCardId.value = null
}

// add card: POST /flashcards/sets/:setId/cards
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

function startEdit(card) {
    editingCardId.value = card.id
    cardForm.value = {
        term: card.term,
        definition: card.definition,
        hint: card.hint || '',
        image_url: card.image_url || '',
    }
    showAddForm.value = false
}

function cancelEdit() {
    editingCardId.value = null
}

// save edited card: PATCH /flashcards/cards/:cardId
async function saveCard() {
    const ok = await store.updateCard(editingCardId.value, {
        term: cardForm.value.term,
        definition: cardForm.value.definition,
        hint: cardForm.value.hint || undefined,
        image_url: cardForm.value.image_url || undefined,
    })
    if (ok) editingCardId.value = null
}

async function doDeleteCard() {
    if (!cardToDelete.value) return
    const ok = await store.deleteCard(cardToDelete.value.id)
    if (ok) cardToDelete.value = null
}

async function doClearAll() {
    for (const card of [...cards.value]) {
        await store.deleteCard(card.id)
    }
    showClearConfirm.value = false
}
</script>

<style scoped>
.editor-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1.5rem 1.5rem 5rem;
}

.breadcrumb-bar {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-bottom: 1.5rem;
}

.breadcrumb-link {
    color: var(--text-muted);
    text-decoration: none;
    transition: color 0.15s;
}

.breadcrumb-link:hover {
    color: var(--primary-pink);
}

.breadcrumb-sep {
    font-size: 16px;
    opacity: 0.5;
}

.breadcrumb-current {
    font-weight: 600;
    color: var(--primary-pink);
}

.editor-layout {
    display: flex;
    gap: 2rem;
    align-items: flex-start;
}

.editor-main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.editor-sidebar {
    width: 280px;
    flex-shrink: 0;
    position: sticky;
    top: 5rem;
}

.panel {
    background: var(--white);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
}

.panel-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
}

.field-label {
    display: block;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
}

.cards-section {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.cards-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 4px;
}

.cards-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-main);
}

.cards-title .material-symbols-outlined {
    color: var(--primary-pink);
    font-size: 22px;
}

.text-action {
    display: flex;
    align-items: center;
    gap: 4px;
    background: none;
    border: none;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--primary-pink);
    cursor: pointer;
    font-family: inherit;
    padding: 0;
    transition: opacity 0.15s;
}

.text-action:hover {
    opacity: 0.75;
}

.text-action .material-symbols-outlined {
    font-size: 17px;
}

.text-action-danger {
    color: var(--text-muted);
    transition: color 0.15s;
}

.text-action-danger:hover {
    color: #ef4444;
    opacity: 1;
}

.card-row {
    background: var(--white);
    border: 1px solid transparent;
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    transition: border-color 0.15s;
}

.card-row:hover {
    border-color: rgba(237, 64, 130, 0.3);
}

.card-row-active {
    border-color: var(--primary-pink) !important;
}

.card-row-new {
    border-color: rgba(237, 64, 130, 0.25) !important;
}

.row-num {
    font-size: 0.75rem;
    font-weight: 700;
    color: rgba(237, 64, 130, 0.35);
    min-width: 24px;
    padding-top: 4px;
}

.row-num-active {
    color: var(--primary-pink);
}

.card-fields {
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    min-width: 0;
}

.card-col {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.card-col-img {
    grid-column: span 2;
}

.col-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
}

.col-label-active {
    color: var(--primary-pink);
}

.term-text {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-main);
    margin: 0;
}

.def-text {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin: 0;
}

.hint-text {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.78rem;
    color: #ca8a04;
    margin: 4px 0 0;
}

.hint-text .material-symbols-outlined {
    font-size: 14px;
}

/* image */

.card-img-preview {
    max-width: 120px;
    max-height: 80px;
    border-radius: 8px;
    object-fit: cover;
    border: 1px solid var(--card-border);
}

.image-upload-row {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-top: 4px;
}

.image-upload-area {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.upload-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--primary-pink);
    cursor: pointer;
    padding: 6px 12px;
    border: 1px dashed rgba(237, 64, 130, 0.4);
    border-radius: 8px;
    transition: background 0.15s;
}

.upload-btn:hover {
    background: rgba(237, 64, 130, 0.05);
}

.upload-btn .material-symbols-outlined {
    font-size: 16px;
}

.file-input {
    display: none;
}

.remove-img-btn {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    font-size: 0.75rem;
    color: #ef4444;
    background: none;
    border: none;
    cursor: pointer;
    font-family: inherit;
    padding: 0;
}

.remove-img-btn .material-symbols-outlined {
    font-size: 14px;
}

.inline-edit {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.inline-textarea {
    width: 100%;
    background: transparent;
    border: none;
    outline: none;
    font-family: inherit;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-main);
    resize: none;
    line-height: 1.5;
    padding: 0;
}

.inline-textarea::placeholder {
    color: #d1d5db;
}

.hint-input {
    background: transparent;
    border: none;
    border-bottom: 1px dashed var(--card-border);
    outline: none;
    font-family: inherit;
    font-size: 0.8rem;
    color: var(--text-muted);
    padding: 4px 0;
    width: 100%;
}

.hint-input:focus {
    border-color: var(--primary-pink);
}

.hint-input::placeholder {
    color: #d1d5db;
}

.inline-edit-btns {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
}

.row-actions {
    display: flex;
    gap: 2px;
    flex-shrink: 0;
}

.row-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: none;
    border-radius: 8px;
    padding: 6px;
    cursor: pointer;
    color: #d1d5db;
    transition: color 0.15s;
}

.row-btn:hover {
    color: var(--text-muted);
}

.row-btn-delete:hover {
    color: #ef4444;
}

.row-btn .material-symbols-outlined {
    font-size: 20px;
}

/* single add card button at bottom */

.add-card-btn {
    width: 100%;
    padding: 1.5rem;
    border: 2px dashed rgba(237, 64, 130, 0.2);
    border-radius: var(--radius-lg);
    background: none;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    transition: border-color 0.2s, background 0.2s;
    font-family: inherit;
}

.add-card-btn:hover {
    border-color: var(--primary-pink);
    background: rgba(237, 64, 130, 0.03);
}

.add-card-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(237, 64, 130, 0.1);
    color: var(--primary-pink);
    display: flex;
    align-items: center;
    justify-content: center;
}

.add-card-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--primary-pink);
}

.save-first-hint {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 1.25rem;
    background: rgba(237, 64, 130, 0.05);
    border: 1px dashed rgba(237, 64, 130, 0.2);
    border-radius: var(--radius-md);
    color: var(--text-muted);
    font-size: 0.875rem;
}

.save-first-hint .material-symbols-outlined {
    color: var(--primary-pink);
    font-size: 20px;
}

.empty-cards {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 2.5rem 1rem;
    color: var(--text-muted);
    text-align: center;
}

.empty-cards .material-symbols-outlined {
    font-size: 36px;
    opacity: 0.3;
}

.sidebar-panel {
    background: var(--white);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.sidebar-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-main);
}

.sidebar-title .material-symbols-outlined {
    color: var(--primary-pink);
    font-size: 22px;
}

.overview-stats {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.875rem;
}

.stat-label {
    color: var(--text-muted);
}

.stat-value {
    font-weight: 600;
    color: var(--text-main);
}

.sidebar-actions {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
}

.sidebar-btn {
    width: 100%;
    justify-content: center;
    gap: 6px;
}

.sidebar-btn .material-symbols-outlined {
    font-size: 18px;
}

.autosave-note {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    font-size: 0.72rem;
    color: var(--text-muted);
}

.autosave-note .material-symbols-outlined {
    font-size: 14px;
    color: #22c55e;
}

.state-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 4rem;
    color: var(--text-muted);
}

.spinner {
    width: 36px;
    height: 36px;
    border: 3px solid #e5e7eb;
    border-top-color: var(--primary-pink);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.error-msg {
    font-size: 0.875rem;
    color: #ef4444;
    padding: 0 4px;
}

.btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
}

.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.35);
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

.btn-danger {
    background: #ef4444;
    color: white;
    padding: 0.65rem 1.25rem;
    border-radius: var(--radius-md);
    font-weight: 700;
    border: none;
    cursor: pointer;
    font-family: inherit;
}

.btn-danger:hover:not(:disabled) {
    background: #dc2626;
}

.btn-danger:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

@media (max-width: 900px) {
    .editor-layout {
        flex-direction: column;
    }
    .editor-sidebar {
        width: 100%;
        position: static;
    }
    .panel-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 600px) {
    .editor-page {
        padding: 1rem 1rem 3rem;
    }
    .card-fields {
        grid-template-columns: 1fr;
    }
}
</style>