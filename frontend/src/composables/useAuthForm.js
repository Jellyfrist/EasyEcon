import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authService } from '@/services/authService';

export function useAuthForm() {
    const router = useRouter();
    const isLoading = ref(false);
    const errorMessage = ref('');

    // clear error message
    const clearError = () => {
        errorMessage.value = '';
    };

    // redirect to Google or GitHub SSO
    const handleSocialLogin = (provider) => {
        authService.loginWithSocial(provider);
    };

    // login with username/email + password
    // on success: backend sets JWT cookie, we store csrf_token + user
    const handleLogin = async (usernameOrEmail, password) => {
        isLoading.value = true;
        errorMessage.value = '';
        try {
            await authService.login(usernameOrEmail, password);
            router.push('/dashboard');
            return { success: true };
        } catch (error) {
            // AuthError already has the message extracted from backend
            errorMessage.value = error.message || 'Invalid username or password.';
            return { success: false, error };
        } finally {
            isLoading.value = false;
        }
    };

    // register a new student account
    // backend always assigns role "student"
    // on success: redirect to login (register does not set a cookie)
    const handleSignUp = async (userData) => {
        isLoading.value = true;
        errorMessage.value = '';
        try {
            await authService.register(
                userData.username,
                userData.email,
                userData.password,
                userData.full_name || userData.username,
            );
            router.push('/login');
            return { success: true };
        } catch (error) {
            errorMessage.value = error.message || 'Something went wrong. Please try again.';
            return { success: false, error };
        } finally {
            isLoading.value = false;
        }
    };

    return {
        isLoading,
        errorMessage,
        clearError,
        handleSocialLogin,
        handleLogin,
        handleSignUp,
    };
}