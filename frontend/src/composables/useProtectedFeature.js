import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authStore';

export function useProtectedFeature() {
    const authStore = useAuthStore();
    const router = useRouter();

    const isAuthenticated = computed(() => authStore.isAuthenticated);

    const navigateToProtected = (path, featureName) => {
        if (!isAuthenticated.value) {
            // if not authenticated, redirect to login with message
            router.push({
                path: '/login',
                query: { redirect: path, msg: `Please login to access ${featureName}` }
            });
        } else {
            router.push(path);
        }
    };

    return {
        isAuthenticated,
        navigateToProtected
    };
}