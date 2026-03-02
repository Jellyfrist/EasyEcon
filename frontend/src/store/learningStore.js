// manages modules, learning pages, and mini quiz attempts

import { defineStore } from 'pinia'
import { ref } from 'vue'
import learningService from '../services/learningService'

export const useLearningStore = defineStore('learning', () => {

    // list of modules for current course
    const modules = ref([])

    // list of pages for current module (summary only)
    const pages = ref([])

    // currently opened page (full content)
    const currentPage = ref(null)

    // student's mini quiz result for current page
    const quizResult = ref(null)

    const loading = ref(false)
    const error = ref(null)

    function _setError(err) {
        error.value = err?.response?.data?.detail || err.message || 'something went wrong'
    }

    /**
     * teacher: modules
     * - create, update, delete modules
     * - create, update, delete pages inside modules
     */

    // create a module for a course
    async function createModule(data) {
        loading.value = true
        error.value = null
        // add the new module to the list if creation is successful
        try {
            const res = await learningService.createModule(data)
            modules.value.push(res.data)
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // update module title or order
    async function updateModule(moduleId, data) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.updateModule(moduleId, data)
            const idx = modules.value.findIndex(m => m.id === moduleId)
            if (idx !== -1) modules.value[idx] = res.data
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // delete a module and all its pages
    async function deleteModule(moduleId) {
        loading.value = true
        error.value = null
        try {
            await learningService.deleteModule(moduleId)
            modules.value = modules.value.filter(m => m.id !== moduleId)
            return true
        } catch (err) {
            _setError(err)
            return false
        } finally {
            loading.value = false
        }
    }

    /**
     * teacher: learning pages
     * - create, update, delete pages inside modules
     */

    // create a learning page inside a module
    async function createPage(data) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.createPage(data)
            pages.value.push(res.data)
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // get full page including topic_tag (teacher editor view)
    async function fetchPage(pageId) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.getPage(pageId)
            currentPage.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // update page content, title, or publish status
    async function updatePage(pageId, data) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.updatePage(pageId, data)
            currentPage.value = res.data
            // update in pages list if present
            const idx = pages.value.findIndex(p => p.id === pageId)
            if (idx !== -1) pages.value[idx] = res.data
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // delete a page
    async function deletePage(pageId) {
        loading.value = true
        error.value = null
        try {
            await learningService.deletePage(pageId)
            pages.value = pages.value.filter(p => p.id !== pageId)
            if (currentPage.value?.id === pageId) currentPage.value = null
            return true
        } catch (err) {
            _setError(err)
            return false
        } finally {
            loading.value = false
        }
    }

    /**
     *  student:
     * - fetch modules and pages for a course
     * - study a page (fetch full content)
     * - submit mini quiz answers and fetch quiz result
     */

    // fetch all modules for a course (student view)
    async function fetchModules(courseId) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.listModules(courseId)
            modules.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // fetch published pages in a module (summary only, no content blocks)
    async function fetchPages(moduleId) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.listPages(moduleId)
            pages.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // get a page for studying (correct answers stripped from mini quiz)
    async function studyPage(pageId) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.studyPage(pageId)
            currentPage.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // submit mini quiz answers for a page, return quiz result
    async function submitMiniQuiz(learningPageId, answers) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.submitMiniQuiz({
                learning_page_id: learningPageId,
                answers,
            })
            quizResult.value = res.data
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // get student's best or latest mini quiz result for a page
    async function fetchMyQuizResult(pageId) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.getMyQuizResult(pageId)
            quizResult.value = res.data
        } catch (err) {
            // 404 means no attempt yet, not a real error
            if (err?.response?.status !== 404) _setError(err)
            quizResult.value = null
        } finally {
            loading.value = false
        }
    }

    // clear currently opened page and quiz result (e.g. when navigating away from study view)
    function clearCurrent() {
        currentPage.value = null
        quizResult.value = null
    }

    // clear all learning data (e.g. when switching courses)
    function clearAll() {
        modules.value = []
        pages.value = []
        currentPage.value = null
        quizResult.value = null
    }

    return {
        modules,
        pages,
        currentPage,
        quizResult,
        loading,
        error,
        createModule,
        updateModule,
        deleteModule,
        createPage,
        fetchPage,
        updatePage,
        deletePage,
        fetchModules,
        fetchPages,
        studyPage,
        submitMiniQuiz,
        fetchMyQuizResult,
        clearCurrent,
        clearAll,
    }
})