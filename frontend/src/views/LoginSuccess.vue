<template>
  <div class="login-loading">
    <p>Loading...</p>
    </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/authStore'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
    const result = await authStore.handleSSOCallback()

    // debug
    console.log("SSO Result:", result);
    console.log("Current User in Store:", authStore.user);
    console.log(result)
    if (result.success) {
        // Check the role stored in the authStore after a successful callback
        const user = authStore.user;

        if (authStore.isAdmin) {
            router.push('/admin');
        } else if (authStore.isTeacher) {
            router.push('/teacher');
        } else {
            router.push('/dashboard');
        }
    } else {
        router.push('/login');
    }
})
</script>