<template>
    <div class="cd-root">
    
        <div v-if="store.loading" class="cd-state-box">
            <div class="cd-spinner"></div>
            <p class="cd-state-text">Loading course...</p>
        </div>
    
        <div v-else-if="store.error" class="cd-state-box">
            <div class="cd-error-icon">!</div>
            <p class="cd-error-msg">{{ store.error }}</p>
            <button class="cd-btn-back" @click="goToDashboard">Go Back</button>
        </div>
    
        <template v-else-if="store.currentCourse">
      
            <div class="cd-container">
              
              <div class="cd-hero">
                <div class="cd-hero-top">
                  
                  <button class="back-btn" @click="goToDashboard">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M19 12H5M12 5l-7 7 7 7"/>
                    </svg>
                  </button>
    
                  <div class="cd-breadcrumb">
                    <span class="cd-label clickable" @click="goToDashboard">Home</span>
                    <span class="separator">›</span>
                    <span class="cd-label">Course</span>
                  </div>
                </div>
    
                <div class="cd-hero-inner">
                  <h1 class="cd-title">{{ store.currentCourse.title }}</h1>
                  <p v-if="store.currentCourse.description" class="cd-desc">
                    {{ store.currentCourse.description }}
                  </p>
                </div>
              </div>
      
              <div class="cd-body">
      
                <div class="cd-stats">
                  <div class="cd-stat-card">
                    <div class="cd-stat-num">{{ store.currentCourse.module_count ?? 0 }}</div>
                    <div class="cd-stat-lbl">Total Modules</div>
                  </div>
      
                  <div class="cd-stat-card">
                    <div class="cd-stat-num">{{ store.currentCourse.flashcard_set_count ?? 0 }}</div>
                    <div class="cd-stat-lbl">Flashcard Sets</div>
                  </div>
      
                  <div class="cd-stat-card">
                    <div class="cd-stat-num">{{ store.currentCourse.exam_template_count ?? 0 }}</div>
                    <div class="cd-stat-lbl">Total Exams</div>
                  </div>
                </div>
      
                <div class="cd-section-head">
                  <h2 class="cd-section-title">Study Tools</h2>
                </div>
      
                <div class="cd-banners">
      
                  <div class="cd-banner cd-green" @click="router.push({ name: 'ModulesList', params: { courseId: courseId } })">
                    <div class="cd-banner-left">
                      <div class="cd-b-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                          <line x1="9" y1="3" x2="9" y2="21"></line>
                          <path d="M13 8l2 2 4-4"></path>
                        </svg>
                      </div>
                      <div class="cd-b-text">
                        <span class="cd-b-tag">LEARN</span>
                        <h3 class="cd-b-title">Modules</h3>
                        <p class="cd-b-desc">Work through ordered lessons with mini quizzes to test your understanding. <span class="dot">•</span> {{ store.currentCourse.module_count ?? 0 }} available</p>
                      </div>
                    </div>
                    <div class="cd-banner-right">
                      <div class="cd-art cd-art-lines">
                        <span></span><span></span><span></span>
                      </div>
                      <button class="cd-arrow" aria-label="go to modules">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                          <line x1="5" y1="12" x2="19" y2="12"></line>
                          <polyline points="12 5 19 12 12 19"></polyline>
                        </svg>
                      </button>
                    </div>
                  </div>
      
                  <div class="cd-banner cd-pink" @click="router.push(`/flashcards/${courseId}`)">
                    <div class="cd-banner-left">
                      <div class="cd-b-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <rect x="2" y="5" width="20" height="14" rx="2"></rect>
                          <line x1="2" y1="10" x2="22" y2="10"></line>
                        </svg>
                      </div>
                      <div class="cd-b-text">
                        <span class="cd-b-tag">REVIEW</span>
                        <h3 class="cd-b-title">Flashcards</h3>
                        <p class="cd-b-desc">Master key concepts with flashcard sets made by your teacher for fast revision. <span class="dot">•</span> {{ store.currentCourse.flashcard_set_count ?? 0 }} sets</p>
                      </div>
                    </div>
                    <div class="cd-banner-right">
                      <div class="cd-art cd-art-cards">
                        <span></span><span></span><span></span>
                      </div>
                      <button class="cd-arrow" aria-label="go to flashcards">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                          <line x1="5" y1="12" x2="19" y2="12"></line>
                          <polyline points="12 5 19 12 12 19"></polyline>
                        </svg>
                      </button>
                    </div>
                  </div>
      
                  <div class="cd-banner cd-orange" @click="router.push(`/exam/${courseId}`)">
                    <div class="cd-banner-left">
                      <div class="cd-b-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                          <polyline points="14 2 14 8 20 8"></polyline>
                          <line x1="16" y1="13" x2="8" y2="13"></line>
                          <line x1="16" y1="17" x2="8" y2="17"></line>
                        </svg>
                      </div>
                      <div class="cd-b-text">
                        <span class="cd-b-tag">PRACTICE TEST</span>
                        <h3 class="cd-b-title">Exams</h3>
                        <p class="cd-b-desc">Practice with past midterm and final exam question banks to build confidence. <span class="dot">•</span> {{ store.currentCourse.exam_template_count ?? 0 }} exams</p>
                      </div>
                    </div>
                    <div class="cd-banner-right">
                      <div class="cd-art cd-art-circles">
                        <span></span><span></span>
                        <em>✓</em>
                      </div>
                      <button class="cd-arrow" aria-label="go to exams">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                          <line x1="5" y1="12" x2="19" y2="12"></line>
                          <polyline points="12 5 19 12 12 19"></polyline>
                        </svg>
                      </button>
                    </div>
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

const goToDashboard = () => {
    router.push('/dashboard')
}

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
 Root Layout
 ===================================================== */

.cd-root {
    width: 100%;
    min-height: 100vh;
    background: linear-gradient( 90deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
    font-family: 'DM Sans', 'Outfit', 'Segoe UI', sans-serif;
    padding: 2rem;
    box-sizing: border-box;
}

.cd-container {
    max-width: 1100px;
    margin: 0 auto;
}

/* ---- loading / error states ---- */

.cd-state-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    gap: 1rem;
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
    color: #6b7280;
    font-weight: 500;
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
    font-weight: 500;
}

.cd-btn-back {
    padding: 0.6rem 1.5rem;
    border-radius: 10px;
    border: none;
    background: #df4a7d;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
}

/* =====================================================
 Hero: Pink rounded banner
 ===================================================== */

.cd-hero {
    background: linear-gradient(135deg, #df4a7d 0%, #c83264 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    color: #fff;
    margin-bottom: 2rem;
    box-shadow: 0 10px 25px rgba(223, 74, 125, 0.15);
}

.cd-hero-top {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.back-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.4);
    background: transparent;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    padding: 0;
    flex-shrink: 0;
}

.back-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.6);
}

.cd-breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    font-weight: 600;
    opacity: 0.9;
}

.cd-label.clickable {
    cursor: pointer;
    transition: opacity 0.2s;
}

.cd-label.clickable:hover {
    opacity: 0.7;
    text-decoration: underline;
}

.separator {
    font-size: 1.2rem;
}

.cd-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0 0 0.5rem;
    letter-spacing: -0.01em;
}

.cd-desc {
    font-size: 0.95rem;
    opacity: 0.9;
    margin: 0;
    max-width: 600px;
    line-height: 1.6;
}

/* =====================================================
 Stats: Separate white cards
 ===================================================== */

.cd-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
    margin-bottom: 2.5rem;
}

.cd-stat-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.cd-stat-num {
    font-size: 2.2rem;
    font-weight: 800;
    color: #1f2937;
    line-height: 1;
    margin-bottom: 0.4rem;
}

.cd-stat-lbl {
    font-size: 0.85rem;
    color: #6b7280;
    font-weight: 600;
}

/* =====================================================
 Section Heading
 ===================================================== */

.cd-section-head {
    margin-bottom: 1.25rem;
}

.cd-section-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #1f2937;
    margin: 0;
}

/* =====================================================
 Feature Banners
 ===================================================== */

.cd-banners {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.cd-banner {
    border-radius: 16px;
    padding: 1.5rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    color: #ffffff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}

.cd-banner:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.cd-banner:hover .cd-arrow {
    background: rgba(255, 255, 255, 0.3);
    transform: translateX(5px);
}

.cd-green {
    background: linear-gradient(135deg, #357a44 0%, #4db15f 100%);
}

.cd-pink {
    background: linear-gradient(135deg, #b42158 0%, #df4c82 100%);
}

.cd-orange {
    background: linear-gradient(135deg, #c97924 0%, #eeb141 100%);
}

/* Left Content */

.cd-banner-left {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    flex: 1;
    z-index: 2;
}

.cd-b-icon {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.cd-b-icon svg {
    width: 26px;
    height: 26px;
    color: #ffffff;
}

.cd-b-text {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.cd-b-tag {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.85;
}

.cd-b-title {
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.01em;
}

.cd-b-desc {
    font-size: 0.9rem;
    margin: 0;
    font-weight: 400;
    opacity: 0.95;
}

.cd-b-desc .dot {
    margin: 0 0.4rem;
    opacity: 0.5;
}

/* Right Content */

.cd-banner-right {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-left: 1rem;
    z-index: 2;
}

.cd-arrow {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.15);
    border: none;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    flex-shrink: 0;
}

.cd-arrow svg {
    width: 20px;
    height: 20px;
}

/* =====================================================
 Decorative Art 
 ===================================================== */

.cd-art {
    position: relative;
    width: 90px;
    height: 72px;
    opacity: 0.25;
    flex-shrink: 0;
}

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

/* =====================================================
 Responsive
 ===================================================== */

@media (max-width: 860px) {
    .cd-stats {
        grid-template-columns: 1fr;
        gap: 0.75rem;
    }
    .cd-b-desc {
        max-width: 280px;
    }
}

@media (max-width: 640px) {
    .cd-root {
        padding: 1rem;
    }
    .cd-hero {
        padding: 1.5rem;
    }
    .cd-banner {
        padding: 1.25rem;
    }
    .cd-banner-left {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    .cd-b-icon {
        width: 48px;
        height: 48px;
    }
    .cd-b-desc {
        display: none;
    }
    .cd-art {
        display: none;
    }
}
</style>