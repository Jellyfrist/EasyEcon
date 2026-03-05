<template>
    <div class="teacher-fc-page">
    
        <div class="page-header">
            <div class="header-left">
                <router-link :to="{ name: 'CourseEditor', params: { courseId } }" class="back-link">
                    <span class="material-symbols-outlined">arrow_back</span> Back to Course
                </router-link>
                <h1 class="page-title">Flashcard Sets</h1>
            </div>
            <button class="btn btn-primary" @click="goToEditor()">
            <span class="material-symbols-outlined">add</span>
            New Set
          </button>
        </div>
    
        <!-- loading -->
        <div v-if="store.loading" class="state-box">
            <div class="spinner"></div>
            <p>Loading sets...</p>
        </div>
    
        <!-- error -->
        <p v-else-if="store.error" class="error-msg">{{ store.error }}</p>
    
        <!-- empty -->
        <div v-else-if="store.sets.length === 0" class="empty-state">
            <span class="material-symbols-outlined">layers_clear</span>
            <p>No flashcard sets yet.</p>
            <button class="btn btn-primary" @click="goToEditor()">Create First Set</button>
        </div>
    
        <!-- sets grid -->
        <div v-else class="sets-grid">
            <div v-for="set in store.sets" :key="set.id" class="set-card">
    
                <div class="set-card-top">
                    <span class="material-symbols-outlined set-icon">layers</span>
                    <span class="card-count-badge">{{ set.card_count ?? 0 }} cards</span>
                </div>
    
                <h3 class="set-title">{{ set.title }}</h3>
                <p class="set-desc">{{ set.description || 'No description' }}</p>
    
                <div class="set-actions">
                    <button class="btn btn-outline btn-sm" @click="goToEditor(set.id)">
                <span class="material-symbols-outlined">edit</span>
                Edit
              </button>
                    <button class="btn btn-danger-outline btn-sm" @click="confirmDelete(set)">
                <span class="material-symbols-outlined">delete</span>
                Delete
              </button>
                </div>
    
            </div>
        </div>
    
        <!-- delete confirm modal -->
        <div v-if="setToDelete" class="modal-overlay" @click.self="setToDelete = null">
            <div class="modal">
                <h3 class="modal-title">Delete "{{ setToDelete.title }}"?</h3>
                <p class="modal-body">This will also delete all cards in this set. This cannot be undone.</p>
                <div class="modal-actions">
                    <button class="btn btn-outline" @click="setToDelete = null">Cancel</button>
                    <button class="btn btn-danger" :disabled="store.loading" @click="doDelete">
                {{ store.loading ? 'Deleting...' : 'Delete' }}
              </button>
                </div>
            </div>
        </div>
    
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFlashcardStore } from '../store/flashcardStore'

const route = useRoute()
const router = useRouter()
const store = useFlashcardStore()

const courseId = computed(() => parseInt(route.params.courseId, 10))

function goToEditor(setId) {
    router.push({
        name: 'FlashcardEditor',
        params: { courseId: courseId.value, setId }
    })
}

const setToDelete = ref(null)

function confirmDelete(set) {
    setToDelete.value = set
}

async function doDelete() {
    if (!setToDelete.value) return
    const ok = await store.deleteSet(setToDelete.value.id)
    if (ok) setToDelete.value = null
}

onMounted(() => {
    store.sets = []
    if (courseId.value) store.fetchSets(courseId.value)
})
</script>

<style scoped>
.teacher-fc-page {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem 1.5rem 5rem;
}

.page-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 2rem;
    gap: 1rem;
}

.header-left {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.back-link {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.85rem;
    color: var(--text-muted);
    text-decoration: none;
    transition: color 0.15s;
}

.back-link:hover {
    color: var(--primary-pink);
}

.back-link .material-symbols-outlined {
    font-size: 16px;
}

.page-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text-main);
    margin: 0;
}

.sets-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.25rem;
}

.set-card {
    background: var(--white);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    transition: box-shadow 0.2s, border-color 0.2s;
}

.set-card:hover {
    box-shadow: var(--shadow-md);
    border-color: rgba(237, 64, 130, 0.25);
}

.set-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.25rem;
}

.set-icon {
    color: var(--primary-pink);
    font-size: 28px;
}

.card-count-badge {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--primary-pink);
    background: rgba(237, 64, 130, 0.08);
    padding: 3px 10px;
    border-radius: 999px;
}

.set-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-main);
    margin: 0;
}

.set-desc {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin: 0;
    flex: 1;
}

.set-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
}

.btn-danger-outline {
    background: none;
    border: 1px solid #fca5a5;
    color: #ef4444;
    padding: 0.5rem 1rem;
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: background 0.15s;
}

.btn-danger-outline:hover {
    background: #fef2f2;
}

.btn-danger-outline .material-symbols-outlined {
    font-size: 16px;
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

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 5rem 2rem;
    color: var(--text-muted);
    text-align: center;
}

.empty-state .material-symbols-outlined {
    font-size: 48px;
    opacity: 0.3;
}

.error-msg {
    color: #ef4444;
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
    margin: 0 0 0.5rem;
}

.modal-body {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin: 0 0 1.5rem;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
}

@media (max-width: 600px) {
    .teacher-fc-page {
        padding: 1rem 1rem 3rem;
    }
    .page-header {
        flex-direction: column;
        align-items: flex-start;
    }
    .sets-grid {
        grid-template-columns: 1fr;
    }
}
</style>