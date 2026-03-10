<template>
    <div class="tfd-page">
    
        <!-- page header -->
        <div class="tfd-page-header">
            <div class="tfd-breadcrumb">

                <router-link :to="{ name: 'Teacher' }" class="tfd-crumb-link">Dashboard</router-link>
                <span class="tfd-sep">/</span>

                <router-link :to="{ name: 'CoursesEditor', params: { courseId } }" class="tfd-crumb-link">Edit Course</router-link>
                <span class="tfd-sep">/</span>

                <span class="tfd-crumb-current">Flashcard Sets</span>
            </div>
            <div class="tfd-title-row">
                <div>
                    <h1 class="tfd-page-title">Flashcard Sets</h1>
                    <p class="tfd-page-sub">Manage and organise your flashcard sets for this course.</p>
                </div>
                <button class="tfd-btn tfd-btn-primary" @click="goToEditor()">
                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                            <path d="M7 1.5V12.5M1.5 7H12.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        New Set
                    </button>
            </div>
        </div>
    
        <!-- loading -->
        <div v-if="store.loading" class="tfd-state-box">
            <div class="tfd-spinner"></div>
            <p>Loading sets...</p>
        </div>
    
        <!-- error -->
        <div v-else-if="store.error" class="tfd-state-card">
            <div class="tfd-state-icon tfd-icon-red">
                <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                        <circle cx="11" cy="11" r="9" stroke="currentColor" stroke-width="1.75"/>
                        <path d="M11 7V11.5M11 14.5V15" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>
                    </svg>
            </div>
            <p class="tfd-state-msg">{{ store.error }}</p>
        </div>
    
        <!-- empty -->
        <div v-else-if="store.sets.length === 0" class="tfd-state-card">
            <div class="tfd-state-icon tfd-icon-neutral">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <rect x="2" y="6" width="15" height="11" rx="2.5" stroke="currentColor" stroke-width="1.75"/>
                        <rect x="7" y="3" width="15" height="11" rx="2.5" stroke="currentColor" stroke-width="1.75"/>
                    </svg>
            </div>
            <h3 class="tfd-state-title">No flashcard sets yet</h3>
            <p class="tfd-state-msg">Create your first set to start adding cards.</p>
            <button class="tfd-btn tfd-btn-primary" @click="goToEditor()">Create First Set</button>
        </div>
    
        <!-- sets grid -->
        <div v-else class="tfd-grid">
            <div v-for="(set, index) in store.sets" :key="set.id" class="tfd-card">
                <!-- colored top stripe -->
                <div class="tfd-card-stripe" :style="{ background: stripeColors[index % stripeColors.length] }"></div>
    
                <div class="tfd-card-body" @click="goToStudy(set.id)" style="cursor:pointer">
                    <div class="tfd-card-top">
                        <span class="tfd-count-pill">{{ set.card_count ?? 0 }} cards</span>
                    </div>
    
                    <h3 class="tfd-set-title">{{ set.title }}</h3>
                    <p class="tfd-set-desc">{{ set.description || 'No description provided.' }}</p>
    
                    <div class="tfd-card-actions">
                        <button class="tfd-btn tfd-btn-edit" @click.stop="goToEditor(set.id)">
                                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                                    <path d="M9.5 1.5L11.5 3.5L4.5 10.5H2.5V8.5L9.5 1.5Z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
                                </svg>
                                Edit
                            </button>
                        <button class="tfd-btn tfd-btn-delete" @click.stop="confirmDelete(set)">
                                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                                    <path d="M2 3.5H11M4.5 3.5V2.5C4.5 2 4.9 1.5 5.5 1.5H7.5C8.1 1.5 8.5 2 8.5 2.5V3.5M5.5 6V9.5M7.5 6V9.5M3 3.5L3.5 11C3.5 11.3 3.8 11.5 4 11.5H9C9.3 11.5 9.5 11.3 9.5 11L10 3.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                                Delete
                            </button>
                    </div>
                </div>
            </div>
        </div>
    
        <!-- delete confirm modal -->
        <Transition name="tfd-fade">
            <div v-if="setToDelete" class="tfd-overlay" @click.self="setToDelete = null">
                <div class="tfd-modal">
                    <div class="tfd-modal-icon">
                        <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                                <path d="M11 3L20 19H2L11 3Z" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/>
                                <path d="M11 9V13M11 15.5V16.5" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/>
                            </svg>
                    </div>
                    <h3 class="tfd-modal-title">Delete "{{ setToDelete.title }}"?</h3>
                    <p class="tfd-modal-body">All cards in this set will also be deleted. This cannot be undone.</p>
                    <div class="tfd-modal-actions">
                        <button class="tfd-btn tfd-btn-ghost" @click="setToDelete = null">Cancel</button>
                        <button class="tfd-btn tfd-btn-danger" :disabled="store.loading" @click="doDelete">
                                {{ store.loading ? 'Deleting...' : 'Delete Set' }}
                            </button>
                    </div>
                </div>
            </div>
        </Transition>
    
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

// accent stripe colors cycling per card
const stripeColors = [
    '#ed4081', '#f59e0b', '#22c55e',
    '#ec4899', '#14b8a6', '#f97316',
    '#8b5cf6', '#06b6d4',
]

function goToEditor(setId) {
    router.push({
        name: 'FlashcardEditor',
        params: { courseId: courseId.value, setId }
    })
}

function goToStudy(setId) {
    router.push({
        name: 'FlashcardStudy',
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
/* ---- page shell ---- */

.tfd-page {
    min-height: 100vh;
    background: #f8f9fb;
    padding: 2rem 3rem 4rem;
    font-family: 'DM Sans', 'Helvetica Neue', sans-serif;
    box-sizing: border-box;
}

/* ---- page header ---- */

.tfd-page-header {
    margin-bottom: 2rem;
}

.tfd-breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    font-size: 0.8rem;
    color: #94a3b8;
}

.tfd-crumb-link {
    background: none;
    border: none;
    color: #64748b;
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    padding: 0;
    text-decoration: none;
    transition: color 0.15s;
    font-family: inherit;
}

.tfd-crumb-link:hover {
    color: #ed4081;
}

.tfd-sep {
    color: #cbd5e1;
}

.tfd-crumb-current {
    color: #475569;
    font-weight: 500;
}

.tfd-title-row {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
}

.tfd-page-title {
    font-size: 1.65rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin: 0 0 0.3rem;
}

.tfd-page-sub {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0;
}

/* ---- state boxes ---- */

.tfd-state-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 4rem;
    color: #94a3b8;
    font-size: 0.875rem;
}

.tfd-spinner {
    width: 32px;
    height: 32px;
    border: 2.5px solid #e2e8f0;
    border-top-color: #ed4081;
    border-radius: 50%;
    animation: tfd-spin 0.7s linear infinite;
}

@keyframes tfd-spin {
    to {
        transform: rotate(360deg);
    }
}

.tfd-state-card {
    background: #ffffff;
    border: 1px solid #e8edf3;
    border-radius: 16px;
    padding: 3.5rem 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.tfd-state-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.25rem;
}

.tfd-icon-red {
    background: #fff1f2;
    color: #e11d48;
}

.tfd-icon-neutral {
    background: #fce7ef;
    color: #ed4081;
}

.tfd-state-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
}

.tfd-state-msg {
    font-size: 0.85rem;
    color: #94a3b8;
    margin: 0;
}

/* ---- sets grid ---- */

.tfd-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.25rem;
}

/* ---- set card ---- */

.tfd-card {
    background: #ffffff;
    border: 1.5px solid #e8edf3;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
    display: flex;
    flex-direction: column;
}

.tfd-card:hover {
    border-color: #ffc7db;
    box-shadow: 0 6px 20px rgba(237, 64, 129, 0.1);
    transform: translateY(-2px);
}

/* top colored stripe */

.tfd-card-stripe {
    height: 5px;
    width: 100%;
    flex-shrink: 0;
}

.tfd-card-body {
    padding: 1.25rem 1.4rem 1.4rem;
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    flex: 1;
}

.tfd-card-top {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    margin-bottom: 0.2rem;
}

.tfd-count-pill {
    font-size: 0.75rem;
    font-weight: 600;
    color: #ed4081;
    background: #fce7ef;
    padding: 3px 10px;
    border-radius: 999px;
}

.tfd-set-title {
    font-size: 0.975rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    line-height: 1.35;
}

.tfd-set-desc {
    font-size: 0.815rem;
    color: #94a3b8;
    margin: 0;
    line-height: 1.55;
    flex: 1;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* ---- card action buttons ---- */

.tfd-card-actions {
    display: flex;
    gap: 0.5rem;
    padding-top: 0.85rem;
    border-top: 1px solid #f1f5f9;
    margin-top: 0.5rem;
}

/* ---- shared button ---- */

.tfd-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.55rem 1.1rem;
    font-size: 0.825rem;
    font-weight: 600;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: all 0.15s;
    font-family: inherit;
}

.tfd-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.tfd-btn-primary {
    background: #ed4081;
    color: #ffffff;
    padding: 0.6rem 1.2rem;
    font-size: 0.875rem;
}

.tfd-btn-primary:hover:not(:disabled) {
    background: #d13570;
    box-shadow: 0 4px 12px rgba(237, 64, 129, 0.3);
    transform: translateY(-1px);
}

.tfd-btn-edit {
    background: #f8fafc;
    color: #374151;
    border: 1.5px solid #e2e8f0;
    flex: 1;
    justify-content: center;
}

.tfd-btn-edit:hover {
    border-color: #ffc7db;
    background: #fce7ef;
    border-color: #ffc7db;
    color: #d13570;
}

.tfd-btn-delete {
    background: #fff1f2;
    color: #e11d48;
    border: 1.5px solid #fecdd3;
    flex: 1;
    justify-content: center;
}

.tfd-btn-delete:hover {
    background: #ffe4e8;
    border-color: #fda4af;
}

.tfd-btn-ghost {
    background: transparent;
    color: #64748b;
    border: 1.5px solid #e2e8f0;
}

.tfd-btn-ghost:hover {
    background: #f8fafc;
    color: #1e293b;
}

.tfd-btn-danger {
    background: #e11d48;
    color: #ffffff;
}

.tfd-btn-danger:hover:not(:disabled) {
    background: #be123c;
    box-shadow: 0 4px 12px rgba(225, 29, 72, 0.25);
}

/* ---- modal ---- */

.tfd-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 300;
    backdrop-filter: blur(2px);
}

.tfd-modal {
    background: #ffffff;
    border-radius: 16px;
    padding: 2rem;
    max-width: 400px;
    width: 90%;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
}

.tfd-modal-icon {
    width: 46px;
    height: 46px;
    border-radius: 12px;
    background: #fff7ed;
    color: #f97316;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.25rem;
}

.tfd-modal-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
}

.tfd-modal-body {
    font-size: 0.85rem;
    color: #64748b;
    margin: 0 0 0.5rem;
    line-height: 1.55;
}

.tfd-modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.65rem;
}

/* ---- modal transition ---- */

.tfd-fade-enter-active,
.tfd-fade-leave-active {
    transition: opacity 0.18s ease;
}

.tfd-fade-enter-from,
.tfd-fade-leave-to {
    opacity: 0;
}

/* ---- responsive ---- */

@media (max-width: 768px) {
    .tfd-page {
        padding: 1.5rem 1.25rem 3rem;
    }
    .tfd-title-row {
        flex-direction: column;
        align-items: flex-start;
    }
    .tfd-btn-primary {
        width: 100%;
        justify-content: center;
    }
    .tfd-grid {
        grid-template-columns: 1fr;
    }
}
</style>