// manages course list and current course for both teacher and student

import { defineStore } from 'pinia'
import { ref } from 'vue'
import courseService from '../services/courseService'

export const useCourseStore = defineStore('course', () => {

    // list of courses (teacher: own courses, student: all courses)
    const courses = ref([])

    // currently opened course detail
    const currentCourse = ref(null)

    // loading and error state
    const loading = ref(false)
    const error = ref(null)

    function _setError(err) {
        error.value = err?.response?.data?.detail || err.message || 'something went wrong'
    }

    /**
        teacher
    **/

    // list teacher's own courses (with optional search)
    async function fetchMyCourses(search = '') {
        loading.value = true
        error.value = null
        try {
            const res = await courseService.listMyCourses(search)
            courses.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // get full course details (teacher view)
    async function fetchCourse(courseId) {
        loading.value = true
        error.value = null
        try {
            const res = await courseService.getCourse(courseId)
            currentCourse.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // create course
    async function createCourse(data) {
        loading.value = true
        error.value = null
        // if creation is successful, add the new course to the top of the list and return it
        // so that teacher can immediately see it and click to edit content
        try {
            const res = await courseService.createCourse(data)
            courses.value.unshift(res.data) // add to top of list
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // only title and description can be updated, no content update here
    async function updateCourse(courseId, data) {
        loading.value = true
        error.value = null
        try {
            const res = await courseService.updateCourse(courseId, data)
            // update in list
            const idx = courses.value.findIndex(c => c.id === courseId)
            if (idx !== -1) courses.value[idx] = res.data
            if (currentCourse.value?.id === courseId) currentCourse.value = res.data
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // deleting a course also deletes all its content
    // so just remove it from list and clear current if needed
    async function deleteCourse(courseId) {
        loading.value = true
        error.value = null
        // if current course is the one being deleted, clear it immediately to avoid showing data during loading
        try {
            await courseService.deleteCourse(courseId)
            courses.value = courses.value.filter(c => c.id !== courseId)
            if (currentCourse.value?.id === courseId) currentCourse.value = null
            return true
        } catch (err) {
            _setError(err)
            return false
        } finally {
            loading.value = false
        }
    }


    /**
        student
    **/ 

    // browse all courses (with optional search)
    async function browseCourses(search = '') {
        loading.value = true
        error.value = null
        try {
            const res = await courseService.browseCourses(search)
            courses.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // view course details (student view)
    async function viewCourse(courseId) {
        loading.value = true
        error.value = null
        // if successful, set current course to trigger detail view
        // if error, keep current course unchanged (don't clear) to avoid losing data during loading
        try {
            const res = await courseService.viewCourse(courseId)
            currentCourse.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    function clearCurrent() {
        currentCourse.value = null
    }

    return {
        courses,
        currentCourse,
        loading,
        error,
        fetchMyCourses,
        fetchCourse,
        createCourse,
        updateCourse,
        deleteCourse,
        browseCourses,
        viewCourse,
        clearCurrent,
    }
})