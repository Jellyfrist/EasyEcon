<template>
    <div class="page-wrapper">
    
        <!-- form card: create or edit course -->
        <div class="card form-card">
            <h2 class="form-title">
                {{ isEditMode ? 'Edit Course' : 'Create New Course' }}
            </h2>
    
            <div class="form-group">
                <label>Course Title</label>
                <input v-model="title" class="input-field" type="text" placeholder="e.g. Microeconomics 101" maxlength="50" :disabled="store.loading" />
            </div>
    
            <div class="form-group">
                <label>Description</label>
                <textarea v-model="description" class="input-field" placeholder="Short description of the course..." rows="4" :disabled="store.loading" />
            </div>
    
            <div v-if="store.error" class="error-msg">{{ store.error }}</div>
    
            <div class="btn-row">
                <button class="btn btn-primary" :disabled="store.loading || !title.trim()" @click="handleSubmit">
              {{ store.loading ? 'Saving...' : (isEditMode ? 'Update Course' : 'Create Course') }}
            </button>
    
                <button v-if="isEditMode" class="btn btn-danger" :disabled="store.loading" @click="handleDelete">
              Delete Course
            </button>
    
                <button class="btn btn-outline" :disabled="store.loading" @click="router.back()">
              Cancel
            </button>
            </div>
        </div>
    
        <!-- quick action cards: show in edit mode always (even while loading) -->
        <!-- fix: use isEditMode only, not store.currentCourse, so cards appear right after redirect -->
        <div v-if="isEditMode" class="grid-3 mt-4">
    
            <!-- flashcard: route matches /flashcards/:courseId/edit/:setId? in index.js -->
            <!-- card click: go to flashcard dashboard for this course -->
            <!-- button click: go to create new flashcard set (no setId = create mode) -->
            <div class="card action-card" @click="router.push({ name: 'TeacherFlashcardDashboard', params: { courseId: courseId } })">
                <div class="card-icon">🃏</div>
                <h3>Flashcard Sets</h3>
                <p class="text-muted">Stand-alone flashcard topics for this course.</p>
                <span class="count-badge">
              {{ store.currentCourse?.flashcard_set_count ?? 0 }} sets
            </span>
                <button class="btn btn-outline mt-2" @click.stop="router.push({ name: 'FlashcardEditor', params: { courseId: courseId } })">
              + New Flashcard Set
            </button>
            </div>
    
            <!-- module: no route yet, disabled -->
            <div class="card action-card">
                <div class="card-icon">📚</div>
                <h3>Modules</h3>
                <p class="text-muted">Ordered lessons with mini quizzes.</p>
                <span class="count-badge">
              {{ store.currentCourse?.module_count ?? 0 }} modules
            </span>
                <button class="btn btn-outline mt-2" disabled>
              + New Module
            </button>
            </div>
    
            <!-- exam: no route yet, disabled -->
            <div class="card action-card">
                <div class="card-icon">📝</div>
                <h3>Exam Templates</h3>
                <p class="text-muted">Past midterm and final exam question banks.</p>
                <span class="count-badge">
              {{ store.currentCourse?.exam_template_count ?? 0 }} exams
            </span>
                <button class="btn btn-outline mt-2" disabled>
              + New Exam
            </button>
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
.form-card {
    max-width: 680px;
    margin: 0 auto 2rem;
}

.form-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text-main);
    margin-bottom: 1.5rem;
}

textarea.input-field {
    resize: vertical;
}

.btn-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
}

.btn-danger {
    background-color: #ef4444;
    color: white;
    border: none;
}

.btn-danger:hover {
    background-color: #dc2626;
}

.error-msg {
    color: #ef4444;
    font-size: 0.875rem;
    background: #fef2f2;
    border-radius: var(--radius-md);
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
}

.action-card {
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.card-icon {
    font-size: 2rem;
    margin-bottom: 0.25rem;
}

.action-card h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-main);
}

.count-badge {
    display: inline-block;
    background: var(--gray-light);
    color: var(--text-main);
    font-weight: 700;
    font-size: 0.875rem;
    padding: 4px 12px;
    border-radius: 999px;
    width: fit-content;
}

@media (max-width: 768px) {
    .btn-row {
        flex-direction: column;
    }
    .btn-row .btn {
        width: 100%;
    }
}
</style>