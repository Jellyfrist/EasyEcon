/*
    base axios instance used by all services
    - sends cookies automatically (withCredentials)
    - reads csrf_token from localStorage and adds X-CSRF-Token header
    - all services import this instead of raw axios
*/

import axios from 'axios'

// Use env var if set, otherwise fall back to a relative path so every
// deployment (preview or production) calls its OWN backend automatically.
const rawUrl = import.meta.env.VITE_BACKEND_URL || '/api'
const baseURL = rawUrl.replace(/\/auth$/, '')

const api = axios.create({
    baseURL,
    withCredentials: true, // send jwt cookie on every request
})

// attach csrf token to every mutating request
api.interceptors.request.use((config) => {
    const csrf = localStorage.getItem('csrf_token')
    if (csrf && ['post', 'put', 'patch', 'delete'].includes(config.method)) {
        config.headers['X-CSRF-Token'] = csrf
    }
    return config
})

// handle 401 globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('csrf_token')
            localStorage.removeItem('user_profile')
            if (window.location.pathname !== '/login') {
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default api