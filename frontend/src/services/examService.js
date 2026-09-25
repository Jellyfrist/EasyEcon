// covers all /exam endpoints for teacher and student

import api from './api'

const examService = {
    uploadQuestionImage(file) {
        const form = new FormData()
        form.append('file', file)
        return api.post('/flashcards/upload-image', form)
    },

    /* 
        teacher: exam templates
        - POST   /exam/templates                 create an exam template (question bank)
        - GET    /exam/templates                 list templates for a course (past-year browser)
        - GET    /exam/templates/{template_id}   get full template with all questions
        - PATCH  /exam/templates/{template_id}   update template metadata or questions
        - DELETE /exam/templates/{template_id}   delete template
    */

    // create an exam template (question bank)
    createTemplate(data) {
        // data: { course_id, title, exam_type, academic_year, term, question_data, ... }
        return api.post('/exam/templates', data)
    },

    // list templates for a course (past-year browser)
    listTemplates(courseId, filters = {}) {
        // filters: { exam_type, academic_year }
        return api.get('/exam/templates', {
            params: { course_id: courseId, ...filters },
        })
    },

    // get full template with all questions
    getTemplate(templateId) {
        return api.get(`/exam/templates/${templateId}`)
    },

    // update template metadata or questions
    updateTemplate(templateId, data) {
        return api.patch(`/exam/templates/${templateId}`, data)
    },

    // delete template
    deleteTemplate(templateId) {
        return api.delete(`/exam/templates/${templateId}`)
    },

    
    /*
        teacher: exam sessions
        - POST   /exam/sessions/{session_id}            launch a session from a template
        - GET    /exam/sessions/{session_id}/results    view all student results for a session
    */

    // launch a session from a template
    launchSession(data) {
        // data: { template_id, title, instructions, available_from, available_until, ... }
        return api.post('/exam/sessions', data)
    },

    // view all student results for a session
    getSessionResults(sessionId) {
        return api.get(`/exam/sessions/${sessionId}/results`)
    },

    
    /*
        student:
        - GET    /exam/sessions?course_id={courseId}        list open exam sessions for a course
        - GET    /exam/sessions/{session_id}/open           open a session to see questions (answers stripped)
        - POST   /exam/attempts                             submit exam answers (graded immediately)
        - GET    /exam/attempts/{attempt_id}                get a specific attempt result
        - GET    /exam/sessions/{session_id}/my-attempts    list all of student's attempts for a session
        - GET    /exam/attempts/{attempt_id}/wrong-topics   wrong topics + lessons to review
    */

    // list open exam sessions for a course
    listOpenSessions(courseId) {
        return api.get('/exam/sessions', { params: { course_id: courseId } })
    },

    // open a session to see questions (answers stripped)
    openSession(sessionId) {
        return api.get(`/exam/sessions/${sessionId}/open`)
    },

    // submit exam answers (graded immediately)
    submitAttempt(data) {
        // data: { session_id, answers: { q1: "A", q2: "B", ... } }
        return api.post('/exam/attempts', data)
    },

    // get a specific attempt result
    getAttempt(attemptId) {
        return api.get(`/exam/attempts/${attemptId}`)
    },

    // list all of student's attempts for a session
    getMyAttempts(sessionId) {
        return api.get(`/exam/sessions/${sessionId}/my-attempts`)
    },

    // topics the student answered wrong + the lessons that cover them
    // each row: { topic_tag, wrong_count, total_questions, score_pct, is_weak,
    //             message, question_ids, lessons: [{ page_id, title, study_url, ... }],
    //             redirect_url }
    getWrongTopics(attemptId, { weakOnly = false } = {}) {
        return api.get(`/exam/attempts/${attemptId}/wrong-topics`, {
            params: weakOnly ? { weak_only: true } : {},
        })
    },
}

export default examService
