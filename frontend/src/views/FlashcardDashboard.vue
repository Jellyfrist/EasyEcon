<template>
    <div class="flashcard-dashboard">
    
        <!-- page header -->
        <div class="page-header">
            <div class="header-inner">
                <p class="header-eyebrow">{{ courseStore.currentCourse.title }}</p>
                <h1 class="header-title">Flashcard Sets</h1>
                <p class="header-subtitle" v-if="!store.loading && store.sets.length > 0">
                    {{ store.sets.length }} sets available for this course
                </p>
            </div>
        </div>
    
        <!-- loading state -->
        <div v-if="store.loading" class="state-container">
            <div class="skeleton-grid">
                <div class="skeleton-card" v-for="n in 4" :key="n">
                    <div class="skeleton-stripe"></div>
                    <div class="skeleton-body">
                        <div class="skeleton-line short"></div>
                        <div class="skeleton-line long"></div>
                        <div class="skeleton-line medium"></div>
                    </div>
                </div>
            </div>
        </div>
    
        <!-- error state -->
        <div v-else-if="store.error" class="state-container">
            <div class="state-box error-box">
                <span class="state-icon">⚠️</span>
                <p class="state-title">Something went wrong</p>
                <p class="state-desc">{{ store.error }}</p>
            </div>
        </div>
    
        <!-- empty state -->
        <div v-else-if="store.sets.length === 0" class="state-container">
            <div class="state-box empty-box">
                <span class="state-icon">📭</span>
                <p class="state-title">No flashcard sets yet</p>
                <p class="state-desc">Your teacher hasn't added any sets for this course.</p>
            </div>
        </div>
    
        <!-- 2-column grid -->
        <div v-else class="sets-grid">
            <div v-for="(set, index) in store.sets" :key="set.id" class="set-card" :style="{ '--accent': accentColor(index) }" @click="goToStudy(set.id)">
                <!-- color stripe at top -->
                <div class="card-stripe"></div>
    
                <div class="card-body">
                    <!-- top row: icon + title -->
                    <div class="card-top">
                        <div class="set-icon">{{ setIcon(index) }}</div>
                        <div class="card-titles">
                            <h3 class="card-title">{{ set.title }}</h3>
                            <!-- teacher name -->
                            <p class="card-teacher" v-if="set.teacher_name">
                                <span class="teacher-label">by</span> {{ set.teacher_name }}
                            </p>
                        </div>
                    </div>
    
                    <!-- description -->
                    <p class="card-desc">{{ set.description || 'No description provided.' }}</p>
    
                    <!-- progress bar -->
                    <div class="progress-section">
                        <div class="progress-row">
                            <span class="progress-label">Progress</span>
                            <span class="progress-count">{{ set.known_count ?? 0 }} / {{ set.card_count ?? 0 }} cards</span>
                        </div>
                        <div class="progress-track">
                            <div class="progress-fill" :style="{ width: progressPercent(set) + '%' }"></div>
                        </div>
                    </div>
    
                    <!-- footer: card count + study button -->
                    <div class="card-footer">
                        <span class="card-count-pill">{{ set.card_count ?? 0 }} cards</span>
                        <button class="study-btn" @click.stop="goToStudy(set.id)">
                                    Study now
                                    <span class="btn-arrow">→</span>
                                </button>
                    </div>
                </div>
            </div>
        </div>
    
    </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFlashcardStore } from '../store/flashcardStore'
import { useCourseStore } from '../store/courseStore'
import flashcardService from '../services/flashcardService'

const route = useRoute()
const router = useRouter()
const store = useFlashcardStore()
const courseStore = useCourseStore()

const courseId = computed(() => route.params.courseId ? parseInt(route.params.courseId, 10) : null)

// list of soft accent colors for each card
const accents = [
    '#4f8ef7', // blue
    '#f7724f', // orange
    '#4fcfb0', // teal
    '#c97ff7', // purple
    '#f7c74f', // yellow
    '#f7506e', // red
    '#4fd97f', // green
    '#f74fc9', // pink
]

// pick accent color based on card index
function accentColor(index) {
    return accents[index % accents.length]
}

// pick a simple emoji icon based on index
const icons = ['📘', '📗', '📙', '📕', '📓', '📔', '📒', '📃']

function setIcon(index) {
    return icons[index % icons.length]
}

// calculate progress as a percent using known cards from real api data
function progressPercent(set) {
    const total = set.card_count ?? 0
    const known = set.known_count ?? 0
    if (total === 0) return 0
    return Math.min(100, Math.round((known / total) * 100))
}

function goToStudy(setId) {
    router.push({ name: 'FlashcardStudy', params: { courseId: route.params.courseId, setId } })
}

onMounted(async () => {
    store.sets = []
    if (!courseId.value) return

    // load course title and sets at the same time
    await Promise.all([
        courseStore.viewCourse(courseId.value),
        store.browseSets(courseId.value),
    ])

    // fetch progress for every set in parallel, then merge known count into each set
    await Promise.all(
        store.sets.map(async (set) => {
            try {
                const res = await flashcardService.getSetProgress(set.id)
                // merge known count so the template can read it
                set.known_count = res.data.known_count ?? 0
            } catch {
                set.known_count = 0
            }
        })
    )
})
</script>

<style scoped>

/* base layout */

.flashcard-dashboard {
    min-height: 100vh;
    background: #f0ede8;
    /* background: #ffffff; */
    font-family: 'Georgia', serif;
}

/* page header */

.page-header {
    background: radial-gradient(ellipse at 70% 50%, #7b1035 0%, transparent 60%), 
    radial-gradient(ellipse at 20% 80%, #4a0a1e 0%, transparent 55%), #2d0514;
    padding: 56px 40px 52px;
}

.header-inner {
    max-width: 1100px;
    margin: 0 auto;
}

.header-eyebrow {
    display: inline-block;
    font-size: 0.7rem;
    font-family: 'Courier New', monospace;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #f472b6;
    border: 1px solid #f472b6;
    padding: 3px 10px;
    border-radius: 4px;
    margin: 0 0 16px;
}

.header-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 10px;
    line-height: 1.15;
    letter-spacing: -0.02em;
}

.header-subtitle {
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.45);
    margin: 0;
    font-family: 'Courier New', monospace;
}

/* 2-column grid */

.sets-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
    max-width: 1100px;
    margin: 0 auto;
    padding: 40px 40px;
}

@media (max-width: 700px) {
    .sets-grid {
        grid-template-columns: 1fr;
        padding: 24px 20px;
    }
    .page-header {
        padding: 40px 20px 36px;
    }
    .header-title {
        font-size: 1.75rem;
    }
}

/* card */

.set-card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07);
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    border: 1px solid #f0f0f0;
    display: flex;
    flex-direction: column;
}

.set-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.11);
}

/* colored stripe using css variable from parent */

.card-stripe {
    height: 6px;
    background: var(--accent);
    width: 100%;
    flex-shrink: 0;
}

.card-body {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    flex: 1;
}

/* top row */

.card-top {
    display: flex;
    align-items: flex-start;
    gap: 14px;
}

.set-icon {
    font-size: 1.75rem;
    line-height: 1;
    flex-shrink: 0;
    margin-top: 2px;
}

.card-titles {
    flex: 1;
    min-width: 0;
}

.card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 4px;
    line-height: 1.3;
    /* cut off very long titles */
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.card-teacher {
    font-size: 0.78rem;
    color: #9ca3af;
    margin: 0;
}

.teacher-label {
    font-style: italic;
}

/* description */

.card-desc {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0;
    line-height: 1.6;
    /* limit to 3 lines */
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* progress */

.progress-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.progress-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.progress-label {
    font-size: 0.75rem;
    font-family: 'Courier New', monospace;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9ca3af;
}

.progress-count {
    font-size: 0.75rem;
    color: #6b7280;
    font-family: 'Courier New', monospace;
}

.progress-track {
    height: 6px;
    background: #f3f4f6;
    border-radius: 999px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: var(--accent);
    border-radius: 999px;
    transition: width 0.5s ease;
    opacity: 0.85;
}

/* card footer */

.card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: auto;
    padding-top: 4px;
}

.card-count-pill {
    font-size: 0.75rem;
    font-family: 'Courier New', monospace;
    color: #9ca3af;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    padding: 4px 10px;
    border-radius: 999px;
}

.study-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent);
    color: #fff;
    border: none;
    padding: 9px 18px;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s ease, transform 0.15s ease;
    font-family: inherit;
    letter-spacing: 0.01em;
}

.study-btn:hover {
    opacity: 0.88;
    transform: scale(1.02);
}

.btn-arrow {
    font-size: 1rem;
    line-height: 1;
    transition: transform 0.15s ease;
}

.study-btn:hover .btn-arrow {
    transform: translateX(3px);
}

/* ── skeleton loading ── */

.skeleton-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
    max-width: 1100px;
    margin: 0 auto;
    padding: 40px 40px;
}

@media (max-width: 700px) {
    .skeleton-grid {
        grid-template-columns: 1fr;
        padding: 24px 20px;
    }
}

.skeleton-card {
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #f0f0f0;
}

.skeleton-stripe {
    height: 6px;
    background: #e5e7eb;
    animation: shimmer 1.4s infinite;
}

.skeleton-body {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.skeleton-line {
    height: 14px;
    border-radius: 8px;
    background: #e5e7eb;
    animation: shimmer 1.4s infinite;
}

.skeleton-line.short {
    width: 40%;
}

.skeleton-line.medium {
    width: 65%;
}

.skeleton-line.long {
    width: 100%;
}

@keyframes shimmer {
    0%,
    100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

/* ── empty / error states ── */

.state-container {
    display: flex;
    justify-content: center;
    padding: 80px 40px;
}

.state-box {
    text-align: center;
    max-width: 340px;
}

.state-icon {
    font-size: 2.5rem;
    display: block;
    margin-bottom: 16px;
}

.state-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 8px;
}

.state-desc {
    font-size: 0.9rem;
    color: #6b7280;
    margin: 0;
    line-height: 1.6;
}

.error-box .state-title {
    color: #ef4444;
}
</style>