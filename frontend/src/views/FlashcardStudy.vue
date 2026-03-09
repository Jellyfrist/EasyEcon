<template>
    <div class="study-page">
    
        <!-- loading -->
        <div v-if="store.loading" class="state-box">
            <div class="spinner"></div>
            <p>Loading flashcards...</p>
        </div>
    
        <!-- error -->
        <div v-else-if="store.error" class="state-box state-error">
            <span class="material-symbols-outlined">error</span>
            <p>{{ store.error }}</p>
        </div>
    
        <template v-else-if="store.currentSet">
        
              <!-- topbar -->
              <div class="study-topbar">
                <div class="topbar-left">
                  <router-link :to="backLink" class="back-btn">
                    <span class="material-symbols-outlined">arrow_back</span>
                  </router-link>
                  <div class="set-info">
                    <span class="set-label">Flashcards</span>
                    <span class="set-divider">›</span>
                    <span class="set-name">{{ store.currentSet.title }}</span>
                  </div>
                </div>
                <div class="topbar-center">
                  <span class="card-counter">{{ currentIndex + 1 }} / {{ cards.length }}</span>
                  <span class="card-title-sm">{{ store.currentSet.title }}</span>
                </div>
                <div class="topbar-right"></div>
              </div>
        
              <!-- empty -->
              <div v-if="cards.length === 0" class="state-box">
                <span class="material-symbols-outlined">layers_clear</span>
                <p>This set has no cards yet.</p>
              </div>
        
              <!-- done screen -->
              <div v-else-if="isDone" class="done-screen">
                <div class="done-icon">🎉</div>
                <h2>You finished this set!</h2>
                <h4>
                  You marked <strong>{{ knownCount }}</strong> card(s) as known
                  and <strong>{{ learningCount }}</strong> as still learning.
                </h4>
                <div class="done-actions">
                  <button class="btn-outline-light" @click="restart">
                    <span class="material-symbols-outlined">replay</span>
                    Study again
                  </button>
                  <router-link :to="backLink" class="btn btn-primary">Back to sets</router-link>
                </div>
              </div>
        
              <!-- main area -->
              <div v-else class="main-area">
        
                <!-- progress row -->
                <div class="progress-row">
                  <div class="prog-chip prog-learning">
                    <span class="prog-count">{{ learningCount }}</span>
                    <span class="prog-label">Still learning</span>
                  </div>
                  <div class="prog-bar-track">
                    <div class="prog-bar-fill prog-bar-learning" :style="{ width: learningPercent + '%' }"></div>
                    <div class="prog-bar-fill prog-bar-known" :style="{ width: knownPercent + '%', left: learningPercent + '%' }"></div>
                  </div>
                  <div class="prog-chip prog-known">
                    <span class="prog-label">Know</span>
                    <span class="prog-count">{{ knownCount }}</span>
                  </div>
                </div>
        
                <!-- flashcard: full width -->
                <div
                  class="flashcard-wrap"
                  :class="{ 'is-flipped': isFlipped }"
                  @click="flipCard"
                  role="button"
                  aria-label="flip card"
                >
                  <div class="flashcard-inner">
        
                    <!-- front: term -->
                    <div class="flashcard-face flashcard-front">
                      <div v-if="currentCard.image_url" class="card-img-wrap">
                        <img :src="currentCard.image_url" class="card-img" alt="card image" />
                      </div>
                      <p class="card-word">{{ currentCard.term }}</p>
                      <!-- shortcut bar inside card -->
                      <div class="card-shortcut-bar" @click.stop>
                        <span class="material-symbols-outlined shortcut-icon">keyboard</span>
                        <span class="shortcut-label">Shortcut</span>
                        <span class="shortcut-text">Press <kbd>Space</kbd> or click on the card to flip</span>
                      </div>
                    </div>
        
                    <!-- back: definition -->
                    <div class="flashcard-face flashcard-back">
                      <div v-if="currentCard.image_url" class="card-img-wrap">
                        <img :src="currentCard.image_url" class="card-img" alt="card image" />
                      </div>
                      <p class="card-word">{{ currentCard.definition }}</p>
                      <!-- shortcut bar inside card back -->
                      <div class="card-shortcut-bar" @click.stop>
                        <span class="material-symbols-outlined shortcut-icon">keyboard</span>
                        <span class="shortcut-label">Shortcut</span>
                        <span class="shortcut-text">Press <kbd>←</kbd> Don't Know · <kbd>→</kbd> Know</span>
                      </div>
                    </div>
        
                  </div>
                </div>
        
                <!-- hint row: below card, right-aligned -->
                <div class="hint-row">
                  <transition name="hint-slide">
                    <div v-if="showHint && currentCard.hint" class="hint-box">
                      <span class="material-symbols-outlined">lightbulb</span>
                      {{ currentCard.hint }}
                    </div>
                  </transition>
                  <button
                    v-if="currentCard.hint"
                    class="hint-btn"
                    :class="{ 'hint-btn-active': showHint }"
                    @click="showHint = !showHint"
                  >
                    <span class="material-symbols-outlined">lightbulb</span>
                    {{ showHint ? 'Hide Hint' : 'Show Hint' }}
                  </button>
                </div>
        
                <!-- bottom controls -->
                <div class="bottom-controls">
                  <!-- track progress toggle -->
                  <div class="track-toggle">
                    <span class="track-label">Track progress</span>
                    <button
                      class="toggle-btn"
                      :class="{ 'toggle-on': trackProgress }"
                      @click="trackProgress = !trackProgress"
                    >
                      <span class="toggle-thumb"></span>
                    </button>
                  </div>
        
                  <!-- Don't Know / Know buttons -->
                  <div class="mark-btns">
                    <button
                      class="mark-btn mark-learning"
                      :class="{ active: currentCard.status === 'learning' }"
                      :disabled="!isFlipped"
                      @click.stop="mark('learning')"
                    >
                      <span class="material-symbols-outlined">close</span>
                      Don't Know
                    </button>
                    <button
                      class="mark-btn mark-known"
                      :class="{ active: currentCard.status === 'known' }"
                      :disabled="!isFlipped"
                      @click.stop="mark('known')"
                    >
                      <span class="material-symbols-outlined">check</span>
                      Know
                    </button>
                  </div>
        
                  <!-- restart + shuffle -->
                  <div class="right-controls">
                    <button class="icon-btn" @click="restart" title="restart">
                      <span class="material-symbols-outlined">replay</span>
                    </button>
                    <button class="icon-btn" @click="shuffle" title="shuffle">
                      <span class="material-symbols-outlined">shuffle</span>
                    </button>
                  </div>
                </div>
        
                <!-- prev / next arrows -->
                <div class="nav-row">
                  <button class="nav-btn" :disabled="currentIndex === 0" @click="prev">
                    <span class="material-symbols-outlined">chevron_left</span>
                  </button>
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
              </div>
</template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useFlashcardStore } from '../store/flashcardStore'
import { authService } from '../services/authService'

const route = useRoute()
const store = useFlashcardStore()

const setId = computed(() => route.params.setId)

const backLink = computed(() => {
    const role = authService.getUser() ?.role
    if (role === 'teacher' || role === 'admin') {
        return { name: 'TeacherFlashcardDashboard', params: { courseId: route.params.courseId } }
    }
    return { name: 'FlashcardsDashboard', params: { courseId: route.params.courseId } }
})

const cards = computed(() => store.currentSet ?.cards ?? [])
const currentIndex = ref(0)
const isFlipped = ref(false)
const isDone = ref(false)
const showHint = ref(false)
const trackProgress = ref(true)

const currentCard = computed(() => cards.value[currentIndex.value] ?? {})

watch(currentIndex, () => {
    showHint.value = false
})

const knownCount = computed(() => cards.value.filter(c => c.status === 'known').length)
const learningCount = computed(() => cards.value.filter(c => c.status === 'learning').length)
const knownPercent = computed(() => Math.round((knownCount.value / (cards.value.length || 1)) * 100))
const learningPercent = computed(() => Math.round((learningCount.value / (cards.value.length || 1)) * 100))

function flipCard() { isFlipped.value = !isFlipped.value }

function next() {
    isFlipped.value = false
    if (currentIndex.value < cards.value.length - 1) {
        currentIndex.value++
    } else {
        isDone.value = true
    }
}

function prev() {
    isFlipped.value = false
    if (currentIndex.value > 0) currentIndex.value--
}

async function mark(status) {
    if (trackProgress.value) {
        // save to api and update local status
        await store.markCard(currentCard.value.id, status)
        const card = cards.value[currentIndex.value]
        if (card) card.status = status
    }
    // flip back then advance
    isFlipped.value = false
    setTimeout(() => next(), 600)
}

function restart() {
    currentIndex.value = 0
    isFlipped.value = false
    isDone.value = false
    showHint.value = false
}

function shuffle() {
    if (!store.currentSet) return
    const shuffled = [...store.currentSet.cards].sort(() => Math.random() - 0.5)
    store.currentSet = { ...store.currentSet, cards: shuffled }
    currentIndex.value = 0
    isFlipped.value = false
}

function handleKey(e) {
    if (e.key === ' ') {
        e.preventDefault();
        flipCard()
    } else if (e.key === 'ArrowRight' && isFlipped.value) mark('known')
    else if (e.key === 'ArrowLeft' && isFlipped.value) mark('learning')
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
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #f0ede8;
}

/* topbar */

.study-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2.5rem;
    background: radial-gradient(ellipse at 70% 50%, #7b1035 0%, transparent 60%), radial-gradient(ellipse at 20% 80%, #4a0a1e 0%, transparent 55%), #2d0514;
    border-bottom: none;
    position: sticky;
    top: 0;
    z-index: 10;
}

.topbar-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 1;
}

.back-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #ffffff;
    text-decoration: none;
    transition: all 0.2s;
    flex-shrink: 0;
}

.back-btn:hover {
    background: rgba(255, 255, 255, 0.22);
    transform: translateX(-2px);
}

.set-info {
    display: flex;
    align-items: center;
    gap: 6px;
}

.set-label {
    font-size: 0.92rem;
    font-weight: 800;
    color: #f472b6;
}

.set-divider {
    color: rgba(255, 255, 255, 0.3);
}

.set-name {
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.6);
    font-weight: 500;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.topbar-center {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
}

.card-counter {
    font-size: 1.05rem;
    font-weight: 800;
    color: #ffffff;
}

.card-title-sm {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.45);
}

.topbar-right {
    flex: 1;
}

/* states */

.state-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 4rem 2rem;
    color: var(--text-muted);
    text-align: center;
}

.state-box .material-symbols-outlined {
    font-size: 48px;
    opacity: 0.35;
}

.state-error {
    color: #f87171;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--card-border);
    border-top-color: var(--primary-pink);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* main area */

.main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    padding: 1.5rem 2.5rem 2rem;
    gap: 1rem;
    max-width: 1100px;
    width: 100%;
    margin: 0 auto;
}

/* progress row */

.progress-row {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.prog-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.82rem;
    font-weight: 700;
    white-space: nowrap;
}

.prog-chip.prog-learning {
    color: var(--primary-hover);
}

.prog-chip.prog-known {
    color: var(--forest-green);
}

.prog-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: 2px solid currentColor;
    font-size: 0.82rem;
    font-weight: 800;
}

.prog-bar-track {
    flex: 1;
    height: 8px;
    background: #e5e0d8;
    border-radius: 99px;
    position: relative;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.08);
}

.prog-bar-fill {
    position: absolute;
    top: 0;
    height: 100%;
    border-radius: 99px;
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.prog-bar-learning {
    background: linear-gradient(90deg, var(--primary-hover), var(--primary-pink));
    left: 0;
}

.prog-bar-known {
    background: linear-gradient(90deg, var(--forest-green), var(--accent-green));
}

/* flashcard */

.flashcard-wrap {
    width: 100%;
    height: 420px;
    perspective: 1400px;
    cursor: pointer;
    position: relative;
    border-radius: 20px;
    filter: drop-shadow(0 16px 40px rgba(46, 56, 86, 0.13));
    transition: filter 0.3s;
}

.flashcard-wrap:hover {
    filter: drop-shadow(0 20px 48px rgba(46, 56, 86, 0.18));
}

.flashcard-inner {
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 20px;
}

.flashcard-wrap.is-flipped .flashcard-inner {
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
    padding: 2.5rem 3rem 4.5rem;
    gap: 1.25rem;
    border-radius: 20px;
    overflow: hidden;
}

.flashcard-front {
    background: var(--white);
    border: 1.5px solid rgba(237, 64, 130, 0.1);
}

.flashcard-back {
    background: linear-gradient(145deg, #fbfbfb, #ffffff);
    border: 1.5px solid rgba(237, 64, 130, 0.1);
    transform: rotateY(180deg);
}

.card-img-wrap {
    width: 100%;
    max-height: 160px;
    display: flex;
    justify-content: center;
}

.card-img {
    max-height: 160px;
    max-width: 100%;
    object-fit: contain;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.card-word {
    font-size: 1.85rem;
    font-weight: 800;
    color: var(--text-main);
    text-align: center;
    line-height: 1.35;
    letter-spacing: -0.02em;
}

/* shortcut bar: inside card at bottom */

.card-shortcut-bar {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(165, 180, 252, 0.15);
    border-top: 1px solid rgba(165, 180, 252, 0.2);
    padding: 0.7rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.8rem;
    color: var(--text-muted);
    cursor: default;
    border-radius: 0 0 20px 20px;
}

.shortcut-icon {
    font-size: 20px;
    color: var(--primary-pink);
    opacity: 0.8;
}

.shortcut-label {
    font-weight: 700;
    color: var(--text-main);
}

kbd {
    display: inline-block;
    padding: 2px 8px;
    border: 1px solid var(--card-border);
    border-radius: 6px;
    font-size: 0.76rem;
    font-family: inherit;
    background: var(--white);
    color: var(--text-main);
    font-weight: 600;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

/* hint row */

.hint-row {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
}

.hint-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 16px;
    border-radius: 99px;
    border: 1.5px solid #fbbf24;
    background: rgba(255, 251, 235, 0.8);
    color: #d97706;
    font-size: 0.8rem;
    font-weight: 700;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
    box-shadow: 0 2px 6px rgba(251, 191, 36, 0.15);
}

.hint-btn:hover {
    background: #fef3c7;
    box-shadow: 0 4px 12px rgba(251, 191, 36, 0.25);
}

.hint-btn-active {
    background: #fef3c7;
}

.hint-btn .material-symbols-outlined {
    font-size: 16px;
}

.hint-box {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.8rem 1.25rem;
    background: linear-gradient(135deg, rgba(255, 251, 235, 0.9), rgba(254, 243, 199, 0.9));
    border: 1.5px solid #fde68a;
    border-radius: var(--radius-md);
    font-size: 0.9rem;
    font-weight: 500;
    color: #92400e;
    box-shadow: 0 2px 8px rgba(251, 191, 36, 0.12);
}

.hint-box .material-symbols-outlined {
    font-size: 18px;
    color: #f59e0b;
    flex-shrink: 0;
}

.hint-slide-enter-active {
    transition: opacity 0.25s, transform 0.25s;
}

.hint-slide-leave-active {
    transition: opacity 0.15s;
}

.hint-slide-enter-from {
    opacity: 0;
    transform: translateY(6px);
}

.hint-slide-leave-to {
    opacity: 0;
}

/* bottom controls */

.bottom-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.track-toggle {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    flex: 1;
}

.track-label {
    font-size: 0.82rem;
    color: var(--text-muted);
    font-weight: 600;
}

.toggle-btn {
    width: 46px;
    height: 26px;
    border-radius: 99px;
    background: #d1d5db;
    border: none;
    cursor: pointer;
    position: relative;
    transition: background 0.25s;
    padding: 0;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toggle-btn.toggle-on {
    background: var(--primary-pink);
}

.toggle-thumb {
    position: absolute;
    top: 3px;
    left: 3px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: white;
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.toggle-btn.toggle-on .toggle-thumb {
    transform: translateX(20px);
}

.mark-btns {
    display: flex;
    gap: 1.25rem;
    flex: 1;
    justify-content: center;
}

.mark-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0.75rem 1.5rem;
    border-radius: 99px;
    border: none;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    font-family: inherit;
    font-size: 0.95rem;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.mark-btn:hover:not(:disabled) {
    transform: scale(1.05);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.mark-btn:active:not(:disabled) {
    transform: scale(0.97);
}

.mark-btn .material-symbols-outlined {
    font-size: 20px;
}

.mark-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
    box-shadow: none;
}

.mark-learning {
    background: linear-gradient(135deg, #ffe3f8, #ffacf0);
    color: var(--primary-hover);
}

.mark-learning:hover:not(:disabled),
.mark-learning.active {
    background: linear-gradient(135deg, #ffc7f5, #ffb3e4);
}

.mark-known {
    background: linear-gradient(135deg, #a7f3d0, #6ee7b7);
    color: var(--forest-green);
}

.mark-known:hover:not(:disabled),
.mark-known.active {
    background: linear-gradient(135deg, #6ee7b7, #34d399);
}

.next-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0.75rem 2rem;
    border-radius: 99px;
    background: var(--primary-pink);
    border: none;
    color: white;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
    box-shadow: 0 4px 14px rgba(237, 64, 130, 0.35);
    animation: pop 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.next-btn:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(237, 64, 130, 0.45);
}

.next-btn .material-symbols-outlined {
    font-size: 20px;
}

.right-controls {
    display: flex;
    gap: 0.5rem;
    flex: 1;
    justify-content: flex-end;
}

.icon-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid var(--card-border);
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.2s;
    font-family: inherit;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(6px);
}

.icon-btn:hover {
    background: var(--white);
    color: var(--text-main);
    transform: scale(1.05);
    box-shadow: var(--shadow-md);
}

.icon-btn .material-symbols-outlined {
    font-size: 20px;
}

/* nav row */

.nav-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    justify-content: space-between;
}

.nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid var(--card-border);
    color: var(--text-main);
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
    box-shadow: var(--shadow-sm);
    backdrop-filter: blur(6px);
}

.nav-btn:hover:not(:disabled) {
    background: var(--white);
    box-shadow: var(--shadow-md);
}

.nav-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.nav-btn .material-symbols-outlined {
    font-size: 26px;
}

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
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid var(--card-border);
    transition: background 0.2s, transform 0.2s;
}

.dot-active {
    background: var(--gray);
    border-color: var(--primary-pink);
    transform: scale(1.4);
}

.dot-known {
    background: var(--forest-green);
    border-color: var(--forest-green);
}

.dot-learning {
    background: var(--primary-hover);
    border-color: var(--primary-hover);
}

/* done screen */

.done-screen {
    flex: 1;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1.25rem;
    padding: 3rem 1rem;
    color: var(--text-main);
}

.done-icon {
    font-size: 4rem;
    line-height: 1;
    animation: pop 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes pop {
    from {
        transform: scale(0.5);
        opacity: 0;
    }
    to {
        transform: scale(1);
        opacity: 1;
    }
}

.done-screen h2 {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.02em;
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

.btn-outline-light {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius-md);
    border: 2px solid var(--card-border);
    background: var(--white);
    color: var(--text-main);
    font-weight: 700;
    cursor: pointer;
    font-family: inherit;
    font-size: 0.95rem;
    text-decoration: none;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s;
}

.btn-outline-light:hover {
    background: var(--gray-light);
}

@media (max-width: 600px) {
    .study-topbar {
        padding: 0.75rem 1rem;
    }
    .main-area {
        padding: 1.25rem 1rem 1.5rem;
        gap: 0.75rem;
    }
    .flashcard-wrap {
        height: 300px;
    }
    .card-word {
        font-size: 1.35rem;
    }
    .topbar-left .set-name {
        display: none;
    }
    .mark-btn {
        width: 52px;
        height: 52px;
    }
}
</style>