// manages user list, role changes, deactivation, and teacher invites

import { defineStore } from 'pinia'
import { ref } from 'vue'
import adminService from '../services/adminService'

export const useAdminStore = defineStore('admin', () => {

    const users = ref([])
    const loading = ref(false)
    const error = ref(null)
    const successMessage = ref(null)

    function _setError(err) {
        error.value = err?.response?.data?.detail || err.message || 'something went wrong'
        successMessage.value = null
    }

    function _setSuccess(msg) {
        successMessage.value = msg
        error.value = null
    }

    function clearMessages() {
        error.value = null
        successMessage.value = null
    }

    // load all users, optionally filter by role
    async function fetchUsers(role = null) {
        loading.value = true
        error.value = null
        try {
            const res = await adminService.listUsers(role)
            users.value = res.data
        } catch (err) {
            _setError(err)
        } finally {
            loading.value = false
        }
    }

    // change a user's role and update locally
    async function changeRole(userId, role) {
        loading.value = true
        error.value = null
        try {
            const res = await adminService.changeRole(userId, role)
            const idx = users.value.findIndex(u => u.id === userId)
            if (idx !== -1) users.value[idx] = res.data
            _setSuccess(`role updated to ${role}`)
            return true
        } catch (err) {
            _setError(err)
            return false
        } finally {
            loading.value = false
        }
    }

    // deactivate a user and update locally
    async function deactivateUser(userId) {
        loading.value = true
        error.value = null
        try {
            const res = await adminService.deactivateUser(userId)
            const idx = users.value.findIndex(u => u.id === userId)
            if (idx !== -1) users.value[idx] = res.data
            _setSuccess('account deactivated')
            return true
        } catch (err) {
            _setError(err)
            return false
        } finally {
            loading.value = false
        }
    }

    // invite a teacher (full_name + email only)
    async function inviteTeacher(data) {
        loading.value = true
        error.value = null
        try {
            const res = await adminService.inviteTeacher(data)
            // add to list if currently showing all or teachers
            users.value.push(res.data)
            _setSuccess(`invitation sent to ${data.email}`)
            return res.data
        } catch (err) {
            _setError(err)
            return null
        } finally {
            loading.value = false
        }
    }

    // resend credentials email (resets password)
    async function sendCredentials(userId) {
        loading.value = true
        error.value = null
        try {
            await adminService.sendCredentials(userId)
            _setSuccess('credentials email sent')
            return true
        } catch (err) {
            _setError(err)
            return false
        } finally {
            loading.value = false
        }
    }

    return {
        users,
        loading,
        error,
        successMessage,
        clearMessages,
        fetchUsers,
        changeRole,
        deactivateUser,
        inviteTeacher,
        sendCredentials,
    }
})