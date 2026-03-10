<template>
  <div class="flashcard-dashboard">
  
      <div class="header-container">
          <div class="page-header-card">
              <div class="breadcrumb-row">
                  <button class="back-btn" @click="goToCourses">
                      <span class="material-symbols-outlined">arrow_back</span>
                  </button>
                  <span class="breadcrumb-text">Course <span class="material-symbols-outlined breadcrumb-arrow">chevron_right</span> <strong>Flashcard Sets</strong></span>
              </div>
              
              <h1 class="header-title">Flashcard Sets</h1>
              <p class="header-subtitle">
                  Select a flashcard set to start studying.
              </p>
          </div>
      </div>
  
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
  
      <div v-else-if="store.error" class="state-container">
          <div class="state-box error-box">
              <span class="state-icon">⚠️</span>
              <p class="state-title">Something went wrong</p>
              <p class="state-desc">{{ store.error }}</p>
          </div>
      </div>
  
      <div v-else-if="store.sets.length === 0" class="state-container">
          <div class="state-box empty-box">
              <span class="state-icon">📭</span>
              <p class="state-title">No flashcards found</p>
              <p class="state-desc">Your teacher hasn't added any flashcard sets for this course yet. Check back later!</p>
          </div>
      </div>
  
      <div v-else class="sets-grid">
          <div 
            v-for="(set, index) in store.sets" 
            :key="set.id" 
            class="set-card" 
            :style="{ '--accent': accentColor(index) }" 
            @click="goToStudy(set.id)"
          >
              <div class="card-stripe"></div>
  
              <div class="card-body">
                  <div class="card-top">
                      <div class="set-icon">{{ setIcon(index) }}</div>
                      <div class="card-titles">
                          <h3 class="card-title">{{ set.title }}</h3>
                          <p class="card-teacher" v-if="set.teacher_name">
                              <span class="teacher-label">by</span> {{ set.teacher_name }}
                          </p>
                      </div>
                  </div>
  
                  <p class="card-desc">{{ set.description || 'No description provided for this flashcard set.' }}</p>
  
                  <div class="progress-section">
                      <div class="progress-row">
                          <span class="progress-label">PROGRESS</span>
                          <span class="progress-count">{{ set.known_count ?? 0 }} / {{ set.card_count ?? 0 }} cards</span>
                      </div>
                      <div class="progress-track">
                          <div class="progress-fill" :style="{ width: progressPercent(set) + '%' }"></div>
                      </div>
                  </div>
  
                  <div class="card-footer">
                      <span class="card-count-pill">{{ set.card_count ?? 0 }} Cards</span>
                      <button class="study-btn" @click.stop="goToStudy(set.id)">
                          Study now
                          <span class="material-symbols-outlined btn-arrow">arrow_forward</span>
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

const accents = [
  '#df4a7d', // Primary Pink
  '#f59e0b', // Amber
  '#10b981', // Emerald
  '#8b5cf6', // Violet
  '#3b82f6', // Blue
  '#f43f5e', // Rose
  '#14b8a6', // Teal
  '#ec4899', // Pink
]

function accentColor(index) {
  return accents[index % accents.length]
}

const icons = ['📘', '📗', '📙', '📕', '📓', '📔', '📒', '📃']

function setIcon(index) {
  return icons[index % icons.length]
}

function progressPercent(set) {
  const total = set.card_count ?? 0
  const known = set.known_count ?? 0
  if (total === 0) return 0
  return Math.min(100, Math.round((known / total) * 100))
}

function goToStudy(setId) {
  router.push({ name: 'FlashcardStudy', params: { courseId: route.params.courseId, setId } })
}

function goToCourses() {
  router.push(`/courses/${courseId.value}`);
}

onMounted(async () => {
  store.sets = []
  if (!courseId.value) return

  await Promise.all([
      courseStore.viewCourse(courseId.value),
      store.browseSets(courseId.value),
  ])

  await Promise.all(
      store.sets.map(async (set) => {
          try {
              const res = await flashcardService.getSetProgress(set.id)
              set.known_count = res.data.known_count ?? 0
          } catch {
              set.known_count = 0
          }
      })
  )
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=Sarabun:wght@400;500;600;700;800&display=swap');

/* =====================================================
 Base Layout
 ===================================================== */
.flashcard-dashboard {
  min-height: 100vh;
  background: linear-gradient(90deg, #fffcec, #e8dfbf, #ffc7db, #fff8d0);
  font-family: 'DM Sans', 'Sarabun', sans-serif;
  padding-bottom: 4rem;
}

.material-symbols-outlined {
  vertical-align: middle;
}

/* =====================================================
 Page Header 
 ===================================================== */
.header-container {
  padding: 2rem;
  display: flex;
  justify-content: center;
}

.page-header-card {
  width: 100%;
  max-width: 1100px;
  background: linear-gradient(135deg, var(--primary-pink) 0%, #f06292 100%);
  border-radius: 20px;
  padding: 2rem 2.5rem;
  color: white;
  box-shadow: 0 10px 30px rgba(192, 80, 114, 0.2);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.breadcrumb-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: 1.5px solid rgba(255, 255, 255, 0.6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  padding: 0;
}

.back-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: white;
}

.breadcrumb-text {
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  opacity: 0.9;
}

.breadcrumb-arrow {
  font-size: 18px;
  opacity: 0.7;
}

.breadcrumb-text strong {
  font-weight: 800;
  color: white;
  opacity: 1;
}

.header-title {
  font-size: 3rem;
  font-weight: 900;
  margin: 0;
  letter-spacing: -0.02em;
}

.header-subtitle {
  font-size: 1.1rem;
  margin: 0;
  font-weight: 500;
  opacity: 0.9;
}

/* =====================================================
 2-Column Grid
 ===================================================== */
.sets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 2rem;
}

@media (max-width: 768px) {
  .sets-grid {
      grid-template-columns: 1fr;
      padding: 0 1.5rem;
  }
  .header-container { padding: 1.5rem; }
  .page-header-card { padding: 2rem 1.5rem; }
  .header-title { font-size: 2.2rem; }
}

/* =====================================================
 Set Card
 ===================================================== */
.set-card {
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #ffffff;
  display: flex;
  flex-direction: column;
}

.set-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(223, 74, 125, 0.1);
  border-color: #fce4ec;
}

/* Colored stripe */
.card-stripe {
  height: 8px;
  background: var(--accent);
  width: 100%;
  flex-shrink: 0;
}

.card-body {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  flex: 1;
}

/* Top Row */
.card-top {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.set-icon {
  font-size: 2.2rem;
  line-height: 1;
  flex-shrink: 0;
  background: #f9fafb;
  padding: 12px;
  border-radius: 16px;
}

.card-titles {
  flex: 1;
  min-width: 0;
  padding-top: 4px;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #111827;
  margin: 0 0 4px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-teacher {
  font-size: 0.85rem;
  color: #9ca3af;
  margin: 0;
  font-weight: 500;
}

.teacher-label { color: #d1d5db; }

/* Description */
.card-desc {
  font-size: 0.95rem;
  color: #6b7280;
  margin: 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Progress Section */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #faf9f7;
  padding: 1rem;
  border-radius: 16px;
  border: 1px solid #f3f4f6;
}

.progress-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-label {
  font-size: 0.75rem;
  font-weight: 800;
  color: #9ca3af;
  letter-spacing: 0.05em;
}

.progress-count {
  font-size: 0.85rem;
  color: #4b5563;
  font-weight: 700;
}

.progress-track {
  height: 8px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 999px;
  transition: width 0.6s ease;
}

/* Card Footer */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 0.5rem;
}

.card-count-pill {
  font-size: 0.8rem;
  font-weight: 700;
  color: #6b7280;
  background: #f3f4f6;
  padding: 6px 14px;
  border-radius: 999px;
}

.study-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 99px; /* Pill shape */
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.study-btn:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.btn-arrow {
  font-size: 1.2rem;
  transition: transform 0.2s ease;
}

.study-btn:hover .btn-arrow {
  transform: translateX(4px);
}

/* =====================================================
 Skeleton Loading
 ===================================================== */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 2rem;
}

.skeleton-card {
  background: #ffffff;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02);
}

.skeleton-stripe {
  height: 8px;
  background: #f3f4f6;
  animation: shimmer 1.5s infinite;
}

.skeleton-body {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.skeleton-line {
  height: 16px;
  border-radius: 8px;
  background: #f3f4f6;
  animation: shimmer 1.5s infinite;
}

.skeleton-line.short { width: 30%; height: 24px; margin-bottom: 8px; }
.skeleton-line.medium { width: 70%; }
.skeleton-line.long { width: 100%; }

@keyframes shimmer {
  0% { opacity: 0.5; background-color: #f3f4f6; }
  50% { opacity: 1; background-color: #e5e7eb; }
  100% { opacity: 0.5; background-color: #f3f4f6; }
}

/* =====================================================
 Empty / Error States
 ===================================================== */
.state-container {
  display: flex;
  justify-content: center;
  padding: 4rem 2rem;
}

.state-box {
  text-align: center;
  max-width: 400px;
  background: #ffffff;
  padding: 3rem;
  border-radius: 24px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.03);
}

.state-icon {
  font-size: 3.5rem;
  display: block;
  margin-bottom: 1.25rem;
}

.state-title {
  font-size: 1.4rem;
  font-weight: 800;
  color: #111827;
  margin: 0 0 10px;
}

.state-desc {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
  line-height: 1.6;
}

.error-box .state-title { color: #ef4444; }
</style>