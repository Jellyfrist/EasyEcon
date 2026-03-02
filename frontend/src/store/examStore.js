// manages exam templates, sessions, and student attempts

import { defineStore } from 'pinia'
import { ref } from 'vue'
import examService from '../services/examService'

export const useExamStore = defineStore('exam', () => {

    // teacher: list of templates for current course
    const templates = ref([])

    // teacher: currently opened full template
    const currentTemplate = ref(null)

    // teacher: all student results for a session
    const sessionResults = ref([])

    // student: list of open sessions for current course
    const openSessions = ref([])

    // student: currently opened session with questions
    const currentSession = ref(null)

    // student: result of latest submitted attempt
    const currentAttempt = ref(null)

    // student: all attempts for a session
    const myAttempts = ref([])

    const loading = ref(false)
    const error = ref(null)

    function _setError(err) {
        error.value = err?.response?.data?.detail || err.message || 'something went wrong'
    }

    /**
     * teacher: templates
     */

    async function fetchTemplates(courseId, filters = {}) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.listTemplates(courseId, filters)
            templates.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    async function fetchTemplate(templateId) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.getTemplate(templateId)
            currentTemplate.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    async function createTemplate(data) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.createTemplate(data)
            templates.value.unshift(res.data)
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    async function updateTemplate(templateId, data) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.updateTemplate(templateId, data)
            const idx = templates.value.findIndex(t => t.id === templateId)
            if (idx !== -1) templates.value[idx] = res.data
            if (currentTemplate.value?.id === templateId) currentTemplate.value = res.data
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    async function deleteTemplate(templateId) {
        loading.value = true
        error.value = null
        try {
            await examService.deleteTemplate(templateId)
            templates.value = templates.value.filter(t => t.id !== templateId)
            if (currentTemplate.value?.id === templateId) currentTemplate.value = null
            return true
        } catch (err) {
            _setError(err)
            return false
        } finally {
            loading.value = false
        }
    }

    /**
     * teacher: sessions 
     */

    async function launchSession(data) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.launchSession(data)
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    async function fetchSessionResults(sessionId) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.getSessionResults(sessionId)
            sessionResults.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    /**
     * student
     */

    async function fetchOpenSessions(courseId) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.listOpenSessions(courseId)
            openSessions.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    async function openSession(sessionId) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.openSession(sessionId)
            currentSession.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    async function submitAttempt(sessionId, answers) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.submitAttempt({
                session_id: sessionId,
                answers,
            })
            currentAttempt.value = res.data
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    async function fetchAttempt(attemptId) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.getAttempt(attemptId)
            currentAttempt.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    async function fetchMyAttempts(sessionId) {
        loading.value = true
        error.value = null
        try {
            const res = await examService.getMyAttempts(sessionId)
            myAttempts.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    function clearCurrent() {
        currentTemplate.value = null
        currentSession.value = null
        currentAttempt.value = null
        sessionResults.value = []
        myAttempts.value = []
    }

    return {
        templates,
        currentTemplate,
        sessionResults,
        openSessions,
        currentSession,
        currentAttempt,
        myAttempts,
        loading,
        error,
        fetchTemplates,
        fetchTemplate,
        createTemplate,
        updateTemplate,
        deleteTemplate,
        launchSession,
        fetchSessionResults,
        fetchOpenSessions,
        openSession,
        submitAttempt,
        fetchAttempt,
        fetchMyAttempts,
        clearCurrent,
    }
})