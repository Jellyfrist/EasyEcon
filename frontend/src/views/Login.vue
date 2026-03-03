<template>
    <div class="page-wrapper">
    
        <AuthHeroSection subtitle="Your Economics Space Awaits" />
    
        <div class="form-section">
            <div class="form-container">
                <nav class="auth-nav">
                    <router-link to="/signup" class="nav-item">Sign up</router-link>
                    <div class="nav-item active">Log in</div>
                </nav>
    
                <header class="form-header">
                    <h2>Continue learning</h2>
                    <p>Log in to continue your economics journey.</p>
                </header>
    
                <div class="social-group">
                    <button class="social-btn" @click="loginWithGoogle">
                                <svg width="20" height="20" viewBox="0 0 48 48">
                                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.69 1.22 9.18 3.6l6.85-6.85C35.91 2.27 30.42 0 24 0 14.82 0 6.89 5.48 3.18 13.44l7.98 6.19C13.06 13.11 18.07 9.5 24 9.5z"/>
                                    <path fill="#4285F4" d="M46.14 24.5c0-1.57-.14-3.08-.4-4.55H24v9.1h12.44c-.54 2.9-2.2 5.36-4.7 7.02l7.2 5.6c4.2-3.87 6.6-9.57 6.6-17.17z"/>
                                    <path fill="#FBBC05" d="M10.16 28.63c-.5-1.48-.8-3.06-.8-4.63s.3-3.15.8-4.63l-7.98-6.19C.77 16.24 0 20.02 0 24s.77 7.76 2.18 10.82l7.98-6.19z"/>
                                    <path fill="#34A853" d="M24 48c6.42 0 11.91-2.12 15.88-5.75l-7.2-5.6c-2 1.35-4.56 2.15-8.68 2.15-5.93 0-10.94-3.61-12.84-8.87l-7.98 6.19C6.89 42.52 14.82 48 24 48z"/>
                                </svg>
                                <span>Continue with Google</span>
                            </button>
                    <button class="social-btn" @click="loginWithGithub">
                                <svg width="20" height="20" viewBox="0 0 24 24"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" fill="currentColor"></path></svg>
                                <span>Continue with GitHub</span>
                            </button>
                </div>
    
                <div class="divider">
                    <span>or email</span>
                </div>
    
                <form @submit.prevent="login">
                    <div class="form-group">
                        <label>Email / Username</label>
                        <input v-model="email" type="text" placeholder="Enter your email or username" required />
                    </div>
    
                    <div class="form-group">
                        <div class="label-row">
                            <label>Password</label>
                            <a href="#" class="forgot-link">Forgot password?</a>
                        </div>
                        <div class="password-wrapper">
                            <input v-model="password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" required />
                            <button type="button" @click="showPassword = !showPassword" class="toggle-btn">
                                        <span class="material-symbols-outlined">
                                            {{ showPassword ? 'visibility_off' : 'visibility' }}
                                        </span>
                                    </button>
                        </div>
                    </div>
    
                    <button type="submit" class="btn-login" :disabled="isLoading">
                                {{ isLoading ? 'Logging in...' : 'Log in' }}
                            </button>
                </form>
    
                <p class="footer-text">
                    New to the site?
                    <router-link to="/signup">Create an account</router-link>
                </p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authService } from '../services/authService';
import { useAuthStore } from '../store/authStore';
import AuthHeroSection from '@/components/AuthHeroSection.vue'

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const showPassword = ref(false);
const isLoading = ref(false);

const login = async () => {
    isLoading.value = true;
    try {
        const result = await authStore.login(email.value, password.value);

        // Redirect based on the role
        if (result.success) {
            if (authStore.isAdmin) {
                router.push('/admin');
            } else {
                router.push('/dashboard');
            }
        }
    } catch (error) {
        console.error("Login failed:", error);
        const errorMessage = error.response?.data?.detail || error.message || "Invalid login credentials";
        alert("ERROR: " + errorMessage);
        password.value = ''; 
    } finally {
        isLoading.value = false;
    }
};

const loginWithGoogle = () => authService.loginWithSocial('google');
const loginWithGithub = () => authService.loginWithSocial('github');
</script>

<style scoped>
/* Layout */

.page-wrapper {
    display: flex;
    min-height: 100vh;
}

/* --- Form Section --- */

.form-section {
    flex: 1;
    background: white;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px;
}

.form-container {
    width: 100%;
    max-width: 420px;
}

/* Auth Nav (Tabs) */

.auth-nav {
    display: flex;
    background: #f1f3f7;
    padding: 4px;
    border-radius: 12px;
    margin-bottom: 30px;
}

.nav-item {
    flex: 1;
    text-align: center;
    padding: 10px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    text-decoration: none;
    color: #6b7280;
}

.nav-item.active {
    background: white;
    color: var(--forest-green);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.form-header h2 {
    color: #111827;
    font-size: 24px;
    margin-bottom: 5px;
}

.form-header p {
    color: #6b7280;
    font-size: 14px;
    margin-bottom: 25px;
}

/* Social Buttons */

.social-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 25px;
}

.social-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 12px;
    border: 1px solid #e5e7eb;
    background: white;
    border-radius: 12px;
    font-weight: 600;
    font-size: 15px;
    cursor: pointer;
    transition: background 0.2s;
}

.social-btn:hover {
    background: #f9fafb;
}

/* Divider */

.divider {
    display: flex;
    align-items: center;
    margin: 25px 0;
    color: #9ca3af;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.divider::before,
.divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #e5e7eb;
}

.divider span {
    padding: 0 15px;
}

/* Form Elements */

.form-group {
    margin-bottom: 18px;
}

.form-group label {
    display: block;
    margin-bottom: 6px;
    font-weight: 600;
    font-size: 14px;
    color: #374151;
}

.label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.forgot-link {
    font-size: 12px;
    color: var(--forest-green);
    text-decoration: none;
}

.forgot-link:hover {
    text-decoration: underline;
}

input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: #f9fafb;
    font-size: 16px;
    box-sizing: border-box;
}

input:focus {
    outline: none;
    border-color: var(--forest-green);
    background: white;
    box-shadow: 0 0 0 4px rgba(10, 112, 60, 0.1);
}

.password-wrapper {
    position: relative;
}

.toggle-btn {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #9ca3af;
    cursor: pointer;
}

.btn-login {
    width: 100%;
    padding: 14px;
    background-color: var(--forest-green);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-login:hover {
    filter: brightness(1.2);
    box-shadow: 0 4px 12px rgba(10, 112, 60, 0.2);
}

.btn-login:active {
    transform: scale(0.98);
}

.footer-text {
    text-align: center;
    margin-top: 24px;
    color: var(--gray-text);
    font-size: 14px;
}

.footer-text a {
    color: var(--forest-green);
    text-decoration: none;
    font-weight: 600;
}

.footer-text a:hover {
    text-decoration: underline;
}

/* Mobile */

@media (max-width: 768px) {
    .hero-section {
        display: none;
    }
}
</style>