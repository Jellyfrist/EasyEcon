// self-service profile calls: any logged-in user

import api from './api'

const userService = {

    // get own profile (shape differs by role)
    getProfile() {
        return api.get('/users/me')
    },

    // student only: update username
    updateUsername(username) {
        return api.patch('/users/me', { username })
    },

    // student only: change password
    changePassword(newPassword) {
        return api.patch('/users/me/password', { new_password: newPassword })
    },
}

export default userService