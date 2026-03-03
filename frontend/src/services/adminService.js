// admin-only API calls: user management + teacher invite

import api from './api'

const adminService = {

    // list all users, optionally filtered by role
    listUsers(role = null) {
        return api.get('/admin/users', { params: role ? { role } : {} })
    },

    // change a user's role
    changeRole(userId, role) {
        return api.patch(`/admin/users/${userId}/role`, null, { params: { role } })
    },

    // deactivate a user account (soft delete)
    deactivateUser(userId) {
        return api.patch(`/admin/users/${userId}/deactivate`)
    },

    // invite a teacher: system auto-generates username + password + sends email
    inviteTeacher(data) {
        // data: { full_name, email }
        return api.post('/admin/teachers/invite', data)
    },

    // resend credentials: resets password + sends new email to teacher
    sendCredentials(userId) {
        return api.post(`/admin/teachers/${userId}/send-credentials`)
    },
}

export default adminService