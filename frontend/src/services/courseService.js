// covers all /courses endpoints for teacher and student

import api from './api'

const courseService = {

    /* 
        teacher-only endpoints:
        - POST   /courses                create a new course
        - GET    /courses                list teacher's own courses (with optional search)
        - GET    /courses/{course_id}    get full course details (teacher view)
        - PATCH  /courses/{course_id}    update course title or description
        - DELETE /courses/{course_id}    delete course and all its content
    */

    // create a new course
    createCourse(data) {
        return api.post('/courses', data)
    },

    // list teacher's own courses (with optional search)
    listMyCourses(search = '') {
        return api.get('/courses', { params: search ? { search } : {} })
    },

    // get full course details (teacher view)
    getCourse(courseId) {
        return api.get(`/courses/${courseId}`)
    },

    // update course title or description
    updateCourse(courseId, data) {
        return api.patch(`/courses/${courseId}`, data)
    },

    // delete course and all its content
    deleteCourse(courseId) {
        return api.delete(`/courses/${courseId}`)
    },


    /*
        student endpoints:
        - GET /courses/browse/all         browse all courses (with optional search)
        - GET /courses/{course_id}/view   view course details (student view)
    */

    // browse all courses (with optional search)
    browseCourses(search = '') {
        return api.get('/courses/browse/all', { params: search ? { search } : {} })
    },

    // view course details (student view)
    viewCourse(courseId) {
        return api.get(`/courses/${courseId}/view`)
    },
}

export default courseService