import { defineStore } from "pinia";
import {
    getUser,
    isAuthenticated,
    saveToken,
    removeToken,
    login,
    register,
    logout,
    getProfile,
    handleSSOCallback,
} from "@/services/authService";

/**
 * Authentication Store
 * Manages global authentication state.
 * 
 * JWT lives in HTTP-only cookie (backend controls it).
 * csrf_token + user profile live in localStorage (we control them).
 */
export const useAuthStore = defineStore("auth", {
    state: () => ({
        user: getUser(),      // loaded from localStorage on app start
        isLoading: false,
        error: null,
    }),

    getters: {
        // auth status
        isAuthenticated: (state) => {
            return isAuthenticated() && !!state.user;
        },

        // role checks (match backend require_* dependencies)
        userRole: (state) => state.user?.role || null,

        isStudent: (state) => state.user?.role === "student",

        // matches backend require_teacher: role "teacher" OR "admin"
        isTeacher: (state) => ["teacher", "admin"].includes(state.user?.role),

        isAdmin: (state) => state.user?.role === "admin",

        // user info
        fullName: (state) =>
            state.user?.full_name ||
            state.user?.username ||
            "Guest",

        email: (state) => state.user?.email || null,
        username: (state) => state.user?.username || null,
    },

    actions: {
        // internal helpers

        _setUser(user) {
            this.user = user;
        },

        setError(error) {
            this.error = error;
        },

        clearError() {
            this.error = null;
        },

        // login

        /**
         * Login with username/email + password.
         * Backend sets JWT cookie, we store csrf_token + user in localStorage.
         */
        async login(usernameOrEmail, password) {
            this.isLoading = true;
            this.clearError();

            try {
                const data = await login(usernameOrEmail, password);
                // data = { csrf_token, user: { id, username, email, role, full_name } }
                this._setUser(data.user);
                return { success: true, data };
            } catch (error) {
                this.setError(error.message);
                return { success: false, error };
            } finally {
                this.isLoading = false;
            }
        },

        // register

        /**
         * Register a new student account.
         * Does not auto-login: redirect to login page after.
         */
        async register(username, email, password, fullName = null) {
            this.isLoading = true;
            this.clearError();

            try {
                const data = await register(username, email, password, fullName);
                return { success: true, data };
            } catch (error) {
                this.setError(error.message);
                return { success: false, error };
            } finally {
                this.isLoading = false;
            }
        },

        // SSO callback

        /**
         * Called by LoginSuccess.vue after Google/GitHub redirect.
         * Reads csrf_token from URL, fetches profile, saves everything.
         */
        async handleSSOCallback() {
            this.isLoading = true;
            this.clearError();

            try {
                const user = await handleSSOCallback();
                this._setUser(user);
                return { success: true, user };
            } catch (error) {
                this.setError(error.message);
                return { success: false, error };
            } finally {
                this.isLoading = false;
            }
        },

        // logout

        /**
         * Logout: clears backend cookie + localStorage.
         */
        async logout(redirectToLogin = true) {
            this.isLoading = true;

            try {
                await logout(false); // service handles removeToken()
            } catch (error) {
                console.error("Logout error:", error);
            } finally {
                this._setUser(null);
                this.clearError();
                this.isLoading = false;

                if (redirectToLogin) {
                    window.location.href = "/login";
                }
            }
        },

        // profile

        /**
         * Refresh user profile from backend.
         * Useful on app start to verify the cookie is still valid.
         */
        async refreshUser() {
            if (!isAuthenticated()) return false;

            this.isLoading = true;

            try {
                const profile = await getProfile();
                if (profile) {
                    // merge in case backend returns extra fields
                    this._setUser({ ...this.user, ...profile });
                    localStorage.setItem("user", JSON.stringify(this.user));
                }
                return true;
            } catch (error) {
                this.setError(error.message);
                if (error.statusCode === 401) {
                    await this.logout();
                }
                return false;
            } finally {
                this.isLoading = false;
            }
        },

        /**
         * Initialize auth on app start.
         * Loads user from localStorage. If cookie is expired,
         * the first API call will get 401 and auto-logout via interceptor.
         */
        initializeAuth() {
            this.user = getUser();
        },
    },
});