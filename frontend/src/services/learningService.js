// services/learningService.js
import api from './api'

const learningService = {

    /* ==========================================
       👨‍🏫 TEACHER ENDPOINTS
       ========================================== */

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
    // แก้ไขชื่อให้เป็นมาตรฐาน เพื่อให้ Store เรียกใช้งานได้ง่าย
    getPage(pageId) {
        return api.get(`/learning/pages/${pageId}`)
    },
    updatePage(pageId, payload) {
        return api.patch(`/learning/pages/${pageId}`, payload)
    },
    deletePage(pageId) {
        return api.delete(`/learning/pages/${pageId}`)
    },


    /* ==========================================
       🎓 STUDENT ENDPOINTS
       ========================================== */

    // ดึงรายการ Modules ทั้งหมดใน Course
    listModules(courseId) {
        return api.get('/learning/modules', { params: { course_id: courseId } })
    },

    // ดึงรายการ Pages ทั้งหมดใน Module (เฉพาะที่ Published)
    listPages(moduleId) {
        return api.get(`/learning/modules/${moduleId}/pages`)
    },

    // ดึงข้อมูลภาพรวมความคืบหน้า (Progress) ของนักเรียนในโมดูลนั้นๆ
    getModuleDashboard(moduleId) {
        return api.get(`/learning/modules/${moduleId}/dashboard`)
    },

    // ดึงเนื้อหาหน้าบทเรียนสำหรับนักเรียน (ตัดเฉลย Quiz ออก)
    studyPage(pageId) {
        return api.get(`/learning/pages/${pageId}/study`)
    },

    // บันทึกว่านักเรียนเรียนหน้านี้จบแล้ว
    completePage(pageId) {
        return api.post(`/learning/pages/${pageId}/complete`)
    },

    // ส่งคำตอบ Mini Quiz
    submitMiniQuiz(data) {
        return api.post('/learning/pages/mini-quiz', data)
    },

    // ดูผลคะแนน Quiz ล่าสุดของนักเรียนในหน้านั้นๆ
    getMyQuizResult(pageId) {
        return api.get(`/learning/pages/${pageId}/my-quiz`)
    }
}

export default learningService