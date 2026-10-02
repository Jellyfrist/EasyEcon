<template>
    <FeaturePage class="ml-root">
    <template #navigation><CourseNavigation :course-id="courseId" current="modules" /></template>
        <EditorHeader inline class="modules-page-heading" title="Modules" :breadcrumbs="[{ label: 'Courses', to: { name: 'Dashboard' } }, { label: 'Course', to: { name: 'Courses', params: { courseId: courseId } } }, { label: 'Modules', to: route.fullPath }]" />

        <div class="ml-container">

            <div class="ml-body">

                <div v-if="loading" class="ml-state">
                    <div class="ml-spinner"></div>
                    <p>Loading modules...</p>
                </div>

                <div v-else-if="error" class="ml-state error-state">
                    <span class="material-symbols-outlined">error_outline</span>
                    <p>{{ error }}</p>
                </div>

                <div v-else-if="modules.length === 0" class="ml-empty">
                    <div class="ml-empty-icon">
                        <span class="material-symbols-outlined">menu_book</span>
                    </div>
                    <h3>No content yet</h3>
                    <p>No modules have been added to this course.<br>Check back later when your instructor publishes content.</p>
                </div>

                <div v-else class="ml-grid">
                    <div v-for="(mod, index) in modules" :key="mod.id" class="ml-card" @click="goToLesson(mod.id)">
                        <div class="ml-card-body">

                            <div class="ml-card-top">
                                <div class="ml-icon-wrapper" :style="{ color: barColors[index % barColors.length], backgroundColor: barColors[index % barColors.length] + '20' }">
                                    <span class="material-symbols-outlined">menu_book</span>
                                </div>

                                <span class="ml-lesson-pill">
                      {{ mod.learning_pages?.length || 0 }} lessons
                    </span>
                            </div>

                            <div class="ml-card-content">
                                <span class="ml-module-num">Module {{ index + 1 }}</span>
                                <h2 class="ml-card-title">{{ mod.title }}</h2>
                            </div>

                            <div class="ml-card-footer">
                                <span class="ml-start-link" :style="{ color: barColors[index % barColors.length] }">
                      Start learning
                      <span class="material-symbols-outlined">arrow_forward</span>
                                </span>
                            </div>

                        </div>
                    </div>
                </div>

            </div>
        </div>
    </FeaturePage>
</template>

<script setup>
import CourseNavigation from '@/components/CourseNavigation.vue'
import EditorHeader from '@/components/EditorHeader.vue'
import FeaturePage from '@/components/FeaturePage.vue'
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import learningService from '@/services/learningService'

const route = useRoute()
const router = useRouter()
const courseId = computed(() => route.params.courseId)

const modules = ref([])
const loading = ref(false)
const error = ref(null)

// accent bar colors using the brand palette
const barColors = [
    '#df4a7d', // Pink
    '#059669', // Emerald Green
    '#ea580c', // Orange
    '#df4a7d',
    '#059669',
    '#ea580c',
]

const loadModules = async () => {
    loading.value = true
    error.value = null
    try {
        const res = await learningService.listModules(courseId.value)
        const fetched = res.data || []

        for (const mod of fetched) {
            try {
                const pRes = await learningService.listPages(mod.id)
                mod.learning_pages = (pRes.data || []).filter(p => p.is_published)
            } catch {
                mod.learning_pages = []
            }
            mod.isExpanded = false
        }
        modules.value = fetched
    } catch (err) {
        console.error('Failed to fetch modules:', err)
        error.value = 'Failed to load modules. Please try again.'
    } finally {
        loading.value = false
    }
}

onMounted(loadModules)

const goToLesson = moduleId => {
    const firstPage = modules.value.find(mod => mod.id === moduleId)?.learning_pages?.[0]
    if (firstPage) {
        router.push({ name: 'LearningChapter', params: { courseId: courseId.value, moduleId, pageId: firstPage.id } })
        return
    }
    router.push({ name: 'LearningDashboard', params: { courseId: courseId.value, moduleId } })
}
</script>

<style scoped>
.modules-page-heading { position: static; }

/* =====================================================
 Root Layout & Background
 ===================================================== */

.ml-container {

    margin: 0 auto;
}

/* =====================================================
 Hero Banner
 ===================================================== */

.ml-breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    font-weight: 600;
    opacity: 0.9;
}

.ml-label.clickable {
    cursor: pointer;
    transition: opacity 0.2s;
}

.ml-label.clickable:hover {
    opacity: 0.7;
    text-decoration: underline;
}

.separator {
    font-size: 1.2rem;
    opacity: 0.8;
}

.ml-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0 0 0.5rem;
    letter-spacing: -0.01em;
}

.ml-desc {
    font-size: 0.95rem;
    opacity: 0.9;
    margin: 0;
    max-width: 600px;
    line-height: 1.6;
}

/* =====================================================
 Body Content
 ===================================================== */

.ml-body {
    padding-bottom: 3rem;
}

/* States */

.ml-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 5rem 0;
    color: var(--theme-fg-6b7280);
    font-weight: 500;
}

.ml-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--theme-border-fce4ec);
    border-top-color: #df4a7d;
    border-radius: 50%;
    animation: ml-spin 0.8s linear infinite;
}

@keyframes ml-spin {
    to {
        transform: rotate(360deg);
    }
}

.error-state {
    background: var(--theme-bg-fef2f2);
    border-radius: 16px;
    color: var(--theme-fg-ef4444);
    padding: 3rem;
    border: 1px dashed var(--theme-border-fecaca);
}

/* Empty State */

.ml-empty {
    text-align: center;
    padding: 5rem 2rem;
    background: rgba(255, 255, 255, 0.7);
    border: 2px dashed var(--theme-border-cbd5e1);
    border-radius: 20px;
    backdrop-filter: blur(8px);
}

.ml-empty-icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: var(--surface);
    color: var(--theme-fg-94a3b8);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.25rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.ml-empty-icon .material-symbols-outlined {
    font-size: 32px;
}

.ml-empty h3 {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--theme-fg-1e293b);
    margin: 0 0 0.5rem;
}

.ml-empty p {
    font-size: 0.95rem;
    color: var(--theme-fg-64748b);
    line-height: 1.6;
    margin: 0;
}

/* =====================================================
 Module Grid & Cards
 ===================================================== */

.ml-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

.ml-card {
    background: var(--surface);
    border: 1px solid var(--theme-border-e5e7eb);
    border-radius: 20px;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.ml-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
    border-color: var(--theme-border-d1d5db);
}

.ml-card-body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    flex: 1;
}

.ml-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;
}

.ml-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.ml-lesson-pill {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--theme-fg-6b7280);
    background: var(--theme-bg-f3f4f6);
    padding: 4px 12px;
    border-radius: 99px;
}

.ml-card-content {
    flex: 1;
}

.ml-module-num {
    display: block;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--theme-fg-9ca3af);
    margin-bottom: 0.5rem;
}

.ml-card-title {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--theme-fg-1f2937);
    margin: 0;
    line-height: 1.4;
}

.ml-card-footer {
    margin-top: 1.5rem;
    border-top: 1px solid var(--theme-border-f3f4f6);
    padding-top: 1.25rem;
}

.ml-start-link {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.9rem;
    font-weight: 800;
    transition: gap 0.2s ease;
}

.ml-start-link .material-symbols-outlined {
    font-size: 18px;
}

.ml-card:hover .ml-start-link {
    gap: 10px;
}

/* =====================================================
 Responsive
 ===================================================== */

@media (max-width: 768px) {

    .ml-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .ml-title {
        font-size: 1.8rem;
    }
}
</style>
