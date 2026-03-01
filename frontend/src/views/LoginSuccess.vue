<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/authStore'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
    const result = await authStore.handleSSOCallback()
    if (result.success) {
        router.push('/dashboard')
    } else {
        router.push('/login')
    }
})
</script>