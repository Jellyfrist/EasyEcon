<template>
    <div class="ce-page">

        <!-- page header -->
        <div class="ce-page-header">
            <div class="ce-breadcrumb">
                <button class="ce-back-btn" @click="router.back()">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Courses
                </button>
                <span class="ce-breadcrumb-sep">/</span>
                <span class="ce-breadcrumb-current">{{ isEditMode ? 'Edit Course' : 'New Course' }}</span>
            </div>
            <h1 class="ce-page-title">{{ isEditMode ? 'Edit Course' : 'Create New Course' }}</h1>
            <p class="ce-page-sub">{{ isEditMode ? 'Update course details and manage course content below.' : 'Fill in the details to create a new course.' }}</p>
        </div>

        <!-- main 2-column layout: form left, action cards right -->
        <div class="ce-layout">

            <!-- left: form -->
            <div class="ce-form-col">
                <div class="ce-card">
                    <div class="ce-card-header">
                        <div class="ce-card-icon">
                            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                                <rect x="2" y="2" width="14" height="14" rx="3" stroke="currentColor" stroke-width="1.75"/>
                                <path d="M5.5 6.5H12.5M5.5 9H10.5M5.5 11.5H9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                            </svg>
                        </div>
                        <span>Course Details</span>
                    </div>

                    <div class="ce-field">
                        <label class="ce-label">
                            Course Title
                            <span class="ce-required">*</span>
                        </label>
                        <input
                            v-model="title"
                            class="ce-input"
                            type="text"
                            placeholder="e.g. Microeconomics 101"
                            maxlength="50"
                            :disabled="store.loading"
                        />
                        <span class="ce-char-count">{{ title.length }} / 50</span>
                    </div>

                    <div class="ce-field">
                        <label class="ce-label">Description</label>
                        <textarea
                            v-model="description"
                            class="ce-input ce-textarea"
                            placeholder="Short description of the course..."
                            rows="4"
                            :disabled="store.loading"
                        />
                    </div>

                    <div v-if="store.error" class="ce-error">
                        <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                            <circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M7.5 4.5V8M7.5 10.5V11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                        {{ store.error }}
                    </div>

                    <div class="ce-form-actions">
                        <button
                            class="ce-btn ce-btn-primary"
                            :disabled="store.loading || !title.trim()"
                            @click="handleSubmit"
                        >
                            <svg v-if="store.loading" class="ce-spin" width="15" height="15" viewBox="0 0 15 15" fill="none">
                                <circle cx="7.5" cy="7.5" r="6" stroke="currentColor" stroke-width="2" stroke-dasharray="28" stroke-dashoffset="10"/>
                            </svg>
                            {{ store.loading ? 'Saving...' : (isEditMode ? 'Update Course' : 'Create Course') }}
                        </button>
                        <button class="ce-btn ce-btn-ghost" :disabled="store.loading" @click="router.back()">
                            Cancel
                        </button>
                    </div>
                </div>

                <!-- danger zone: only in edit mode -->
                <div v-if="isEditMode" class="ce-danger-zone">
                    <div class="ce-danger-header">
                        <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                            <path d="M7.5 1.5L13.5 12.5H1.5L7.5 1.5Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                            <path d="M7.5 6V9M7.5 10.5V11.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                        Danger Zone
                    </div>
                    <div class="ce-danger-row">
                        <div class="ce-danger-info">
                            <strong>Delete this course</strong>
                            <span>Permanently removes the course and all its content. This cannot be undone.</span>
                        </div>
                        <button
                            class="ce-btn ce-btn-danger"
                            :disabled="store.loading"
                            @click="handleDelete"
                        >
                            Delete Course
                        </button>
                    </div>
                </div>
            </div>

            <!-- right: action cards (only in edit mode) -->
            <div v-if="isEditMode" class="ce-action-col">
                <p class="ce-action-label">Course Content</p>

                <!-- flashcard sets card -->
                <div
                    class="ce-action-card"
                    @click="router.push({ name: 'TeacherFlashcardDashboard', params: { courseId: courseId } })"
                >
                    <div class="ce-action-top">
                        <div class="ce-action-icon ce-icon-blue">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <rect x="2" y="5" width="13" height="9" rx="2" stroke="currentColor" stroke-width="1.75"/>
                                <rect x="5" y="3" width="13" height="9" rx="2" stroke="currentColor" stroke-width="1.75"/>
                            </svg>
                        </div>
                        <svg class="ce-action-arrow" width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    <h3 class="ce-action-title">Flashcard Sets</h3>
                    <p class="ce-action-desc">Stand-alone flashcard topics for this course.</p>
                    <div class="ce-action-footer">
                        <span class="ce-count-pill">{{ store.currentCourse?.flashcard_set_count ?? 0 }} sets</span>
                        <button
                            class="ce-action-new"
                            @click.stop="router.push({ name: 'FlashcardEditor', params: { courseId: courseId } })"
                        >
                            + New Set
                        </button>
                    </div>
                </div>

                <!-- modules card -->
                <div
                    class="ce-action-card"
                    @click="router.push({ name: 'TeacherLearningDashboard', params: { courseId: courseId } })"
                >
                    <div class="ce-action-top">
                        <div class="ce-action-icon ce-icon-amber">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <rect x="3" y="3" width="14" height="14" rx="2.5" stroke="currentColor" stroke-width="1.75"/>
                                <path d="M7 7H13M7 10H13M7 13H10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                            </svg>
                        </div>
                    </div>
                    <h3 class="ce-action-title">Modules</h3>
                    <p class="ce-action-desc">Ordered lessons with mini quizzes.</p>
                    <div class="ce-action-footer">
                        <span class="ce-count-pill">{{ store.currentCourse?.module_count ?? 0 }} modules</span>
                        <button
                            class="ce-action-new"
                            @click.stop="router.push({ name: 'LearningModule', params: { courseId: courseId } })"
                        >+ New Module</button>
                    </div>
                </div>

                <!-- exam templates card -->
                <div
                    class="ce-action-card"
                    @click="router.push({ name: 'TeacherExamDashboard', params: { courseId: courseId } })"
                >
                    <div class="ce-action-top">
                        <div class="ce-action-icon ce-icon-green">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M6 3H14C15.1 3 16 3.9 16 5V17L13 15.5L10 17L7 15.5L4 17V5C4 3.9 4.9 3 6 3Z" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/>
                                <path d="M8 8H12M8 11H11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                            </svg>
                        </div>
                        <svg class="ce-action-arrow" width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    <h3 class="ce-action-title">Exam Templates</h3>
                    <p class="ce-action-desc">Past midterm and final exam question banks.</p>
                    <div class="ce-action-footer">
                        <span class="ce-count-pill">{{ store.currentCourse?.exam_template_count ?? 0 }} exams</span>
                        <button
                            class="ce-action-new"
                            @click.stop="router.push({ name: 'ExamEditor', params: { courseId: courseId } })"
                        >
                            + New Exam
                        </button>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { onMounted, onUnmounted, watch, ref, computed } from 'vue'
import { useCourseStore } from '@/store/courseStore'

const route = useRoute()
const router = useRouter()
const store = useCourseStore()

// detect create or edit mode from route param
const courseId = computed(() => route.params.courseId)
const isEditMode = computed(() => !!courseId.value)

// local form fields
const title = ref('')
const description = ref('')

// load course data and fill form fields
// store.fetchCourse -> GET /courses/:courseId (teacher view)
async function loadCourse() {
    await store.fetchCourse(courseId.value)
    if (store.currentCourse) {
        title.value = store.currentCourse.title
        description.value = store.currentCourse.description ?? ''
    }
}

// load on mount when in edit mode
onMounted(async () => {
    if (isEditMode.value) await loadCourse()
})

// watch courseId: when router.replace() changes the id after create,
// the component is reused (not remounted), so we need to reload manually
watch(courseId, async (newId) => {
    if (newId) await loadCourse()
})

// clear currentCourse when leaving the page
onUnmounted(() => {
    store.clearCurrent()
})

// create: store.createCourse -> POST /courses
// update: store.updateCourse -> PATCH /courses/:courseId
const handleSubmit = async () => {
    if (!title.value.trim()) return

    const payload = {
        title: title.value.trim(),
        description: description.value.trim() || null
    }

    if (!isEditMode.value) {
        const created = await store.createCourse(payload)
        // redirect to edit page so action cards appear and teacher can add content
        if (created) router.replace(`/teacher/courses/${created.id}/edit`)
    } else {
        // store also refreshes currentCourse so counts stay accurate
        await store.updateCourse(Number(courseId.value), payload)
    }
}

// store.deleteCourse -> DELETE /courses/:courseId
const handleDelete = async () => {
    if (!confirm('Are you sure? All content in this course will be deleted.')) return

    const ok = await store.deleteCourse(Number(courseId.value))
    if (ok) router.push('/teacher')
}
</script>

<style scoped>
/* ---- page shell ---- */
.ce-page {
    min-height: 100vh;
    background: #f8f9fb;
    padding: 2rem 2.5rem 4rem;
    font-family: 'DM Sans', 'Helvetica Neue', sans-serif;
}

/* ---- page header ---- */
.ce-page-header {
    margin-bottom: 2rem;
}

.ce-breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    font-size: 0.8rem;
    color: #94a3b8;
}

.ce-back-btn {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    background: none;
    border: none;
    color: #64748b;
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    padding: 0;
    transition: color 0.15s;
}

.ce-back-btn:hover {
    color: #1e293b;
}

.ce-breadcrumb-sep {
    color: #cbd5e1;
}

.ce-breadcrumb-current {
    color: #475569;
    font-weight: 500;
}

.ce-page-title {
    font-size: 1.65rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin: 0 0 0.35rem;
}

.ce-page-sub {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0;
}

/* ---- 2-column layout ---- */
.ce-layout {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 1.75rem;
    align-items: start;
}

/* ---- form column ---- */
.ce-form-col {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

/* ---- shared card base ---- */
.ce-card {
    background: #ffffff;
    border: 1px solid #e8edf3;
    border-radius: 14px;
    padding: 1.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
}

.ce-card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.8rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #f1f5f9;
}

.ce-card-icon {
    display: flex;
    align-items: center;
    color: #94a3b8;
}

/* ---- form fields ---- */
.ce-field {
    margin-bottom: 1.25rem;
    position: relative;
}

.ce-label {
    display: block;
    font-size: 0.825rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.45rem;
    letter-spacing: 0.01em;
}

.ce-required {
    color: #f43f5e;
    margin-left: 2px;
}

.ce-input {
    width: 100%;
    padding: 0.65rem 0.9rem;
    font-size: 0.9rem;
    color: #1e293b;
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 9px;
    outline: none;
    transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
    box-sizing: border-box;
    font-family: inherit;
}

.ce-input:focus {
    border-color: #6366f1;
    background: #ffffff;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.ce-input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.ce-textarea {
    resize: vertical;
    min-height: 110px;
    line-height: 1.6;
}

.ce-char-count {
    position: absolute;
    right: 0;
    top: 0;
    font-size: 0.75rem;
    color: #94a3b8;
}

/* ---- error ---- */
.ce-error {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #fff1f2;
    border: 1px solid #fecdd3;
    color: #e11d48;
    font-size: 0.85rem;
    padding: 0.75rem 1rem;
    border-radius: 9px;
    margin-bottom: 1.25rem;
}

/* ---- form action buttons ---- */
.ce-form-actions {
    display: flex;
    gap: 0.75rem;
    padding-top: 0.5rem;
}

.ce-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.6rem 1.25rem;
    font-size: 0.875rem;
    font-weight: 600;
    border-radius: 9px;
    border: none;
    cursor: pointer;
    transition: all 0.15s;
    font-family: inherit;
    white-space: nowrap;
}

.ce-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.ce-btn-primary {
    background: #4f46e5;
    color: #ffffff;
}

.ce-btn-primary:hover:not(:disabled) {
    background: #4338ca;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    transform: translateY(-1px);
}

.ce-btn-ghost {
    background: transparent;
    color: #64748b;
    border: 1.5px solid #e2e8f0;
}

.ce-btn-ghost:hover:not(:disabled) {
    background: #f8fafc;
    color: #1e293b;
    border-color: #cbd5e1;
}

.ce-btn-danger {
    background: #fff1f2;
    color: #e11d48;
    border: 1.5px solid #fecdd3;
    padding: 0.55rem 1.1rem;
    font-size: 0.825rem;
}

.ce-btn-danger:hover:not(:disabled) {
    background: #e11d48;
    color: #ffffff;
    border-color: #e11d48;
}

/* ---- spinner ---- */
@keyframes ce-spin {
    to { transform: rotate(360deg); }
}

.ce-spin {
    animation: ce-spin 0.8s linear infinite;
}

/* ---- danger zone ---- */
.ce-danger-zone {
    background: #ffffff;
    border: 1.5px solid #fecdd3;
    border-radius: 14px;
    padding: 1.25rem 1.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.ce-danger-header {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.78rem;
    font-weight: 700;
    color: #e11d48;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 1rem;
}

.ce-danger-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
}

.ce-danger-info {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}

.ce-danger-info strong {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1e293b;
}

.ce-danger-info span {
    font-size: 0.8rem;
    color: #94a3b8;
    line-height: 1.4;
}

/* ---- action column ---- */
.ce-action-col {
    display: flex;
    flex-direction: column;
    gap: 0.875rem;
    position: sticky;
    top: 1.5rem;
}

.ce-action-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin: 0 0 0.1rem;
}

/* ---- action cards ---- */
.ce-action-card {
    background: #ffffff;
    border: 1.5px solid #e8edf3;
    border-radius: 14px;
    padding: 1.25rem;
    cursor: pointer;
    transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.ce-action-card:hover {
    border-color: #c7d2fe;
    box-shadow: 0 4px 16px rgba(99,102,241,0.1);
    transform: translateY(-2px);
}

.ce-action-card-disabled {
    opacity: 0.65;
    cursor: default;
}

.ce-action-card-disabled:hover {
    transform: none;
    border-color: #e8edf3;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.ce-action-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
}

.ce-action-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.ce-icon-blue {
    background: #eff6ff;
    color: #3b82f6;
}

.ce-icon-amber {
    background: #fffbeb;
    color: #f59e0b;
}

.ce-icon-green {
    background: #f0fdf4;
    color: #22c55e;
}

.ce-action-arrow {
    color: #cbd5e1;
    transition: color 0.15s, transform 0.15s;
}

.ce-action-card:hover .ce-action-arrow {
    color: #6366f1;
    transform: translateX(2px);
}

.ce-coming-soon {
    font-size: 0.7rem;
    font-weight: 600;
    background: #fef3c7;
    color: #d97706;
    padding: 2px 8px;
    border-radius: 999px;
    letter-spacing: 0.03em;
}

.ce-action-title {
    font-size: 0.925rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0 0 0.3rem;
}

.ce-action-desc {
    font-size: 0.8rem;
    color: #94a3b8;
    margin: 0 0 0.85rem;
    line-height: 1.5;
}

.ce-action-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 0.75rem;
    border-top: 1px solid #f1f5f9;
}

.ce-count-pill {
    font-size: 0.775rem;
    font-weight: 600;
    background: #f1f5f9;
    color: #475569;
    padding: 3px 10px;
    border-radius: 999px;
}

.ce-action-new {
    font-size: 0.775rem;
    font-weight: 600;
    color: #6366f1;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    transition: color 0.15s;
    font-family: inherit;
}

.ce-action-new:hover:not(:disabled) {
    color: #4338ca;
}

.ce-action-new:disabled {
    color: #cbd5e1;
    cursor: not-allowed;
}

/* ---- responsive ---- */
@media (max-width: 900px) {
    .ce-page {
        padding: 1.5rem 1.25rem 3rem;
    }

    .ce-layout {
        grid-template-columns: 1fr;
    }

    .ce-action-col {
        position: static;
    }

    .ce-danger-row {
        flex-direction: column;
        align-items: flex-start;
    }

    .ce-btn-danger {
        width: 100%;
        justify-content: center;
    }
}

@media (max-width: 480px) {
    .ce-form-actions {
        flex-direction: column;
    }

    .ce-form-actions .ce-btn {
        width: 100%;
        justify-content: center;
    }
}
</style>