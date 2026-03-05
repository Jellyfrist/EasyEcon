<template>
    <div class="flashcard-dashboard">
    
        <div class="header">
            <h1>Flashcard Sets</h1>
        </div>
    
        <!-- loading -->
        <div v-if="store.loading" class="loading">
            Loading flashcard sets...
        </div>
    
        <!-- error -->
        <div v-else-if="store.error" class="error">
            {{ store.error }}
        </div>
    
        <!-- empty -->
        <div v-else-if="store.sets.length === 0" class="empty">
            No flashcard sets available yet.
        </div>
    
        <!-- sets grid -->
        <div v-else class="sets-grid">
            <div v-for="set in store.sets" :key="set.id" class="set-card" @click="goToStudy(set.id)">
                <h3>{{ set.title }}</h3>
                <p class="meta">{{ set.description || 'No description' }}</p>
                <p class="card-count">{{ set.card_count ?? 0 }} cards</p>
                <button class="study-btn">Study</button>
            </div>
        </div>
    
    </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFlashcardStore } from '../store/flashcardStore'

const route = useRoute()
const router = useRouter()
const store = useFlashcardStore()

const courseId = computed(() => route.params.courseId ? parseInt(route.params.courseId, 10) : null)

function goToStudy(setId) {
    router.push({ name: 'FlashcardStudy', params: { courseId: route.params.courseId, setId } })
}

onMounted(() => {
    store.sets = []
    if (courseId.value) store.fetchSets(courseId.value)
})
</script>

<style scoped>
.flashcard-dashboard {
    padding: 40px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
}

.header h1 {
    margin: 0;
}

.loading,
.empty {
    opacity: 0.6;
    font-style: italic;
}

.error {
    color: #ef4444;
}

.sets-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 20px;
}

.set-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
    cursor: pointer;
    transition: box-shadow 0.2s;
}

.set-card:hover {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.set-card h3 {
    margin: 0 0 6px;
    font-size: 1rem;
    font-weight: 700;
}

.meta {
    font-size: 14px;
    opacity: 0.7;
    margin: 0 0 4px;
}

.card-count {
    font-size: 13px;
    color: #6b7280;
    margin: 0 0 16px;
}

.study-btn {
    background: #0A703C;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.875rem;
}

.study-btn:hover {
    background: #065f2e;
}
</style>