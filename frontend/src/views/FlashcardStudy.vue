<template>
    <div class="study-page">
    
        <!-- loading state -->
        <div v-if="store.loading" class="state-box">
            <div class="spinner"></div>
            <p>Loading flashcards...</p>
        </div>
    
        <!-- error state -->
        <div v-else-if="store.error" class="state-box state-error">
            <span class="material-symbols-outlined">error</span>
            <p>{{ store.error }}</p>
        </div>
    
        <template v-else-if="store.currentSet">
    
          <!-- top bar: back + title + progress bar -->
          <div class="study-header">
            <router-link :to="backLink" class="back-btn">
              <span class="material-symbols-outlined">arrow_back</span>
            </router-link>
    
            <div class="header-info">
              <h1 class="set-title">{{ store.currentSet.title }}</h1>
              <div class="progress-bar-wrap">
                <div class="progress-bar-track">
                  <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }"></div>
                </div>
                <span class="progress-label">{{ currentIndex + 1 }} / {{ cards.length }}</span>
              </div>
            </div>
    
            <!-- progress summary chips -->
            <div class="progress-chips">
              <span class="chip chip-known">
                <span class="material-symbols-outlined">check_circle</span>
                {{ knownCount }} known
              </span>
              <span class="chip chip-learning">
                <span class="material-symbols-outlined">autorenew</span>
                {{ learningCount }} learning
              </span>
            </div>
          </div>
    
          <!-- empty set guard -->
          <div v-if="cards.length === 0" class="state-box">
            <span class="material-symbols-outlined">layers_clear</span>
            <p>This set has no cards yet.</p>
          </div>
    
          <!-- study done screen -->
          <div v-else-if="isDone" class="done-screen">
            <div class="done-icon">🎉</div>
            <h2>You finished this set!</h2>
            <p>
              You marked <strong>{{ knownCount }}</strong> card(s) as known
              and <strong>{{ learningCount }}</strong> as still learning.
            </p>
            <div class="done-actions">
              <button class="btn btn-outline" @click="restart">
                <span class="material-symbols-outlined">replay</span>
                Study again
              </button>
              <router-link :to="backLink" class="btn btn-primary">
                Back to sets
              </router-link>
            </div>
          </div>
    
          <!-- main card area -->
          <div v-else class="card-area">
    
            <!-- flashcard flip -->
            <div
              class="flashcard-container"
              @click="flipCard"
              :class="{ 'is-flipped': isFlipped }"
              role="button"
              aria-label="flip card"
            >
              <div class="flashcard-inner">
                <!-- front: term -->
                <div class="flashcard-face flashcard-front">
                  <span class="face-label">Term</span>
                  <p class="face-text">{{ currentCard.term }}</p>
                  <span class="flip-hint">tap to flip</span>
                </div>
                <!-- back: definition -->
                <div class="flashcard-face flashcard-back">
                  <span class="face-label">Definition</span>
                  <p class="face-text">{{ currentCard.definition }}</p>
                  <p v-if="currentCard.hint" class="face-hint">
                    <span class="material-symbols-outlined">lightbulb</span>
                    {{ currentCard.hint }}
                  </p>
                </div>
              </div>
            </div>
    
            <!-- action buttons: shown after flipping -->
            <transition name="fade-up">
              <div v-if="isFlipped" class="mark-actions">
                <button
                  class="mark-btn mark-learning"
                  :class="{ active: currentCard.status === 'learning' }"
                  @click.stop="mark('learning')"
                >
                  <span class="material-symbols-outlined">autorenew</span>
                  Still learning
                </button>
                <button
                  class="mark-btn mark-known"
                  :class="{ active: currentCard.status === 'known' }"
                  @click.stop="mark('known')"
                >
                  <span class="material-symbols-outlined">check_circle</span>
                  I know this
                </button>
              </div>
            </transition>
    
            <!-- prev / next navigation -->
            <div class="nav-row">
              <button class="nav-btn" :disabled="currentIndex === 0" @click="prev">
                <span class="material-symbols-outlined">chevron_left</span>
              </button>
    
              <!-- dot indicators -->
              <div class="dot-row">
                <span
                  v-for="(card, idx) in cards"
                  :key="card.id"
                  class="dot"
                  :class="{
                    'dot-active': idx === currentIndex,
                    'dot-known': card.status === 'known',
                    'dot-learning': card.status === 'learning',
                  }"
                ></span>
              </div>
    
              <button class="nav-btn" :disabled="currentIndex === cards.length - 1" @click="next">
                <span class="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
    
            <!-- keyboard hint -->
            <p class="kb-hint">use ← → arrow keys to navigate</p>
    
          </div>
</template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useFlashcardStore } from '../store/flashcardStore'

const route = useRoute()
const store = useFlashcardStore()

const setId = computed(() => route.params.setId)

// link to go back to the dashboard — courseId is a route param now
const backLink = computed(() => ({
    name: 'FlashcardsDashboard',
    params: { courseId: route.params.courseId }
}))

// all cards from the loaded set
const cards = computed(() => store.currentSet?.cards ?? [])
// current card index in the list
const currentIndex = ref(0)

// whether the card is showing the back (definition)
const isFlipped = ref(false)

// whether all cards have been seen (user moved past the last card)
const isDone = ref(false)

const currentCard = computed(() => cards.value[currentIndex.value] ?? {})

const progressPercent = computed(() => {
    if (cards.value.length === 0) return 0
    return Math.round(((currentIndex.value + 1) / cards.value.length) * 100)
})

const knownCount = computed(() =>
    cards.value.filter(c => c.status === 'known').length
)

const learningCount = computed(() =>
    cards.value.filter(c => c.status === 'learning').length
)

function flipCard() {
    isFlipped.value = !isFlipped.value
}

function next() {
    if (currentIndex.value < cards.value.length - 1) {
        currentIndex.value++
            isFlipped.value = false
    } else {
        // reached the last card, show done screen
        isDone.value = true
    }
}

function prev() {
    if (currentIndex.value > 0) {
        currentIndex.value--
            isFlipped.value = false
    }
}

async function mark(status) {
    await store.markCard(currentCard.value.id, status)
    // move to next card automatically after marking
    setTimeout(() => next(), 350)
}

function restart() {
    currentIndex.value = 0
    isFlipped.value = false
    isDone.value = false
}

// keyboard navigation
function handleKey(e) {
    if (e.key === 'ArrowRight') next()
    else if (e.key === 'ArrowLeft') prev()
    else if (e.key === ' ') { e.preventDefault();
        flipCard() }
}

onMounted(async () => {
    await store.studySet(setId.value)
    document.addEventListener('keydown', handleKey)
})

onUnmounted(() => {
    document.removeEventListener('keydown', handleKey)
    store.clearCurrent()
})
</script>

<style scoped>
.study-page {
    max-width: 780px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
}

/* state boxes */

.state-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 4rem 2rem;
    color: var(--text-muted);
    text-align: center;
}

.state-box .material-symbols-outlined {
    font-size: 48px;
    opacity: 0.4;
}

.state-error {
    color: #ef4444;
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

/* header */

.study-header {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.back-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: white;
    border: 1px solid var(--card-border);
    color: var(--text-main);
    text-decoration: none;
    transition: background 0.15s;
    flex-shrink: 0;
    margin-top: 2px;
}

.back-btn:hover {
    background: var(--gray-light);
}

.header-info {
    flex: 1;
    min-width: 0;
}

.set-title {
    font-size: 1.3rem;
    font-weight: 800;
    margin: 0 0 0.5rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.progress-bar-wrap {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.progress-bar-track {
    flex: 1;
    height: 6px;
    background: #e5e7eb;
    border-radius: 99px;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    background: var(--primary-pink);
    border-radius: 99px;
    transition: width 0.3s ease;
}

.progress-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
    white-space: nowrap;
}

/* progress chips */

.progress-chips {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    flex-wrap: wrap;
}

.chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 20px;
}

.chip .material-symbols-outlined {
    font-size: 16px;
}

.chip-known {
    background: #dcfce7;
    color: #16a34a;
}

.chip-learning {
    background: #fef9c3;
    color: #ca8a04;
}

/* card area */

.card-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
}

/* flashcard 3d flip */

.flashcard-container {
    width: 100%;
    max-width: 600px;
    height: 340px;
    perspective: 1200px;
    cursor: pointer;
}

.flashcard-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
    transition: transform 0.55s cubic-bezier(0.4, 0, 0.2, 1);
}

.flashcard-container.is-flipped .flashcard-inner {
    transform: rotateY(180deg);
}

.flashcard-face {
    position: absolute;
    inset: 0;
    backface-visibility: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2.5rem;
    border-radius: 20px;
    border: 2px solid var(--card-border);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.07);
    gap: 0.75rem;
}

.flashcard-front {
    background: white;
}

.flashcard-back {
    background: #fff9f1;
    transform: rotateY(180deg);
}

.face-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
}

.face-text {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-main);
    text-align: center;
    line-height: 1.4;
}

.face-hint {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
}

.face-hint .material-symbols-outlined {
    font-size: 18px;
    color: #f59e0b;
}

.flip-hint {
    font-size: 0.78rem;
    color: #d1d5db;
    position: absolute;
    bottom: 1.25rem;
}

/* mark actions */

.mark-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

.mark-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius-md);
    font-size: 0.95rem;
    font-weight: 700;
    border: 2px solid transparent;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
    background: white;
}

.mark-btn .material-symbols-outlined {
    font-size: 20px;
}

.mark-learning {
    border-color: #fbbf24;
    color: #b45309;
}

.mark-learning:hover,
.mark-learning.active {
    background: #fef3c7;
}

.mark-known {
    border-color: #34d399;
    color: #065f46;
}

.mark-known:hover,
.mark-known.active {
    background: #d1fae5;
}

/* fade-up transition for mark buttons */

.fade-up-enter-active {
    transition: opacity 0.25s, transform 0.25s;
}

.fade-up-enter-from {
    opacity: 0;
    transform: translateY(10px);
}

/* navigation row */

.nav-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    max-width: 600px;
    justify-content: space-between;
}

.nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: white;
    border: 1px solid var(--card-border);
    cursor: pointer;
    color: var(--text-main);
    transition: background 0.15s;
    flex-shrink: 0;
}

.nav-btn:hover:not(:disabled) {
    background: var(--gray-light);
}

.nav-btn:disabled {
    opacity: 0.35;
    cursor: not-allowed;
}

.nav-btn .material-symbols-outlined {
    font-size: 24px;
}

/* dots */

.dot-row {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    justify-content: center;
    flex: 1;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #e5e7eb;
    transition: background 0.2s, transform 0.2s;
}

.dot-active {
    background: var(--primary-pink);
    transform: scale(1.3);
}

.dot-known {
    background: #34d399;
}

.dot-learning {
    background: #fbbf24;
}

/* keyboard hint */

.kb-hint {
    font-size: 0.78rem;
    color: #d1d5db;
    text-align: center;
}

/* done screen */

.done-screen {
    text-align: center;
    padding: 3rem 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.done-icon {
    font-size: 3.5rem;
    line-height: 1;
}

.done-screen h2 {
    font-size: 1.6rem;
    font-weight: 800;
}

.done-screen p {
    color: var(--text-muted);
    max-width: 380px;
}

.done-actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 0.5rem;
}

/* responsive */

@media (max-width: 600px) {
    .study-page {
        padding: 1.25rem 1rem 3rem;
    }
    .flashcard-container {
        height: 260px;
    }
    .face-text {
        font-size: 1.2rem;
    }
    .set-title {
        font-size: 1.1rem;
    }
}
</style>