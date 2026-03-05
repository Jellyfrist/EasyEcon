<template>
    <div class="page-wrapper">
    
        <!-- top section -->
        <div class="grid-2 mb-4">
    
            <!-- left: greeting -->
            <section>
                <h1>{{ greeting }}, {{ authStore.fullName }} 👋</h1>
                <p class="text-muted mt-2">Welcome back to your teaching dashboard.</p>
                <button class="btn btn-primary mt-4" @click="router.push('/teacher/courses/create')">
              + Create Course
            </button>
            </section>
    
            <!-- right: stats from store.courses -->
            <section>
                <div class="card">
                    <h2>You currently manage</h2>
                    <div class="grid-3 mt-4">
    
                        <div class="text-center">
                            <h1>{{ courseStore.courses.length }}</h1>
                            <p class="text-muted">Courses</p>
                        </div>
    
                        <div class="text-center">
                            <h1>{{ totalFlashcardSets }}</h1>
                            <p class="text-muted">Flashcard Sets</p>
                        </div>
    
                        <div class="text-center">
                            <h1>{{ totalExams }}</h1>
                            <p class="text-muted">Exam Templates</p>
                        </div>
    
                    </div>
                </div>
            </section>
    
        </div>
    
        <!-- course list -->
        <section>
            <h2 class="mb-4">My Courses</h2>
    
            <!-- loading state -->
            <div v-if="courseStore.loading" class="card text-center">
                <p class="text-muted">Loading courses...</p>
            </div>
    
            <!-- error state -->
            <div v-else-if="courseStore.error" class="card text-center">
                <p class="text-muted">{{ courseStore.error }}</p>
                <button class="btn btn-primary mt-2" @click="courseStore.fetchMyCourses()">
              Try Again
            </button>
            </div>
    
            <!-- course cards -->
            <div v-else-if="courseStore.courses.length > 0" class="grid-2">
                <div v-for="course in courseStore.courses" :key="course.id" class="card">
                    <p class="text-muted">Course Overview</p>
    
                    <h3 class="mt-2">{{ course.title }}</h3>
    
                    <p class="text-muted mt-2">{{ course.description || 'No description.' }}</p>
    
                    <!-- count badges from CourseResponse -->
                    <div class="count-row mt-2">
                        <span class="count-badge">📚 {{ course.module_count ?? 0 }} modules</span>
                        <span class="count-badge">🃏 {{ course.flashcard_set_count ?? 0 }} sets</span>
                        <span class="count-badge">📝 {{ course.exam_template_count ?? 0 }} exams</span>
                    </div>
    
                    <button class="btn btn-green mt-4" @click="router.push(`/teacher/courses/${course.id}/edit`)">
                Edit Course
              </button>
                </div>
            </div>
    
            <!-- empty state -->
            <div v-else class="card text-center">
                <h3>No courses yet</h3>
                <p class="text-muted mt-2">Create your first course to get started.</p>
                <button class="btn btn-primary mt-4" @click="router.push('/teacher/courses/create')">
              + Create Course
            </button>
            </div>
    
        </section>
    
    </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'
import { useCourseStore } from '@/store/courseStore'

const router = useRouter()
const authStore = useAuthStore()
const courseStore = useCourseStore()

// greeting based on time of day
const greeting = computed(() => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good Morning'
    if (hour < 18) return 'Good Afternoon'
    return 'Good Evening'
})

// sum all flashcard_set_count from each course in the list
const totalFlashcardSets = computed(() =>
    courseStore.courses.reduce((sum, c) => sum + (c.flashcard_set_count ?? 0), 0)
)

// sum all exam_template_count from each course in the list
const totalExams = computed(() =>
    courseStore.courses.reduce((sum, c) => sum + (c.exam_template_count ?? 0), 0)
)

// load teacher's own courses on mount
// store.fetchMyCourses -> GET /courses (teacher, returns CourseResponse with counts)
onMounted(async () => {
    await courseStore.fetchMyCourses()
})
</script>

<style scoped>
/* count badges inside course card */

.count-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.count-badge {
    background: var(--gray-light);
    color: var(--text-muted);
    font-size: 0.8rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 999px;
}
</style>