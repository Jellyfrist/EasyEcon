import api from './api'

const learningService = {

    // Modules
    createModule(data) {
        return api.post('/learning/modules', data)
    },
    updateModule(moduleId, data) {
        return api.patch(`/learning/modules/${moduleId}`, data)
    },
    deleteModule(moduleId) {
        return api.delete(`/learning/modules/${moduleId}`)
    },

    // Learning Pages
    createPage(payload) {
        return api.post('/learning/pages', payload)
    },
    getPage(pageId) {
        return api.get(`/learning/pages/${pageId}`)
    },
    updatePage(pageId, payload) {
        return api.patch(`/learning/pages/${pageId}`, payload)
    },
    deletePage(pageId) {
        return api.delete(`/learning/pages/${pageId}`)
    },

    listModules(courseId) {
        return api.get('/learning/modules', { params: { course_id: courseId } })
    },

    listLessonOptions(courseId) {
        return api.get(`/learning/courses/${courseId}/lesson-options`)
    },

    listPages(moduleId) {
        return api.get(`/learning/modules/${moduleId}/pages`)
    },

    getModuleDashboard(moduleId) {
        return api.get(`/learning/modules/${moduleId}/dashboard`)
    },

    studyPage(pageId) {
        return api.get(`/learning/pages/${pageId}/study`)
    },

    completePage(pageId) {
        return api.post(`/learning/pages/${pageId}/complete`)
    },

    submitMiniQuiz(data) {
        return api.post('/learning/pages/mini-quiz', data)
    },

    getMyQuizResult(pageId) {
        return api.get(`/learning/pages/${pageId}/my-quiz`)
    }
}

export default learningService
