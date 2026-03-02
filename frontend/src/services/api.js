/*
    base axios instance used by all services
    - sends cookies automatically (withCredentials)
    - reads csrf_token from localStorage and adds X-CSRF-Token header
    - all services import this instead of raw axios
*/

import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.BACKEND_URL || 'http://localhost:56733',
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

export default api