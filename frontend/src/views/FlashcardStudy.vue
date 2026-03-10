<template>
    <div class="study-page">
    
        <div v-if="store.loading" class="state-box">
            <div class="spinner"></div>
            <p class="state-text">Loading flashcards...</p>
        </div>
    
        <div v-else-if="store.error" class="state-box state-error">
            <span class="material-symbols-outlined error-icon">error</span>
            <p class="state-text">{{ store.error }}</p>
        </div>
    
        <template v-else-if="store.currentSet">
          
                <div class="study-topbar">
                  <div class="topbar-left" >
                    <button class="back-btn" @click="goToDashboard">
                      <span class="material-symbols-outlined">arrow_back</span>
                    </button>
                    <div class="set-info">
                      <span class="set-label">FLASHCARDS</span>
                      <span class="material-symbols-outlined set-divider">chevron_right</span>
                      <span class="set-name">{{ store.currentSet.title }}</span>
                    </div>
                  </div>
                  <div class="topbar-center">
                    <span class="card-counter">{{ currentIndex + 1 }} / {{ cards.length }}</span>
                    <span class="card-title-sm">{{ store.currentSet.title }}</span>
                  </div>
                  <div class="topbar-right"></div>
                </div>
          
                <div v-if="cards.length === 0" class="state-box">
                  <span class="material-symbols-outlined empty-icon">layers_clear</span>
                  <h2 class="state-title">No cards found</h2>
                  <p class="state-text">This set has no cards yet.</p>
                </div>
          
                <div v-else-if="isDone" class="done-screen-wrapper">
                  <div class="result-card">
                      <div class="icon-confetti">🎉</div>
                      <h1 class="result-title">You finished this set!</h1>
                      <p class="result-desc">
                          You marked <strong class="text-green">{{ knownCount }}</strong> card(s) as known
                          and <strong class="text-pink">{{ learningCount }}</strong> as still learning.
                      </p>
                      
                      <div class="action-buttons">
                          <button class="btn-primary" @click="restart">
                              <span class="material-symbols-outlined mr-1">replay</span>
                              Study Again
                          </button>
                          <button class="btn-outline" @click="goToDashboard">
                              Back to Flashcard Sets
                          </button>
                      </div>
                  </div>
                </div>
          
                <div v-else class="main-area">
          
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
          
                  <div
                    class="flashcard-wrap"
                    :class="{ 'is-flipped': isFlipped }"
                    @click="flipCard"
                    role="button"
                    aria-label="flip card"
                  >
                    <div class="flashcard-inner">
          
                      <div class="flashcard-face flashcard-front">
                        <div v-if="currentCard.image_url" class="card-img-wrap">
                          <img :src="currentCard.image_url" class="card-img" alt="card image" />
                        </div>
                        <p class="card-word">{{ currentCard.term }}</p>
                        
                        <div v-if="currentCard.hint && !showHint" class="hint-indicator">
                          <span class="material-symbols-outlined">lightbulb</span> Click "Show Hint" below if stuck
                        </div>
    
                        <div class="card-shortcut-bar" @click.stop>
                          <span class="material-symbols-outlined shortcut-icon">keyboard</span>
                          <span class="shortcut-text">Press <kbd>Space</kbd> or click to flip</span>
                        </div>
                      </div>
          
                      <div class="flashcard-face flashcard-back">
                        <div v-if="currentCard.image_url" class="card-img-wrap">
                          <img :src="currentCard.image_url" class="card-img" alt="card image" />
                        </div>
                        <p class="card-word back-text">{{ currentCard.definition }}</p>
                        <div class="card-shortcut-bar" @click.stop>
                          <span class="material-symbols-outlined shortcut-icon">keyboard</span>
                          <span class="shortcut-text">Press <kbd>←</kbd> Don't Know · <kbd>→</kbd> Know</span>
                        </div>
                      </div>
          
                    </div>
                  </div>
          
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
          
                  <div class="bottom-controls">
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
          
                    <div class="right-controls">
                      <button class="icon-btn" @click="restart" title="Restart">
                        <span class="material-symbols-outlined">replay</span>
                      </button>
                      <button class="icon-btn" @click="shuffle" title="Shuffle">
                        <span class="material-symbols-outlined">shuffle</span>
                      </button>
                    </div>
                  </div>
          
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
                    <button class="nav-btn" @click="next">
                      <span class="material-symbols-outlined">chevron_right</span>
                    </button>
                  </div>
                </div>
</template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFlashcardStore } from '../store/flashcardStore'
import { authService } from '../services/authService'

const route = useRoute()
const router = useRouter();
const store = useFlashcardStore()

const setId = computed(() => route.params.setId)
const courseId = computed(() => route.params.courseId)

const backLink = computed(() => {
    const role = authService.getUser() ?.role
    const cId = route.params.courseId
    if (role === 'teacher' || role === 'admin') {
        return `/teacher/courses/${cId}/flashcards`
    }
    return `/student/courses/${cId}/flashcards`
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
    isFlipped.value = false
})

const knownCount = computed(() => cards.value.filter(c => c.status === 'known').length)
const learningCount = computed(() => cards.value.filter(c => c.status === 'learning').length)
const knownPercent = computed(() => Math.round((knownCount.value / (cards.value.length || 1)) * 100))
const learningPercent = computed(() => Math.round((learningCount.value / (cards.value.length || 1)) * 100))

function flipCard() { isFlipped.value = !isFlipped.value }

function next() {
    if (currentIndex.value < cards.value.length - 1) {
        currentIndex.value++
    } else {
        isDone.value = true
    }
}

function prev() {
    if (currentIndex.value > 0) currentIndex.value--
}

function goToDashboard() {
    router.push(`/flashcards/${courseId.value}`);
}

async function mark(status) {
    if (trackProgress.value) {

        await store.markCard(currentCard.value.id, status)
        const card = cards.value[currentIndex.value]
        if (card) card.status = status
    }
    isFlipped.value = false
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap');
/* =============================
 Base Layout
 =============================== */

.study-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: linear-gradient(90deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
    font-family: 'DM Sans', 'Sarabun', sans-serif;
}

.material-symbols-outlined {
    vertical-align: middle;
}

/* ===============================
 Topbar
 ================================= */

.study-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 2.5rem;
    background: transparent;
    position: sticky;
    top: 0;
    z-index: 10;
}

.topbar-left {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex: 1;
}

.back-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: #ffffff;
    border: 1.5px solid #fce4ec;
    color: #df4a7d;
    text-decoration: none;
    transition: all 0.2s ease;
    flex-shrink: 0;
    box-shadow: 0 4px 10px rgba(223, 74, 125, 0.1);
}

.back-btn:hover {
    background: #df4a7d;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(223, 74, 125, 0.2);
}

.set-info {
    display: flex;
    align-items: center;
    gap: 8px;
}

.set-label {
    font-size: 0.8rem;
    font-weight: 800;
    color: #df4a7d;
    letter-spacing: 0.05em;
    background: #ffffff;
    padding: 4px 12px;
    border-radius: 99px;
}

.set-divider {
    color: #9ca3af;
    font-size: 20px;
}

.set-name {
    font-size: 1rem;
    color: #111827;
    font-weight: 800;
    max-width: 250px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.topbar-center {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.card-counter {
    font-size: 1.2rem;
    font-weight: 900;
    color: #111827;
}

.card-title-sm {
    font-size: 0.85rem;
    color: #6b7280;
    font-weight: 600;
}

.topbar-right {
    flex: 1;
}

/* =====================================================
 States (Loading / Error / Empty)
 ===================================================== */

.state-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 4rem 2rem;
    text-align: center;
}

.empty-icon {
    font-size: 4rem;
    color: #9ca3af;
    margin-bottom: 1rem;
}

.error-icon {
    font-size: 4rem;
    color: #ef4444;
    margin-bottom: 1rem;
}

.state-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #111827;
    margin: 0;
}

.state-text {
    font-size: 1.1rem;
    color: #6b7280;
    font-weight: 500;
}

.spinner {
    width: 44px;
    height: 44px;
    border: 4px solid #fce4ec;
    border-top-color: #df4a7d;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* ===============================
 Main Area
 ================================= */

.main-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    padding: 1rem 2.5rem 3rem;
    gap: 1.5rem;
    max-width: 900px;
    width: 100%;
    margin: 0 auto;
}

/* ===============================
 Progress Row
 ================================= */

.progress-row {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.prog-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    font-weight: 800;
    white-space: nowrap;
}

.prog-chip.prog-learning {
    color: #df4a7d;
}

.prog-chip.prog-known {
    color: #10b981;
}

.prog-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    font-size: 0.95rem;
    font-weight: 900;
}

.prog-bar-track {
    flex: 1;
    height: 10px;
    background: #ffffff;
    border-radius: 99px;
    position: relative;
    overflow: hidden;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.02);
}

.prog-bar-fill {
    position: absolute;
    top: 0;
    height: 100%;
    border-radius: 99px;
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.prog-bar-learning {
    background: linear-gradient(90deg, #ffc7db, #df4a7d);
    left: 0;
}

.prog-bar-known {
    background: linear-gradient(90deg, #10b981, #34d399);
}

/* =================================
 Flashcard
 =================================== */

.flashcard-wrap {
    width: 100%;
    height: 480px;
    perspective: 1500px;
    cursor: pointer;
    position: relative;
    border-radius: 32px;
}

.flashcard-inner {
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 32px;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.06);
}

.flashcard-wrap.is-flipped .flashcard-inner {
    transform: rotateY(180deg);
}

.flashcard-wrap:hover .flashcard-inner {
    box-shadow: 0 20px 50px rgba(223, 74, 125, 0.15);
}

.flashcard-face {
    position: absolute;
    inset: 0;
    backface-visibility: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    gap: 1.5rem;
    border-radius: 32px;
    background: #ffffff;
    border: 1.5px solid #ffffff;
}

.flashcard-back {
    background: #faf9f7;
    transform: rotateY(180deg);
}

.card-img-wrap {
    width: 100%;
    max-height: 180px;
    display: flex;
    justify-content: center;
}

.card-img {
    max-height: 180px;
    max-width: 100%;
    object-fit: contain;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.card-word {
    font-size: 2.8rem;
    font-weight: 800;
    color: #111827;
    text-align: center;
    line-height: 1.3;
    letter-spacing: -0.02em;
    margin: 0;
}

.back-text {
    font-size: 2rem;
    font-weight: 600;
    color: #4b5563;
}

.hint-indicator {
    font-size: 0.9rem;
    color: #f59e0b;
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 600;
    background: #fef3c7;
    padding: 6px 16px;
    border-radius: 99px;
    margin-top: 1rem;
}

/* Shortcut bar */

.card-shortcut-bar {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: #f9fafb;
    border-top: 1px solid #f3f4f6;
    padding: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 0.85rem;
    color: #6b7280;
    cursor: default;
    border-radius: 0 0 32px 32px;
    font-weight: 600;
}

.shortcut-icon {
    font-size: 18px;
    color: #df4a7d;
}

kbd {
    display: inline-block;
    padding: 3px 8px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 0.8rem;
    font-family: inherit;
    background: #ffffff;
    color: #111827;
    font-weight: 700;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* ===========================
 Hint Row
 ============================= */

.hint-row {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.8rem;
    min-height: 40px;
}

.hint-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 20px;
    border-radius: 99px;
    border: 1.5px solid #fcd34d;
    background: #ffffff;
    color: #d97706;
    font-size: 0.9rem;
    font-weight: 800;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.2s;
    box-shadow: 0 4px 10px rgba(245, 158, 11, 0.1);
}

.hint-btn:hover,
.hint-btn-active {
    background: #fef3c7;
    box-shadow: 0 6px 15px rgba(245, 158, 11, 0.2);
}

.hint-box {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 1rem 1.5rem;
    background: #fef3c7;
    border: 1px solid #fde68a;
    border-radius: 16px;
    font-size: 1rem;
    font-weight: 600;
    color: #92400e;
}

.hint-box .material-symbols-outlined {
    color: #f59e0b;
    font-size: 24px;
}

/* ================================
 Bottom Controls
 ==================================*/

.bottom-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 1rem;
}

.track-toggle {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
}

.track-label {
    font-size: 0.9rem;
    color: #6b7280;
    font-weight: 700;
}

.toggle-btn {
    width: 50px;
    height: 28px;
    border-radius: 99px;
    background: #e5e7eb;
    border: none;
    cursor: pointer;
    position: relative;
    transition: background 0.3s;
    padding: 0;
}

.toggle-btn.toggle-on {
    background: #df4a7d;
}

.toggle-thumb {
    position: absolute;
    top: 4px;
    left: 4px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: white;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.toggle-btn.toggle-on .toggle-thumb {
    transform: translateX(22px);
}

/* Mark Buttons */

.mark-btns {
    display: flex;
    gap: 1.5rem;
    flex: 1;
    justify-content: center;
}

.mark-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 1rem 2rem;
    border-radius: 99px;
    border: 2px solid transparent;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    font-family: inherit;
    font-size: 1.05rem;
    font-weight: 800;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.mark-btn:hover:not(:disabled) {
    transform: translateY(-3px);
}

.mark-btn:active:not(:disabled) {
    transform: scale(0.97);
}

.mark-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.mark-learning {
    background: #ffffff;
    color: #df4a7d;
    border-color: #fce4ec;
}

.mark-learning:hover:not(:disabled) {
    background: #fff0f5;
    border-color: #df4a7d;
    box-shadow: 0 8px 20px rgba(223, 74, 125, 0.2);
}

.mark-known {
    background: #ffffff;
    color: #10b981;
    border-color: #dcfce7;
}

.mark-known:hover:not(:disabled) {
    background: #f0fdf4;
    border-color: #10b981;
    box-shadow: 0 8px 20px rgba(16, 185, 129, 0.2);
}

.right-controls {
    display: flex;
    gap: 0.8rem;
    flex: 1;
    justify-content: flex-end;
}

.icon-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #ffffff;
    border: none;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.icon-btn:hover {
    background: #df4a7d;
    color: #ffffff;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(223, 74, 125, 0.2);
}

/* ==================================
 Navigation Row
 ==================================== */

.nav-row {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    justify-content: space-between;
    margin-top: 1rem;
}

.nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    height: 50px;
    border-radius: 16px;
    background: #ffffff;
    border: none;
    color: #111827;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.nav-btn:hover:not(:disabled) {
    background: #f9fafb;
    transform: scale(1.05);
}

.nav-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.dot-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
    flex: 1;
}

.dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #e5e7eb;
    transition: all 0.3s;
}

.dot-active {
    background: #6b7280;
    transform: scale(1.4);
}

.dot-known {
    background: #10b981;
}

.dot-learning {
    background: #df4a7d;
}

/* ================================
 Done Screen 
 ================================== */

.done-screen-wrapper {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
}

.result-card {
    background: #ffffff;
    padding: 4rem 3rem;
    border-radius: 24px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.05);
    text-align: center;
    max-width: 600px;
    width: 100%;
    border: 1px solid #ffffff;
    animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.icon-confetti {
    font-size: 4.5rem;
    margin-bottom: 1rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 120px;
    height: 120px;
    background: #fce4ec;
    border-radius: 50%;
    animation: pop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.result-title {
    color: #111827;
    margin-bottom: 1rem;
    font-size: 2.2rem;
    font-weight: 900;
    letter-spacing: -0.02em;
}

.result-desc {
    color: #6b7280;
    font-size: 1.1rem;
    margin-bottom: 3rem;
    line-height: 1.6;
}

.text-green {
    color: #10b981;
    font-weight: 800;
}

.text-pink {
    color: #df4a7d;
    font-weight: 800;
}

.action-buttons {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
}

.btn-primary {
    width: 100%;
    background: linear-gradient(135deg, #df4a7d 0%, #c83264 100%);
    color: white;
    padding: 16px;
    border: none;
    border-radius: 99px;
    font-size: 1.1rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 15px rgba(223, 74, 125, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(223, 74, 125, 0.35);
}

.btn-outline {
    width: 100%;
    background: white;
    color: #6b7280;
    padding: 16px;
    border: 2px solid #e5e7eb;
    border-radius: 99px;
    font-size: 1.1rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-block;
    box-sizing: border-box;
}

.btn-outline:hover {
    background: #f9fafb;
    color: #111827;
    border-color: #d1d5db;
}

/* Responsive */

@media (max-width: 768px) {
    .study-topbar {
        padding: 1rem;
    }
    .topbar-left .set-name {
        display: none;
    }
    .main-area {
        padding: 1rem;
    }
    .flashcard-wrap {
        height: 380px;
    }
    .card-word {
        font-size: 1.8rem;
    }
    .back-text {
        font-size: 1.4rem;
    }
    .bottom-controls {
        flex-direction: column;
        gap: 1.5rem;
    }
    .mark-btn {
        padding: 0.8rem 1.5rem;
        font-size: 0.95rem;
    }
}
</style>