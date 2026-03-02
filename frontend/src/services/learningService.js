// covers all /learning endpoints for teacher and student

import api from './api'

const learningService = {

    /*
        teacher-only endpoints:
        - POST   /learning/modules              create a module inside a course
        - PATCH  /learning/modules/{module_id}  update module title or order
        - DELETE /learning/modules/{module_id}  delete module and all its pages
    */

    // create a module inside a course
    createModule(data) {
        // data: { course_id, title, order_index }
        return api.post('/learning/modules', data)
    },

    // update module title or order
    updateModule(moduleId, data) {
        return api.patch(`/learning/modules/${moduleId}`, data)
    },

    // delete module and all its pages
    deleteModule(moduleId) {
        return api.delete(`/learning/modules/${moduleId}`)
    },


    /*
        teacher-only endpoints for learning pages:
        - POST   /learning/pages               create a learning page inside a module
        - GET    /learning/pages/{page_id}     get full page including topic_tag (teacher editor view)
        - PATCH  /learning/pages/{page_id}     update page content, title, or publish status
        - DELETE /learning/pages/{page_id}     delete a page
    */

    // create a learning page inside a module
    createPage(data) {
        // data: { module_id, title, content_blocks, template_type, topic_tag, ... }
        return api.post('/learning/pages', data)
    },

    // get full page including topic_tag (teacher editor view)
    getPage(pageId) {
        return api.get(`/learning/pages/${pageId}`)
    },

    // update page content, title, or publish status
    updatePage(pageId, data) {
        return api.patch(`/learning/pages/${pageId}`, data)
    },

    // delete a page
    deletePage(pageId) {
        return api.delete(`/learning/pages/${pageId}`)
    },


    /*
        student endpoints:
        - GET /learning/modules?course_id={course_id}       list all modules for a course
        - GET /learning/modules/{module_id}/pages           list published pages in a module (summary only, no content blocks)
        - GET /learning/pages/{page_id}/study               get a page for studying (correct answers stripped from mini quiz)
        - POST /learning/pages/mini-quiz                    submit mini quiz answers for a page
        - GET  /learning/pages/{page_id}/my-quiz            get student's best or latest mini quiz result for a page
    */

    // list all modules for a course
    listModules(courseId) {
        return api.get('/learning/modules', { params: { course_id: courseId } })
    },

    // list published pages in a module (summary only, no content blocks)
    listPages(moduleId) {
        return api.get(`/learning/modules/${moduleId}/pages`)
    },

    // get a page for studying (correct answers stripped from mini quiz)
    studyPage(pageId) {
        return api.get(`/learning/pages/${pageId}/study`)
    },

    // submit mini quiz answers for a page
    submitMiniQuiz(data) {
        // data: { learning_page_id, answers: { q1: "A", q2: "..." } }
        return api.post('/learning/pages/mini-quiz', data)
    },

    // get student's best or latest mini quiz result for a page
    getMyQuizResult(pageId) {
        return api.get(`/learning/pages/${pageId}/my-quiz`)
    },
}

export default learningService