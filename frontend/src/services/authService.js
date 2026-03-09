/**
 * Authentication Service
 *
 * Cookie strategy (matches backend):
 *   - "jwt" cookie: HTTP-only, set by backend, browser sends automatically
 *   - csrf_token: returned in JSON body on login, stored in localStorage
 *     Frontend must send it as X-CSRF-Token header on POST/PUT/PATCH/DELETE
 *
 * SSO flow:
 *   - Backend redirects to /login-success?csrf_token=xxx
 *   - LoginSuccess.vue reads csrf_token from URL, stores in localStorage
 *
 * NOTE: All axios config (baseURL, withCredentials, interceptors) lives in
 * api.js. This file just uses that instance — no raw axios here.
 */

import api from "./api";
import { jwtDecode } from "jwt-decode";

// All paths are relative to api.js baseURL (e.g. /api)
const AUTH_URL = `/auth`;

// Custom error class

export class AuthError extends Error {
    constructor(message, statusCode, response) {
        super(message);
        this.name = "AuthError";
        this.statusCode = statusCode;
        this.response = response;
    }
}

// Token / user helpers

/**
 * Store csrf_token and user profile after login.
 * JWT cookie is set by the backend — we never touch it here.
 */
export function saveToken(csrfToken, userData) {
    if (csrfToken) localStorage.setItem("csrf_token", csrfToken);
    if (userData) localStorage.setItem("user_profile", JSON.stringify(userData));
}

export function getUser() {
    const raw = localStorage.getItem("user_profile");
    if (!raw) return null;
    try { return JSON.parse(raw); }
    catch { return null; }
}

/**
 * Check if user is authenticated.
 * We check csrf_token in localStorage as a proxy —
 * the actual JWT is in the HTTP-only cookie.
 */
export function isAuthenticated() {
    return !!localStorage.getItem("csrf_token") && !!getUser();
}

/**
 * Clear all auth data from localStorage.
 * The backend clears the JWT cookie via POST /auth/logout.
 */
export function removeToken() {
    localStorage.removeItem("csrf_token");
    localStorage.removeItem("user_profile");
}

// Auth API methods

/**
 * Login with username/email + password.
 * Backend sets JWT cookie and returns { csrf_token, user }.
 */
export async function login(usernameOrEmail, password) {
    try {
        const params = new URLSearchParams();
        params.append("username", usernameOrEmail);
        params.append("password", password);

        const response = await api.post(`${AUTH_URL}/token`, params, {
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });

        const { csrf_token, user } = response.data;
        saveToken(csrf_token, user);
        return response.data;
    } catch (error) {
        throw new AuthError(
            error.response?.data?.detail || "Login failed",
            error.response?.status || 500,
            error.response?.data
        );
    }
}

/**
 * Register a new student account.
 * Does NOT log in automatically — redirect to login after.
 */
export async function register(username, email, password, fullName = null) {
    try {
        const response = await api.post(`${AUTH_URL}/register`, {
            username,
            email,
            password,
            full_name: fullName,
        });
        return response.data;
    } catch (error) {
        throw new AuthError(
            error.response?.data?.detail || "Registration failed",
            error.response?.status || 500,
            error.response?.data
        );
    }
}

export async function verifyEmail(token) {
    try {
        const response = await api.post(`${AUTH_URL}/verify-email`, { token });
        return response.data;
    } catch (error) {
        throw new AuthError(
            error.response?.data?.detail || "Email verification failed",
            error.response?.status || 500,
            error.response?.data
        );
    }
}

/**
 * Logout: clears backend cookie + local storage.
 */
export async function logout(redirectToLogin = true) {
    try {
        await api.post(`${AUTH_URL}/logout`);
    } catch (e) {
        console.warn("Logout API call failed, clearing local state anyway");
    } finally {
        removeToken();
        if (redirectToLogin) {
            window.location.href = "/login";
        }
    }
}

/**
 * Get current user profile from backend.
 * Backend reads JWT from cookie.
 */
export async function getProfile() {
    try {
        const response = await api.get(`${AUTH_URL}/me`);
        return response.data;
    } catch (error) {
        console.error("Get profile error:", error);
        return null;
    }
}

export const refreshUser = getProfile;

/**
 * SSO login: redirect browser to backend OAuth route.
 * Backend handles OAuth, sets cookie, redirects to /login-success?csrf_token=xxx
 */
export function loginWithGoogle() {
    // Must be a full URL for browser redirect — derive from current origin
    const base = import.meta.env.VITE_BACKEND_URL || `${window.location.origin}/api`;
    window.location.href = `${base}/auth/login/google`;
}

export function loginWithGithub() {
    const base = import.meta.env.VITE_BACKEND_URL || `${window.location.origin}/api`;
    window.location.href = `${base}/auth/login/github`;
}

export function loginWithSocial(provider) {
    if (provider === "google") return loginWithGoogle();
    if (provider === "github") return loginWithGithub();
    console.error(`Unknown provider: ${provider}`);
}

/**
 * Called by LoginSuccess.vue after SSO redirect.
 * Reads csrf_token from URL, fetches user profile, saves both.
 */
export async function handleSSOCallback() {
    const params = new URLSearchParams(window.location.search);
    const csrfToken = params.get("csrf_token");

    if (!csrfToken) {
        throw new AuthError("Missing csrf_token in SSO callback", 400);
    }

    localStorage.setItem("csrf_token", csrfToken);

    const user = await getProfile();
    if (!user) {
        removeToken();
        throw new AuthError("Failed to fetch user profile after SSO login", 401);
    }

    saveToken(csrfToken, user);
    return user;
}

// Unified export

export const authService = {
    login,
    register,
    verifyEmail,
    logout,
    getProfile,
    refreshUser,
    loginWithGoogle,
    loginWithGithub,
    loginWithSocial,
    handleSSOCallback,
    getUser,
    isAuthenticated,
    saveToken,
    removeToken,
};

export default authService;