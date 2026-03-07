// store/learningStore.js
// manages modules, learning pages, mini quiz attempts, and student progress

import { defineStore } from 'pinia'
import { ref } from 'vue'
import learningService from '../services/learningService'

export const useLearningStore = defineStore('learning', () => {

    // --- [State] ---
    const modules = ref([])
    const pages = ref([])
    const currentPage = ref(null)
    const quizResult = ref(null)
    const loading = ref(false)
    const error = ref(null)

    // State สำหรับ Dashboard และ Progress Tracking ของนักเรียน
    const chapterInfo = ref({
        title: '',
        description: '',
        progressPercent: 0,
        completedCount: 0,
        totalCount: 0,
        totalTime: '0 นาที'
    })
    const dashboardLessons = ref([]) // เก็บรายการบทเรียนพร้อมสถานะ (completed, active, locked)

    // --- [Helper] ---
    function _setError(err) {
        error.value = err?.response?.data?.detail || err.message || 'something went wrong'
    }

    /**
     * ==========================================
     * 👨‍🏫 TEACHER ACTIONS
     * ==========================================
     */

    // สร้าง Module ใหม่
    async function createModule(data) {
        loading.value = true
        error.value = null
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

    // อัปเดตข้อมูล Module
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

    // ลบ Module
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

    // สร้างหน้าบทเรียน (Page)
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

    // ดึงข้อมูลหน้าบทเรียนสำหรับ Editor (Teacher)
    async function fetchPage(pageId) {
        loading.value = true
        error.value = null
        try {
            // 🚨 แก้ไขจาก getPage เป็น getPage (ตามที่เราแก้ใน Service)
            const res = await learningService.getPage(pageId)
            currentPage.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // อัปเดตเนื้อหาหน้าบทเรียน
    async function updatePage(pageId, data) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.updatePage(pageId, data)
            currentPage.value = res.data
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

    // ลบหน้าบทเรียน
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
     * ==========================================
     * 🎓 STUDENT ACTIONS (Study & Dashboard)
     * ==========================================
     */

    // ดึงรายการ Module ทั้งหมดของคอร์ส
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

    // ดึงรายการหน้าบทเรียนย่อยใน Module
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

    // ดึงข้อมูลภาพรวมความคืบหน้า (Dashboard)
    async function fetchModuleDashboard(moduleId) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.getModuleDashboard(moduleId)
            chapterInfo.value = res.data.chapterInfo
            dashboardLessons.value = res.data.lessons
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // ดึงเนื้อหาหน้าบทเรียนสำหรับนักเรียน (Study Mode)
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

    // บันทึกว่าเรียนจบหน้านี้แล้ว และอัปเดต UI ทันที
    async function completePage(pageId) {
        try {
            await learningService.completePage(pageId)
            
            // อัปเดตสถานะในหน้า Dashboard โดยไม่ต้องรีโหลดหน้า
            const lessonIndex = dashboardLessons.value.findIndex(l => l.id === parseInt(pageId))
            if (lessonIndex !== -1 && dashboardLessons.value[lessonIndex].status !== 'completed') {
                dashboardLessons.value[lessonIndex].status = 'completed'
                chapterInfo.value.completedCount += 1
                
                // คำนวณเปอร์เซ็นต์ใหม่
                if (chapterInfo.value.totalCount > 0) {
                    chapterInfo.value.progressPercent = Math.round((chapterInfo.value.completedCount / chapterInfo.value.totalCount) * 100)
                }

                // ปลดล็อกบทถัดไป (ถ้ามี)
                if (lessonIndex + 1 < dashboardLessons.value.length) {
                    if (dashboardLessons.value[lessonIndex + 1].status === 'locked') {
                        dashboardLessons.value[lessonIndex + 1].status = 'active'
                    }
                }
            }
        } catch (err) {
            console.error("Failed to mark page as completed", err)
        }
    }

    // ส่งคำตอบ Mini Quiz
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

    // ดึงคะแนน Quiz ล่าสุดของนักเรียน
    async function fetchMyQuizResult(pageId) {
        loading.value = true
        error.value = null
        try {
            const res = await learningService.getMyQuizResult(pageId)
            quizResult.value = res.data
        } catch (err) {
            if (err?.response?.status !== 404) _setError(err)
            quizResult.value = null
        } finally {
            loading.value = false
        }
    }

    /**
     * ==========================================
     * 🧹 CLEAN UP & UTILS
     * ==========================================
     */

    function clearCurrent() {
        currentPage.value = null
        quizResult.value = null
    }

    function clearAll() {
        modules.value = []
        pages.value = []
        currentPage.value = null
        quizResult.value = null
        chapterInfo.value = { 
            title: '', 
            description: '', 
            progressPercent: 0, 
            completedCount: 0, 
            totalCount: 0, 
            totalTime: '0 นาที' 
        }
        dashboardLessons.value = []
        error.value = null
    }

    return {
        // States
        modules,
        pages,
        currentPage,
        quizResult,
        chapterInfo,
        dashboardLessons,
        loading,
        error,
        
        // Actions
        createModule,
        updateModule,
        deleteModule,
        createPage,
        fetchPage,
        updatePage,
        deletePage,
        fetchModules,
        fetchPages,
        fetchModuleDashboard,
        completePage,
        studyPage,
        submitMiniQuiz,
        fetchMyQuizResult,
        clearCurrent,
        clearAll,
    }
})