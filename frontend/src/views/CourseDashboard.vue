<template>
    <div class="cd-root">
    
        <!-- loading state -->
        <div v-if="store.loading" class="cd-state-box">
            <div class="cd-spinner"></div>
            <p class="cd-state-text">Loading course...</p>
        </div>
    
        <!-- error state -->
        <div v-else-if="store.error" class="cd-state-box">
            <div class="cd-error-icon">!</div>
            <p class="cd-error-msg">{{ store.error }}</p>
            <button class="cd-btn-back" @click="router.back()">Go Back</button>
        </div>
    
        <!-- course content -->
        <template v-else-if="store.currentCourse">
    
          <!-- hero: full bleed dark banner -->
          <div class="cd-hero">
            <div class="cd-hero-glow"></div>
            <div class="cd-hero-inner">
              <span class="cd-label">Course</span>
              <h1 class="cd-title">{{ store.currentCourse.title }}</h1>
              <p v-if="store.currentCourse.description" class="cd-desc">
                {{ store.currentCourse.description }}
              </p>
            </div>
          </div>
    
          <!-- body content -->
          <div class="cd-body">
    
            <!-- stat strip -->
            <div class="cd-stats">
              <div class="cd-stat">
                <div class="cd-stat-icon s-green">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                  </svg>
                </div>
                <div>
                  <div class="cd-stat-num">{{ store.currentCourse.module_count ?? 0 }}</div>
                  <div class="cd-stat-lbl">Modules</div>
                </div>
              </div>
    
              <div class="cd-stat-sep"></div>
    
              <div class="cd-stat">
                <div class="cd-stat-icon s-pink">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="2" y="5" width="20" height="14" rx="2"/>
                    <line x1="2" y1="10" x2="22" y2="10"/>
                  </svg>
                </div>
                <div>
                  <div class="cd-stat-num">{{ store.currentCourse.flashcard_set_count ?? 0 }}</div>
                  <div class="cd-stat-lbl">Flashcard Sets</div>
                </div>
              </div>
    
              <div class="cd-stat-sep"></div>
    
              <div class="cd-stat">
                <div class="cd-stat-icon s-amber">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                  </svg>
                </div>
                <div>
                  <div class="cd-stat-num">{{ store.currentCourse.exam_template_count ?? 0 }}</div>
                  <div class="cd-stat-lbl">Exam Templates</div>
                </div>
              </div>
            </div>
    
            <!-- section heading -->
            <div class="cd-section-head">
              <h2 class="cd-section-title">Study Tools</h2>
              <p class="cd-section-sub">Choose how you want to study this course</p>
            </div>
    
            <!-- feature banners -->
            <div class="cd-banners">
    
              <!-- modules -->
              <div class="cd-banner cd-green" @click="router.push(`/courses/${courseId}/modules`)">
                <div class="cd-banner-left">
                  <div class="cd-b-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                    </svg>
                  </div>
                  <div class="cd-b-text">
                    <span class="cd-b-tag">Step-by-step</span>
                    <h3 class="cd-b-title">Modules</h3>
                    <p class="cd-b-desc">Work through ordered lessons with mini quizzes to test your understanding.</p>
                    <span class="cd-b-badge">{{ store.currentCourse.module_count ?? 0 }} available</span>
                  </div>
                </div>
                <div class="cd-banner-right">
                  <div class="cd-art cd-art-lines">
                    <span></span><span></span><span></span>
                  </div>
                  <button class="cd-arrow" aria-label="go to modules">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <line x1="5" y1="12" x2="19" y2="12"/>
                      <polyline points="12 5 19 12 12 19"/>
                    </svg>
                  </button>
                </div>
              </div>
    
              <!-- flashcards -->
              <div class="cd-banner cd-pink" @click="router.push(`/flashcards/${courseId}`)">
                <div class="cd-banner-left">
                  <div class="cd-b-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="2" y="5" width="20" height="14" rx="2"/>
                      <line x1="2" y1="10" x2="22" y2="10"/>
                    </svg>
                  </div>
                  <div class="cd-b-text">
                    <span class="cd-b-tag">Quick review</span>
                    <h3 class="cd-b-title">Flashcards</h3>
                    <p class="cd-b-desc">Master key concepts with flashcard sets made by your teacher for fast revision.</p>
                    <span class="cd-b-badge">{{ store.currentCourse.flashcard_set_count ?? 0 }} sets</span>
                  </div>
                </div>
                <div class="cd-banner-right">
                  <div class="cd-art cd-art-cards">
                    <span></span><span></span><span></span>
                  </div>
                  <button class="cd-arrow" aria-label="go to flashcards">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <line x1="5" y1="12" x2="19" y2="12"/>
                      <polyline points="12 5 19 12 12 19"/>
                    </svg>
                  </button>
                </div>
              </div>
    
              <!-- exams -->
              <div class="cd-banner cd-amber" @click="router.push(`/exam/${courseId}`)">
                <div class="cd-banner-left">
                  <div class="cd-b-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                    </svg>
                  </div>
                  <div class="cd-b-text">
                    <span class="cd-b-tag">Practice test</span>
                    <h3 class="cd-b-title">Exams</h3>
                    <p class="cd-b-desc">Practice with past midterm and final exam question banks to build confidence.</p>
                    <span class="cd-b-badge">{{ store.currentCourse.exam_template_count ?? 0 }} templates</span>
                  </div>
                </div>
                <div class="cd-banner-right">
                  <div class="cd-art cd-art-circles">
                    <span></span><span></span>
                    <em>✓</em>
                  </div>
                  <button class="cd-arrow" aria-label="go to exams">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <line x1="5" y1="12" x2="19" y2="12"/>
                      <polyline points="12 5 19 12 12 19"/>
                    </svg>
                  </button>
                </div>
              </div>
    
            </div>
          </div>
</template>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { onMounted, onUnmounted, computed } from 'vue'
import { useCourseStore } from '@/store/courseStore'

const route = useRoute()
const router = useRouter()
const store = useCourseStore()

// get course id from url: /courses/:courseId
const courseId = computed(() => route.params.courseId)

// fetch course data when page loads
onMounted(async () => {
    await store.viewCourse(courseId.value)
})

// clean up when leaving the page
onUnmounted(() => {
    store.clearCurrent()
})
</script>

<style scoped>
/* =====================================================
   cd-root: escape any parent container so hero bleeds
   edge to edge. uses negative margin + 100vw width.
   ===================================================== */

.cd-root {
    position: relative;
    /* pull left to cancel parent horizontal padding */
    margin-left: calc(50% - 50vw);
    margin-right: calc(50% - 50vw);
    width: 100vw;
    min-height: 100vh;
    background: #f5f4f2;
    font-family: 'DM Sans', 'Outfit', 'Segoe UI', sans-serif;
    overflow-x: hidden;
    box-sizing: border-box;
}

/* ---- loading / error states ---- */

.cd-state-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    gap: 1rem;
    padding: 2rem;
}

.cd-spinner {
    width: 36px;
    height: 36px;
    border: 3px solid #fce4ec;
    border-top-color: #e91e63;
    border-radius: 50%;
    animation: cd-spin 0.8s linear infinite;
}

@keyframes cd-spin {
    to {
        transform: rotate(360deg);
    }
}

.cd-state-text {
    color: #999;
    font-size: 0.9rem;
}

.cd-error-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #fef2f2;
    color: #ef4444;
    font-size: 1.5rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
}

.cd-error-msg {
    color: #ef4444;
    font-size: 0.9rem;
    text-align: center;
}

.cd-btn-back {
    padding: 0.55rem 1.4rem;
    border-radius: 8px;
    border: none;
    background: #e91e63;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background 0.2s;
}

.cd-btn-back:hover {
    background: #c2185b;
}

/* =====================================================
   hero: full bleed, no border, no border-radius
   ===================================================== */

.cd-hero {
    position: relative;
    width: 100%;
    background: linear-gradient(135deg, #130610 0%, #3b0d21 55%, #130610 100%);
    padding: 4.5rem 6vw 4rem;
    overflow: hidden;
    box-sizing: border-box;
}

.cd-hero-glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 55% 90% at 75% 50%, rgba(233, 30, 99, 0.2) 0%, transparent 70%), radial-gradient(ellipse 35% 60% at 15% 30%, rgba(255, 77, 141, 0.1) 0%, transparent 60%);
    pointer-events: none;
}

.cd-hero-inner {
    position: relative;
    max-width: 860px;
}

.cd-label {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #f06292;
    background: rgba(233, 30, 99, 0.15);
    border: 1px solid rgba(233, 30, 99, 0.35);
    border-radius: 4px;
    padding: 0.22rem 0.7rem;
    margin-bottom: 1.2rem;
}

.cd-title {
    font-size: clamp(1.75rem, 3.5vw, 2.8rem);
    font-weight: 800;
    color: #fff;
    line-height: 1.15;
    letter-spacing: -0.02em;
    margin: 0 0 1rem;
}

.cd-desc {
    font-size: 0.975rem;
    color: rgba(255, 255, 255, 0.55);
    line-height: 1.75;
    max-width: 560px;
    margin: 0;
}

/* =====================================================
   body: padded section below hero
   ===================================================== */

.cd-body {
    padding: 2.5rem 6vw 5rem;
    box-sizing: border-box;
}

/* =====================================================
   stat strip
   ===================================================== */

.cd-stats {
    display: flex;
    align-items: center;
    background: #fff;
    border-radius: 16px;
    border: 1px solid #ece7e7;
    box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
    margin-bottom: 2.75rem;
    overflow: hidden;
}

.cd-stat {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.4rem 2rem;
}

.cd-stat-sep {
    width: 1px;
    height: 44px;
    background: #f0eaea;
    flex-shrink: 0;
}

.cd-stat-icon {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.cd-stat-icon svg {
    width: 20px;
    height: 20px;
}

.s-green {
    background: #e8f5e9;
    color: #2e7d32;
}

.s-pink {
    background: #fce4ec;
    color: #c2185b;
}

.s-amber {
    background: #fff8e1;
    color: #f57f17;
}

.cd-stat-num {
    font-size: 1.65rem;
    font-weight: 800;
    color: #130610;
    line-height: 1;
}

.cd-stat-lbl {
    font-size: 0.78rem;
    color: #aaa;
    font-weight: 500;
    margin-top: 0.2rem;
}

/* =====================================================
   section heading
   ===================================================== */

.cd-section-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 1.1rem;
    flex-wrap: wrap;
    gap: 0.25rem;
}

.cd-section-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #130610;
    margin: 0;
}

.cd-section-sub {
    font-size: 0.82rem;
    color: #bbb;
    margin: 0;
}

/* =====================================================
   feature banners
   ===================================================== */

.cd-banners {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
}

.cd-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 20px;
    padding: 1.75rem 2rem;
    cursor: pointer;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
    overflow: hidden;
    position: relative;
    min-height: 130px;
    width: 100%;
    box-sizing: border-box;
}

.cd-banner:hover {
    transform: translateY(-3px);
    box-shadow: 0 18px 48px rgba(0, 0, 0, 0.18);
}

.cd-banner:hover .cd-arrow {
    transform: translateX(5px);
    background: rgba(255, 255, 255, 0.35);
}

/* banner color themes */

.cd-green {
    background: linear-gradient(125deg, #0d5c2e 0%, #1a8c47 60%, #22a855 100%);
    color: #fff;
}

.cd-pink {
    background: linear-gradient(125deg, #ad1457 0%, #e91e63 55%, #f48fb1 100%);
    color: #fff;
}

.cd-amber {
    background: linear-gradient(125deg, #b45309 0%, #d97706 55%, #fbbf24 100%);
    color: #fff;
}

/* left content */

.cd-banner-left {
    display: flex;
    align-items: flex-start;
    gap: 1.2rem;
    flex: 1;
    min-width: 0;
}

.cd-b-icon {
    width: 50px;
    height: 50px;
    border-radius: 13px;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.cd-b-icon svg {
    width: 22px;
    height: 22px;
    stroke: #fff;
}

.cd-b-text {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    min-width: 0;
}

.cd-b-tag {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    opacity: 0.65;
}

.cd-b-title {
    font-size: 1.45rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.01em;
}

.cd-b-desc {
    font-size: 0.86rem;
    opacity: 0.78;
    line-height: 1.6;
    margin: 0.1rem 0 0;
    max-width: 440px;
}

.cd-b-badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.18rem 0.55rem;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.22);
    letter-spacing: 0.5px;
    margin-top: 0.3rem;
    width: fit-content;
}

/* right content */

.cd-banner-right {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    flex-shrink: 0;
    margin-left: 1rem;
}

/* decorative art */

.cd-art {
    position: relative;
    width: 90px;
    height: 72px;
    opacity: 0.3;
    flex-shrink: 0;
}

/* lines: modules */

.cd-art-lines span {
    display: block;
    position: absolute;
    left: 0;
    height: 9px;
    border-radius: 5px;
    background: #fff;
}

.cd-art-lines span:nth-child(1) {
    top: 0;
    width: 100%;
}

.cd-art-lines span:nth-child(2) {
    top: 22px;
    width: 72%;
}

.cd-art-lines span:nth-child(3) {
    top: 44px;
    width: 50%;
}

/* stacked cards: flashcards */

.cd-art-cards span {
    display: block;
    position: absolute;
    width: 68px;
    height: 48px;
    border-radius: 7px;
    background: #fff;
}

.cd-art-cards span:nth-child(1) {
    top: 0;
    left: 16px;
    transform: rotate(-8deg);
}

.cd-art-cards span:nth-child(2) {
    top: 8px;
    left: 8px;
    transform: rotate(-2deg);
}

.cd-art-cards span:nth-child(3) {
    top: 14px;
    left: 0;
    transform: rotate(4deg);
}

/* circles: exams */

.cd-art-circles span {
    display: block;
    position: absolute;
    border-radius: 50%;
    border: 3px solid #fff;
}

.cd-art-circles span:nth-child(1) {
    width: 58px;
    height: 58px;
    top: 4px;
    left: 8px;
}

.cd-art-circles span:nth-child(2) {
    width: 38px;
    height: 38px;
    top: 18px;
    left: 38px;
    opacity: 0.45;
}

.cd-art-circles em {
    position: absolute;
    font-style: normal;
    font-size: 1.5rem;
    font-weight: 800;
    color: #fff;
    top: 18px;
    left: 25px;
}

/* arrow button */

.cd-arrow {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: transform 0.2s ease, background 0.2s ease;
    flex-shrink: 0;
}

.cd-arrow svg {
    width: 17px;
    height: 17px;
    stroke: #fff;
}

/* =====================================================
   responsive breakpoints
   ===================================================== */

/* tablet */

@media (max-width: 900px) {
    .cd-hero {
        padding: 3.5rem 5vw 3rem;
    }
    .cd-body {
        padding: 2rem 5vw 4rem;
    }
    .cd-stat {
        padding: 1.2rem 1.5rem;
    }
    .cd-b-desc {
        max-width: 280px;
    }
}

/* large mobile */

@media (max-width: 640px) {
    .cd-hero {
        padding: 2.5rem 1.25rem 2.5rem;
    }
    .cd-body {
        padding: 1.5rem 1.25rem 3rem;
    }
    /* stats go vertical */
    .cd-stats {
        flex-direction: column;
        align-items: stretch;
    }
    .cd-stat {
        padding: 1rem 1.25rem;
    }
    .cd-stat-sep {
        width: auto;
        height: 1px;
        margin: 0 1.25rem;
    }
    /* simpler banners */
    .cd-banner {
        padding: 1.25rem;
        min-height: auto;
    }
    .cd-art {
        display: none;
    }
    .cd-b-desc {
        display: none;
    }
    .cd-b-title {
        font-size: 1.2rem;
    }
    .cd-section-head {
        flex-direction: column;
        align-items: flex-start;
    }
}

/* small mobile */

@media (max-width: 400px) {
    .cd-title {
        font-size: 1.5rem;
    }
    .cd-b-title {
        font-size: 1.1rem;
    }
    .cd-banner-right {
        gap: 0.5rem;
        margin-left: 0.5rem;
    }
}
</style>